from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .model import SecureEventEnvelope


@dataclass(frozen=True)
class OutboxRecord:
    event: SecureEventEnvelope
    state: str
    attempts: int
    next_attempt_at: str
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
        self._create_schema()

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

            CREATE INDEX IF NOT EXISTS idx_outbox_ready
              ON event_outbox(state, next_attempt_at, created_at);
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
    def _dump_event(event: SecureEventEnvelope) -> str:
        return json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _load_event(raw: str) -> SecureEventEnvelope:
        return SecureEventEnvelope.from_dict(json.loads(raw))

    def enqueue_outbox(self, event: SecureEventEnvelope, now: str) -> bool:
        """Insert once. A duplicate contract/topic pair is a replay, not a new send."""
        with self.transaction() as tx:
            cursor = tx.execute(
                """
                INSERT OR IGNORE INTO event_outbox(
                    event_id, contract_id, topic, event_json, state, attempts,
                    next_attempt_at, created_at, updated_at, last_error
                ) VALUES (?, ?, ?, ?, 'PENDING', 0, ?, ?, ?, NULL)
                """,
                (event.event_id, event.contract_id, event.topic, self._dump_event(event), now, now, now),
            )
            return cursor.rowcount == 1

    def claim_ready(self, now: str, limit: int = 100) -> list[OutboxRecord]:
        if limit <= 0:
            return []
        with self.transaction() as tx:
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
                tx.execute(
                    """
                    UPDATE event_outbox
                    SET state='INFLIGHT', attempts=?, updated_at=?
                    WHERE event_id=? AND state IN ('PENDING','RETRY')
                    """,
                    (attempts, now, row["event_id"]),
                )
                claimed.append(
                    OutboxRecord(
                        event=self._load_event(row["event_json"]),
                        state="INFLIGHT",
                        attempts=attempts,
                        next_attempt_at=row["next_attempt_at"],
                        last_error=row["last_error"],
                    )
                )
            return claimed

    def mark_delivered(self, event_id: str, now: str) -> None:
        with self.transaction() as tx:
            row = tx.execute("SELECT attempts FROM event_outbox WHERE event_id=?", (event_id,)).fetchone()
            if row is None:
                raise KeyError(event_id)
            tx.execute(
                "UPDATE event_outbox SET state='DELIVERED', updated_at=?, last_error=NULL WHERE event_id=?",
                (now, event_id),
            )
            tx.execute(
                "INSERT INTO delivery_attempts(event_id, attempt_no, outcome, error, attempted_at) VALUES (?, ?, 'DELIVERED', NULL, ?)",
                (event_id, int(row["attempts"]), now),
            )

    def fail_attempt(
        self,
        event_id: str,
        error: str,
        now: str,
        retry_at: str,
        max_attempts: int,
    ) -> str:
        with self.transaction() as tx:
            row = tx.execute("SELECT * FROM event_outbox WHERE event_id=?", (event_id,)).fetchone()
            if row is None:
                raise KeyError(event_id)
            attempts = int(row["attempts"])
            tx.execute(
                "INSERT INTO delivery_attempts(event_id, attempt_no, outcome, error, attempted_at) VALUES (?, ?, 'FAILED', ?, ?)",
                (event_id, attempts, error, now),
            )
            if attempts >= max_attempts:
                tx.execute(
                    "UPDATE event_outbox SET state='DEAD', updated_at=?, last_error=? WHERE event_id=?",
                    (now, error, event_id),
                )
                tx.execute(
                    """
                    INSERT OR REPLACE INTO dead_letter(
                        event_id, contract_id, topic, attempts, reason, event_json, failed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["event_id"], row["contract_id"], row["topic"], attempts,
                        error, row["event_json"], now,
                    ),
                )
                return "DEAD"
            tx.execute(
                """
                UPDATE event_outbox
                SET state='RETRY', next_attempt_at=?, updated_at=?, last_error=?
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
                "SELECT first_event_id FROM replay_ledger WHERE consumer_repo=? AND contract_id=?",
                (consumer_repo, event.contract_id),
            ).fetchone()
            if existing is not None:
                return False
            tx.execute(
                """
                INSERT INTO replay_ledger(consumer_repo, contract_id, first_event_id, first_seen_at)
                VALUES (?, ?, ?, ?)
                """,
                (consumer_repo, event.contract_id, event.event_id, now),
            )
            tx.execute(
                """
                INSERT INTO event_inbox(
                    consumer_repo, contract_id, event_id, contract_payload_hash,
                    status, first_seen_at, updated_at
                ) VALUES (?, ?, ?, ?, 'RECEIVED', ?, ?)
                """,
                (
                    consumer_repo, event.contract_id, event.event_id,
                    event.contract_payload_hash, now, now,
                ),
            )
            return True

    def mark_inbox_processed(self, consumer_repo: str, contract_id: str, now: str) -> None:
        with self.transaction() as tx:
            cursor = tx.execute(
                """
                UPDATE event_inbox SET status='PROCESSED', updated_at=?
                WHERE consumer_repo=? AND contract_id=?
                """,
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
