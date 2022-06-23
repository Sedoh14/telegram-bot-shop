from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import admins
from loader import dp


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(
        f"Я не знаю этого слова, вы можете воспользоваться словами: <i>контакты</i> и <i>товары</i> или кнопками внизу.")


@dp.message_handler(state='*', content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state = await state.get_state()
    if message.from_user.id == admins:
        await message.answer(f"Эхо в состоянии <code>{state}</code>.\n"
                             f"\nСодержание сообщения:\n"
                             f"<code>{message}</code>")
    else:
        await message.answer(
            f"Я не знаю этого слова, вы можете воспользоваться словами: <i>контакты</i> и <i>товары</i>"
            f" или кнопками внизу."
            f"Сообщение:\n"
            f"{message.text}")
