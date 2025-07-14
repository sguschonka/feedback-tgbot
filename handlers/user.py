from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_ID as admins
from database.database import session
from database.models import FeedbackORM

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Отправь мне свое сообщение.\n Наши администраторы увидят его и ответят как смогут."
    )


@router.message(F.text & ~F.command)
async def feedback_handler(message: Message):
    async with session() as s:
        feedback = FeedbackORM(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            message=message.text,
        )
        s.add(feedback)
        await s.commit()

        await s.refresh(feedback)

        feedback_data = {
            "id": feedback.id,
            "user_id": feedback.user_id,
            "username": feedback.username,
            "first_name": feedback.first_name,
            "message": feedback.message,
        }

        for admin_id in admins:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"Новое сообщение от {feedback_data['first_name']} (@{feedback_data['username']}, ID: {feedback_data['user_id']}):\n\n{feedback_data['message']}\n\nID сообщения: {feedback_data['id']}",
            )

        await message.answer(
            "Ваше сообщение уже было получено! Ожидайте ответа."
        )
