import aiosqlite
import logging

DB_PATH = "database.db" # Path to SQLite database file

async def init_db(): 
    try:
        # Initialize the database and create tables if they don't exist
        async with aiosqlite.connect(DB_PATH) as db:
            # Saved messages table
            await db.execute("""
            CREATE TABLE IF NOT EXISTS saved_messages (
                id INTEGER PRIMARY KEY,
                message TEXT NOT NULL
                )
            """)
            logging.info("Saved messages table initialized successfully.")

            # Warnings Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logging.info("Warnings table initialized successfully.")

            # Welcome channels table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS welcome_channels (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER NOT NULL
                )
            """)
            logging.info("Welcome channels table initialized successfully.")

            # Club info table (Key-Value store for flexible metadata)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS club_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            logging.info("Club info table initialized successfully.")

            # Track full member list
            await db.execute("""
                CREATE TABLE IF NOT EXISTS guild_members (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    joined_at TIMESTAMP,
                    is_bot BOOLEAN NOT NULL,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            logging.info("Guild members table initialized successfully.")

            # Track active server message counts/stats
            await db.execute("""
                CREATE TABLE IF NOT EXISTS member_activity (
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            logging.info("Member activity table initialized successfully.")

            await db.commit()
            logging.info("SQLite database tables initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing SQLite database: {e}")

# ====================
# SAVED MESSAGES
# ====================
async def get_saved_message(user_id: int):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT message FROM saved_messages WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None  
    except Exception as e:
        logging.error(f"Error retrieving saved message for user {user_id}: {e}")

async def save_user_message(user_id: int, message: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO saved_messages (user_id, message)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET message = excluded.message
        """, (user_id, message))
        await db.commit()

# =============================
# WARNINGS
# =============================
async def add_warning(guild_id: int, user_id: int, reason: str, moderator_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO warnings (guild_id, user_id, reason, moderator_id)
            VALUES (?, ?, ?, ?)
        """, (guild_id, user_id, reason, moderator_id))
        await db.commit()

async def get_warnings(guild_id: int, user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id, reason, moderator_id, timestamp 
            FROM warnings 
            WHERE guild_id = ? AND user_id = ?
        """, (guild_id, user_id)) as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "reason": r[1], "moderator_id": r[2], "timestamp": r[3]} for r in rows]

# =============================
# WELCOME CHANNELS
# =============================
async def get_welcome_channel(guild_id: int) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channel_id FROM welcome_channels WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def save_welcome_channel(guild_id: int, channel_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO welcome_channels (guild_id, channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id
        """, (guild_id, channel_id))
        await db.commit()

# =============================
# CLUB INFO
# =============================
async def set_club_info(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO club_info (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, str(value)))
        await db.commit()

async def get_club_info(key: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM club_info WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

# ======================================
# Member Syncing AND Activity Tracking
# ======================================

async def upsert_member(guild_id: int, user_id: int, username: str, display_name: str, joined_at: str, is_bot: bool):
    # Insert/update member profile information when they join or update
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO guild_members (guild_id, user_id, username, display_name, joined_at, is_bot)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET 
                username = excluded.username,
                display_name = excluded.display_name,
                joined_at = excluded.joined_at,
                is_bot = excluded.is_bot
        """, (guild_id, user_id, username, display_name, str(joined_at), int(is_bot)))
        await db.commit()

async def remove_member(guild_id: int, user_id: int):
    """Deletes member record when they leave the server."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM guild_members WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        await db.commit()

async def increment_message_count(guild_id: int, user_id: int):
    """Tracks message activity whenever a member speaks."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO member_activity (guild_id, user_id, message_count, last_active)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                message_count = message_count + 1,
                last_active = CURRENT_TIMESTAMP
        """, (guild_id, user_id))
        await db.commit()