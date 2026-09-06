from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from .model import SecureEventEnvelope


@dataclass(frozen=True)
class OutboxRecord:
    event: SecureEventEnvelope
    state: str
    attempts: int
    next_attempt_at: str
    lease_until: str | None
    last_error: str | None


class DurableEventStore:
    """SQLite reference implementation of the fabric durability contract.

    Semantics are intentionally at-least-once delivery + idempotent consumption.
    We do not claim impossible end-to-end exactly-once delivery across independent
    transactional systems.
    """

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self._create_schema()
        self._migrate_schema()
        self._create_indexes()

    def close(self) -> None:
        self.conn.close()

    def _create_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS event_outbox (
                event_id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                event_json TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('PENDING','INFLIGHT','RETRY','DELIVERED','DEAD')),
                attempts INTEGER NOT NULL DEFAULT 0 CHECK(attempts >= 0),
                next_attempt_at TEXT NOT NULL,
                lease_until TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_error TEXT,
                UNIQUE(contract_id, topic)
            );

            CREATE TABLE IF NOT EXISTS event_inbox (
                consumer_repo TEXT NOT NULL,
                contract_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                contract_payload_hash TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('RECEIVED','PROCESSED','REJECTED')),
                first_seen_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY(consumer_repo, contract_id)
            );

            CREATE TABLE IF NOT EXISTS replay_ledger (
                consumer_repo TEXT NOT NULL,
                contract_id TEXT NOT NULL,
                first_event_id TEXT NOT NULL,
                first_payload_hash TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                PRIMARY KEY(consumer_repo, contract_id)
            );

            CREATE TABLE IF NOT EXISTS delivery_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                attempt_no INTEGER NOT NULL,
                outcome TEXT NOT NULL,
                error TEXT,
                attempted_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS quarantine (
                event_id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                reason TEXT NOT NULL,
                event_json TEXT NOT NULL,
                quarantined_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dead_letter (
                event_id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                reason TEXT NOT NULL,
                event_json TEXT NOT NULL,
                failed_at TEXT NOT NULL
            );
            """
        )

    def _migrate_schema(self) -> None:
        """Small forward migrations for DBs created by early Secure Event Fabric builds."""
        outbox_columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(event_outbox)").fetchall()}
        if "lease_until" not in outbox_columns:
            self.conn.execute("ALTER TABLE event_outbox ADD COLUMN lease_until TEXT")

        replay_columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(replay_ledger)").fetchall()}
        if "first_payload_hash" not in replay_columns:
            self.conn.execute("ALTER TABLE replay_ledger ADD COLUMN first_payload_hash TEXT")
            self.conn.execute(
                """
                UPDATE replay_ledger
                SET first_payload_hash=(
                    SELECT contract_payload_hash FROM event_inbox i
                    WHERE i.consumer_repo=replay_ledger.consumer_repo
                      AND i.contract_id=replay_ledger.contract_id
                )
                WHERE first_payload_hash IS NULL
                """
            )

    def _create_indexes(self) -> None:
        """Create indexes only after migrations have installed every referenced column."""
        self.conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_outbox_ready
              ON event_outbox(state, next_attempt_at, created_at);
            CREATE INDEX IF NOT EXISTS idx_outbox_lease
              ON event_outbox(state, lease_until);
            CREATE INDEX IF NOT EXISTS idx_attempts_event
              ON delivery_attempts(event_id, attempt_no);
            """
        )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")

    @staticmethod
    def _parse_time(value: str) -> datetime:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    @staticmethod
    def _format_time(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _dump_event(event: SecureEventEnvelope) -> str:
        return json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _load_event(raw: str) -> SecureEventEnvelope:
        return SecureEventEnvelope.from_dict(json.loads(raw))

    def enqueue_outbox(self, event: SecureEventEnvelope, now: str) -> bool:
        """Insert once; conflicting reuse of contract_id is rejected, not deduplicated."""
        with self.transaction() as tx:
            existing = tx.execute(
                "SELECT topic, event_json FROM event_outbox WHERE contract_id=? LIMIT 1",
                (event.contract_id,),
            ).fetchone()
            if existing is not None:
                first = self._load_event(existing["event_json"])
                if first.contract_payload_hash != event.contract_payload_hash:
                    raise ValueError("outbox contract_id replay has conflicting payload hash")
                if first.topic != event.topic:
                    raise ValueError("outbox contract_id replay targets a conflicting topic")
                return False

            cursor = tx.execute(
                """
                INSERT INTO event_outbox(
                    event_id, contract_id, topic, event_json, state, attempts,
                    next_attempt_at, lease_until, created_at, updated_at, last_error
                ) VALUES (?, ?, ?, ?, 'PENDING', 0, ?, NULL, ?, ?, NULL)
                """,
                (event.event_id, event.contract_id, event.topic, self._dump_event(event), now, now, now),
            )
            return cursor.rowcount == 1

    def recover_stale_inflight(self, now: str) -> int:
        """Return abandoned leased deliveries to RETRY after a worker crash."""
        with self.transaction() as tx:
            cursor = tx.execute(
                """
                UPDATE event_outbox
                SET state='RETRY', lease_until=NULL, updated_at=?,
                    last_error=COALESCE(last_error, 'delivery lease expired before ack')
                WHERE state='INFLIGHT' AND lease_until IS NOT NULL AND lease_until <= ?
                """,
                (now, now),
            )
            return cursor.rowcount

    def claim_ready(self, now: str, limit: int = 100, lease_seconds: int = 30) -> list[OutboxRecord]:
        if limit <= 0:
            return []
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        lease_until = self._format_time(self._parse_time(now) + timedelta(seconds=lease_seconds))
        with self.transaction() as tx:
            tx.execute(
                """
                UPDATE event_outbox
                SET state='RETRY', lease_until=NULL, updated_at=?,
                    last_error=COALESCE(last_error, 'delivery lease expired before ack')
                WHERE state='INFLIGHT' AND lease_until IS NOT NULL AND lease_until <= ?
                """,
                (now, now),
            )
            rows = tx.execute(
                """
                SELECT * FROM event_outbox
                WHERE state IN ('PENDING','RETRY') AND next_attempt_at <= ?
                ORDER BY created_at, event_id
                LIMIT ?
                """,
                (now, limit),
            ).fetchall()
            claimed: list[OutboxRecord] = []
            for row in rows:
                attempts = int(row["attempts"]) + 1
                cursor = tx.execute(
                    """
                    UPDATE event_outbox
                    SET state='INFLIGHT', attempts=?, lease_until=?, updated_at=?
                    WHERE event_id=? AND state IN ('PENDING','RETRY')
                    """,
                    (attempts, lease_until, now, row["event_id"]),
                )
                if cursor.rowcount != 1:
                    continue
                claimed.append(
                    OutboxRecord(
                        event=self._load_event(row["event_json"]),
                        state="INFLIGHT",
                        attempts=attempts,
                        next_attempt_at=row["next_attempt_at"],
                        lease_until=lease_until,
                        last_error=row["last_error"],
                    )
                )
            return claimed

    def mark_delivered(self, event_id: str, now: str) -> None:
        with self.transaction() as tx:
            row = tx.execute("SELECT attempts, state FROM event_outbox WHERE event_id=?", (event_id,)).fetchone()
            if row is None:
                raise KeyError(event_id)
            if row["state"] != "INFLIGHT":
                raise ValueError("only INFLIGHT event can be acknowledged as delivered")
            tx.execute(
                "UPDATE event_outbox SET state='DELIVERED', lease_until=NULL, updated_at=?, last_error=NULL WHERE event_id=?",
                (now, event_id),
            )
            tx.execute(
                "INSERT INTO delivery_attempts(event_id, attempt_no, outcome, error, attempted_at) VALUES (?, ?, 'DELIVERED', NULL, ?)",
                (event_id, int(row["attempts"]), now),
            )

    def fail_attempt(self, event_id: str, error: str, now: str, retry_at: str, max_attempts: int) -> str:
        with self.transaction() as tx:
            row = tx.execute("SELECT * FROM event_outbox WHERE event_id=?", (event_id,)).fetchone()
            if row is None:
                raise KeyError(event_id)
            if row["state"] != "INFLIGHT":
                raise ValueError("only INFLIGHT event can fail a delivery attempt")
            attempts = int(row["attempts"])
            tx.execute(
                "INSERT INTO delivery_attempts(event_id, attempt_no, outcome, error, attempted_at) VALUES (?, ?, 'FAILED', ?, ?)",
                (event_id, attempts, error, now),
            )
            if attempts >= max_attempts:
                tx.execute(
                    "UPDATE event_outbox SET state='DEAD', lease_until=NULL, updated_at=?, last_error=? WHERE event_id=?",
                    (now, error, event_id),
                )
                tx.execute(
                    """
                    INSERT OR REPLACE INTO dead_letter(
                        event_id, contract_id, topic, attempts, reason, event_json, failed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (row["event_id"], row["contract_id"], row["topic"], attempts, error, row["event_json"], now),
                )
                return "DEAD"
            tx.execute(
                """
                UPDATE event_outbox
                SET state='RETRY', lease_until=NULL, next_attempt_at=?, updated_at=?, last_error=?
                WHERE event_id=?
                """,
                (retry_at, now, error, event_id),
            )
            return "RETRY"

    def receive_once(self, event: SecureEventEnvelope, consumer_repo: str, now: str) -> bool:
        if event.consumer_repo != consumer_repo:
            raise ValueError("event delivered to wrong consumer repo")
        with self.transaction() as tx:
            existing = tx.execute(
                "SELECT first_event_id, first_payload_hash FROM replay_ledger WHERE consumer_repo=? AND contract_id=?",
                (consumer_repo, event.contract_id),
            ).fetchone()
            if existing is not None:
                known_hash = existing["first_payload_hash"]
                if not known_hash:
                    inbox = tx.execute(
                        "SELECT contract_payload_hash FROM event_inbox WHERE consumer_repo=? AND contract_id=?",
                        (consumer_repo, event.contract_id),
                    ).fetchone()
                    known_hash = None if inbox is None else inbox["contract_payload_hash"]
                if known_hash and known_hash != event.contract_payload_hash:
                    raise ValueError("replayed contract_id has conflicting payload hash")
                return False
            tx.execute(
                """
                INSERT INTO replay_ledger(
                    consumer_repo, contract_id, first_event_id, first_payload_hash, first_seen_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (consumer_repo, event.contract_id, event.event_id, event.contract_payload_hash, now),
            )
            tx.execute(
                """
                INSERT INTO event_inbox(
                    consumer_repo, contract_id, event_id, contract_payload_hash,
                    status, first_seen_at, updated_at
                ) VALUES (?, ?, ?, ?, 'RECEIVED', ?, ?)
                """,
                (consumer_repo, event.contract_id, event.event_id, event.contract_payload_hash, now, now),
            )
            return True

    def mark_inbox_processed(self, consumer_repo: str, contract_id: str, now: str) -> None:
        with self.transaction() as tx:
            cursor = tx.execute(
                "UPDATE event_inbox SET status='PROCESSED', updated_at=? WHERE consumer_repo=? AND contract_id=?",
                (now, consumer_repo, contract_id),
            )
            if cursor.rowcount != 1:
                raise KeyError((consumer_repo, contract_id))

    def quarantine_event(self, event: SecureEventEnvelope, reason: str, now: str) -> None:
        with self.transaction() as tx:
            tx.execute(
                """
                INSERT OR REPLACE INTO quarantine(event_id, contract_id, reason, event_json, quarantined_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (event.event_id, event.contract_id, reason, self._dump_event(event), now),
            )

    def outbox_state(self, event_id: str) -> str | None:
        row = self.conn.execute("SELECT state FROM event_outbox WHERE event_id=?", (event_id,)).fetchone()
        return None if row is None else str(row["state"])

    def inbox_status(self, consumer_repo: str, contract_id: str) -> str | None:
        row = self.conn.execute(
            "SELECT status FROM event_inbox WHERE consumer_repo=? AND contract_id=?",
            (consumer_repo, contract_id),
        ).fetchone()
        return None if row is None else str(row["status"])

    def count(self, table: str) -> int:
        allowed = {"event_outbox", "event_inbox", "replay_ledger", "delivery_attempts", "quarantine", "dead_letter"}
        if table not in allowed:
            raise ValueError("unsupported table")
        return int(self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
