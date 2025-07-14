import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = list(map(int, os.getenv("ADMIN_ID", "").split(",")))
DATABASE_URL = os.getenv("DATABASE_URL")
