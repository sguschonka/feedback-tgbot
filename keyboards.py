from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_main_kb():
    buttons = [
        [
            InlineKeyboardButton(
                text="Неотвеченные сообщения", callback_data="unanswered"
            )
        ],
        [
            InlineKeyboardButton(
                text="Все сообщения", callback_data="all_messages"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def feedback_kb(feedback_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="Ответить", callback_data=f"reply_{feedback_id}"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def feedback_pagination_kb(feedback_id: int, total: int, current_pos: int):
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️", callback_data=f"prev_{feedback_id}_{current_pos}"
            ),
            InlineKeyboardButton(
                text=f"{current_pos}/{total}", callback_data="position"
            ),
            InlineKeyboardButton(
                text="➡️", callback_data=f"next_{feedback_id}_{current_pos}"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Ответить", callback_data=f"reply_{feedback_id}"
            )
        ],
        [InlineKeyboardButton(text="Назад", callback_data="all_messages")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def cancel_reply_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отменить ответ", callback_data="cancel_reply"
                )
            ]
        ]
    )
