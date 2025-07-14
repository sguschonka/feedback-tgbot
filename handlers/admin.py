from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from config import ADMIN_ID as admins
from database.database import session
from database.models import FeedbackORM
from keyboards import (
    admin_main_kb,
    cancel_reply_kb,
    feedback_kb,
    feedback_pagination_kb,
)

router = Router()


class ReplyState(StatesGroup):
    waiting_for_reply = State()


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id not in admins:
        return

    await message.answer("Админ-панель:", reply_markup=admin_main_kb())


@router.callback_query(F.data == "unanswered")
async def show_unanswered(callback: CallbackQuery):
    async with session() as s:
        result = await s.execute(
            select(FeedbackORM).where(FeedbackORM.is_answered == False)
        )
        feedbacks = result.scalars().all()

        if not feedbacks:
            await callback.message.edit_text("Нет неотвеченных сообщений!")
            return

        feedback = feedbacks[0]
        text = (
            f"Сообщение #{feedback.id}\n"
            f"От: {feedback.first_name} (@{feedback.username}, ID: {feedback.user_id})\n"
            f"Текст: {feedback.message}\n"
            f"Ответ: {feedback.admin_response or 'Нет ответа'}\n\n"
        )

        await callback.message.edit_text(
            text=text, reply_markup=feedback_kb(feedback.id)
        )


@router.callback_query(F.data.startswith("reply_"))
async def start_reply(callback: CallbackQuery, state: FSMContext):
    feedback_id = int(callback.data.split("_")[1])
    await state.update_data(feedback_id=feedback_id)
    await state.set_state(ReplyState.waiting_for_reply)
    await callback.message.edit_text(
        "Введите ваш ответ:", reply_markup=cancel_reply_kb()
    )


@router.callback_query(F.data == "cancel_reply", ReplyState.waiting_for_reply)
async def cancel_reply(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Ответ отменён. Сообщнени осталось без ответа"
    )


@router.message(ReplyState.waiting_for_reply)
async def process_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    feedback_id = data["feedback_id"]
    admin_response = message.text

    async with session() as s:
        result = await s.execute(
            select(FeedbackORM).where(FeedbackORM.id == feedback_id)
        )
        feedback = result.scalar_one()

        user_id = feedback.user_id

        feedback.admin_response = admin_response
        feedback.is_answered = True
        await s.commit()

    try:
        await message.bot.send_message(
            chat_id=user_id,
            text=f"Администратор ответил на ваше сообщение:\n\n{admin_response}",
        )

        await message.answer("Ответ отправлен пользователю!")
    except Exception as e:
        await message.answer(f"Ошибка при отправке ответа: {e}")

    await state.clear()


@router.callback_query(F.data == "all_messages")
async def show_all_messages(callback: CallbackQuery):
    async with session() as s:
        res = await s.execute(select(FeedbackORM).order_by(FeedbackORM.id))
        feedbacks = res.scalars().all()

        if not feedbacks:
            await callback.message.edit_text("Нет сообщений в базе.")
            return

        feedback = feedbacks[0]
        total = len(feedbacks)

        text = format_feedback_text(feedback, position=1, total=total)
        keyboard = feedback_pagination_kb(feedback.id, total, 1)

        await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("prev_") | F.data.startswith("next_"))
async def navigate_feedback(callback: CallbackQuery):
    action, feedback_id, current_pos = callback.data.split("_")
    current_pos = int(current_pos)
    feedback_id = int(feedback_id)

    async with session() as s:
        result = await s.execute(select(FeedbackORM).order_by(FeedbackORM.id))
        feedbacks = result.scalars().all()
        total = len(feedbacks)

        if action == "prev":
            new_pos = current_pos - 1 if current_pos > 1 else total
        else:
            new_pos = current_pos + 1 if current_pos < total else 1

        feedback = feedbacks[new_pos - 1]
        text = format_feedback_text(feedback, position=new_pos, total=total)
        keyboard = feedback_pagination_kb(feedback.id, total, new_pos)

        await callback.message.edit_text(text, reply_markup=keyboard)


def format_feedback_text(feedback: FeedbackORM, position: int, total: int):
    status = "✅" if feedback.is_answered else "❌"
    return (
        f"{status} Сообщение {position} из {total}\n"
        f"ID: {feedback.id}\n"
        f"От: {feedback.first_name} (@{feedback.username}, ID: {feedback.user_id})\n"
        f"Дата: {feedback.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(feedback, 'created_at') else 'N/A'}\n\n"
        f"Сообщение:\n{feedback.message}\n\n"
        f"Ответ администратора:\n{feedback.admin_response or 'Нет ответа'}"
    )
