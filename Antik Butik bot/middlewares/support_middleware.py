from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Unauthorized

from loader import dp


class SupportMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        state = dp.current_state(chat=message.from_user.id, user=message.from_user.id)
        state_str = str(await state.get_state())
        if state_str == "in_support" and message.text != 'Завершить вызов':
            data = await state.get_data()
            second_id = data.get("second_id")
            try:
                await message.copy_to(second_id)
            except Unauthorized:
                await message.answer('<b>Антикъ-Бутикъ бот:</b>\n'
                                     '"Пользователь удалил чат, заблокировав отправку сообщений. Завершите вызов"')
            raise CancelHandler()
