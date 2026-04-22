import aiosqlite
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path(os.getenv("DB_PATH", "./data/aiktivist.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


async def init_db():
    """Initialize database schema."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        await db.commit()


async def add_message(session_id: str, role: str, content: str) -> dict:
    """Add message to conversation."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        # Get or create conversation
        cursor = await db.execute(
            "SELECT id FROM conversations WHERE session_id = ?",
            (session_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            await db.execute(
                "INSERT INTO conversations (session_id) VALUES (?)",
                (session_id,)
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT id FROM conversations WHERE session_id = ?",
                (session_id,)
            )
            row = await cursor.fetchone()
        
        conv_id = row[0]
        
        # Insert message
        await db.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conv_id, role, content)
        )
        await db.commit()
        
        cursor = await db.execute(
            "SELECT id, created_at FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 1",
            (conv_id,)
        )
        msg = await cursor.fetchone()
        
        return {
            "id": msg[0],
            "role": role,
            "content": content,
            "created_at": msg[1]
        }


async def get_conversation(session_id: str) -> list:
    """Get all messages from a conversation."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute(
            """
            SELECT m.id, m.role, m.content, m.created_at
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.session_id = ?
            ORDER BY m.created_at
            """,
            (session_id,)
        )
        rows = await cursor.fetchall()
        return [
            {"id": r[0], "role": r[1], "content": r[2], "created_at": r[3]}
            for r in rows
        ]
