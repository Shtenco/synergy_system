from __future__ import annotations

import sqlite3

from synergy_event_fabric import DurableEventStore


def test_early_database_without_lease_column_upgrades_before_index_creation(tmp_path):
    path = tmp_path / "old-fabric.db"
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE event_outbox (
            event_id TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            event_json TEXT NOT NULL,
            state TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            next_attempt_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_error TEXT,
            UNIQUE(contract_id, topic)
        );
        CREATE TABLE event_inbox (
            consumer_repo TEXT NOT NULL,
            contract_id TEXT NOT NULL,
            event_id TEXT NOT NULL,
            contract_payload_hash TEXT NOT NULL,
            status TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(consumer_repo, contract_id)
        );
        CREATE TABLE replay_ledger (
            consumer_repo TEXT NOT NULL,
            contract_id TEXT NOT NULL,
            first_event_id TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            PRIMARY KEY(consumer_repo, contract_id)
        );
        """
    )
    conn.commit()
    conn.close()

    store = DurableEventStore(path)
    outbox_columns = {row[1] for row in store.conn.execute("PRAGMA table_info(event_outbox)").fetchall()}
    replay_columns = {row[1] for row in store.conn.execute("PRAGMA table_info(replay_ledger)").fetchall()}
    indexes = {row[1] for row in store.conn.execute("PRAGMA index_list(event_outbox)").fetchall()}

    assert "lease_until" in outbox_columns
    assert "first_payload_hash" in replay_columns
    assert "idx_outbox_lease" in indexes
    store.close()
