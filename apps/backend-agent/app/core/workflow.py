import os
import json
import uuid
from typing import Any, Dict, Optional, Sequence, Iterator, AsyncIterator
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from contextlib import asynccontextmanager
import asyncpg

class PostgresCheckpointer(BaseCheckpointSaver):
    """
    A LangGraph Checkpointer that saves state to the 'agent_runs_runstep' or a dedicated table.
    For simplicity in this phase and strict schema adherence, we will use a dedicated method
    to update the `AgentRun` model directly via SQL, or a separate checkpoints table if needed.
    
    However, LangGraph expects specific binary serialization.
    To be "startup-credible" but practical, we will implement a simplified version 
    that treats `AgentRun` as the session container and uses a separate `checkpoints` table 
    managed here, OR we adapt to `AgentRun`.
    
    DECISION: We will create a `checkpoints` table in Postgres for LangGraph's internal state,
    and link it to `AgentRun` via metadata.
    """
    conn_string: str

    def __init__(self, conn_string: str):
        super().__init__()
        self.conn_string = conn_string

    @classmethod
    @asynccontextmanager
    async def from_conn_string(cls, conn_string: str) -> AsyncIterator["PostgresCheckpointer"]:
        conn = await asyncpg.connect(conn_string)
        try:
            # Ensure table exists
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
                    thread_id TEXT NOT NULL,
                    thread_ts TEXT NOT NULL,
                    parent_ts TEXT,
                    checkpoint BYTEA NOT NULL,
                    metadata BYTEA NOT NULL,
                    PRIMARY KEY (thread_id, thread_ts)
                );
            """)
            yield cls(conn_string)
        finally:
            await conn.close()

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Optional[dict[str, Any]] = None,
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        # thread_ts = checkpoint["id"] # Standard LangGraph
        # LangGraph v0.1+ changes. Let's stick to basic serialization.
        
        # NOTE: LangGraph API shifts frequently. We will implement robust error handling.
        # For Phase 1 demo, we might skip deep persistence if complex, but the prompt requires "Stateful Workflows".
        # We will use a simpler InMemory for the *very* first pass if DB is complex, but we promised PG.
        
        # Let's rely on the DB connection for every op to be safe with async/cloud run.
        conn = await asyncpg.connect(self.conn_string)
        try:
            # Serialization (Mock for structure)
            ckpt_data = json.dumps(checkpoint).encode()
            meta_data = json.dumps(metadata).encode() 
            
            await conn.execute(
                """
                INSERT INTO langgraph_checkpoints (thread_id, thread_ts, parent_ts, checkpoint, metadata)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (thread_id, thread_ts) DO UPDATE 
                SET checkpoint = EXCLUDED.checkpoint, metadata = EXCLUDED.metadata;
                """,
                thread_id,
                checkpoint["id"],
                config["configurable"].get("thread_ts"), # Parent?
                ckpt_data,
                meta_data
            )
        finally:
            await conn.close()
            
        return {
            "configurable": {
                "thread_id": thread_id,
                "thread_ts": checkpoint["id"],
            }
        }

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]
        # Simplified get
        conn = await asyncpg.connect(self.conn_string)
        try:
            row = await conn.fetchrow(
                "SELECT checkpoint, metadata, parent_ts FROM langgraph_checkpoints WHERE thread_id = $1 ORDER BY thread_ts DESC LIMIT 1",
                thread_id
            )
            if row:
                return CheckpointTuple(
                    config,
                    json.loads(row["checkpoint"]),
                    json.loads(row["metadata"]),
                    None, # Parent config
                )
        finally:
            await conn.close()
        return None

    # Sync methods required by ABC but we only use async
    def put(self, config, checkpoint, metadata, new_versions=None): pass
    def get_tuple(self, config): pass
    def list(self, config, *, filter=None, before=None, limit=None): pass
