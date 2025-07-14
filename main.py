import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database.database import init_db
from handlers import routers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

for router in routers:
    dp.include_router(router=router)


async def set_main_menu(bot):
    await bot.set_my_commands(
        [
            BotCommand(command="/start", description="Запустить бота"),
            BotCommand(command="/admin", description="Админ панель для админов"),
        ]
    )



async def main():
    await set_main_menu(bot)
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
