from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from data.config import support_ids
from loader import dp, bot

support_callback = CallbackData("ask_support", "messages", "user_id", "as_user")
cancel_support_callback = CallbackData("cancel_support", "user_id")


async def check_support_available(support_id):
    state = dp.current_state(chat=support_id, user=support_id)
    state_str = str(
        await state.get_state()
    )
    if state_str == "in_support":
        return
    elif state_str != 'None':
        await bot.send_message(chat_id=support_id, text='С вами пытается связаться новый пользователь, '
                                                        'ваши действия будут прерваны.')
        await state.reset_state()
        return support_id
    else:
        return support_id


async def get_support_manager():
    id = list()
    for support_id in support_ids:
        support_id = await check_support_available(support_id)
        if support_id:
            id.append(support_id)
    return id


async def support_keyboard(messages, user_id=None, free_id=None):
    if user_id:
        contact_id = int(user_id)
        as_user = "no"
        text = "Ответить пользователю"
        free_id = await get_support_manager()
    else:
        as_user = "yes"
        text = "Написать оператору"
    if text == 'Написать оператору':
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                text=text,
                callback_data=support_callback.new(
                    messages=messages,
                    user_id=1,
                    as_user=as_user
                )
            )
        )
        if messages == "many":
            keyboard.add(
                InlineKeyboardButton(
                    text="Завершить вызов",
                    callback_data=cancel_support_callback.new(
                        user_id=1
                    )
                )
            )
        return keyboard
    elif free_id:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(
                text=text,
                callback_data=support_callback.new(
                    messages=messages,
                    user_id=user_id,
                    as_user=as_user
                )
            )
        )
        return keyboard


def cancel_support(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить вызов",
                    callback_data=cancel_support_callback.new(
                        user_id=user_id
                    )
                )
            ]
        ]
    )


