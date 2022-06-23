import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, InputMediaPhoto

from data.config import support_ids
from keyboards.default.new_keyboard import all_cancels_keyboard, start_keyboard
from keyboards.inline.inline_support import support_keyboard, support_callback, \
    get_support_manager, \
    cancel_support_callback
from loader import dp, bot
from utils.db_api.db_commands import get_item


@dp.message_handler(
    Text(equals=['Контакты', 'Интересует конкретный товар', 'контакты', 'интересует конкретный товар', 'товар']),
    state=[None])
async def ask_support_call(message: types.Message, state: FSMContext):
    text = "Нажмите на кнопку написать оператору и он ответит на любые вопросы."
    keyboard = await support_keyboard(messages="many")
    global flag
    flag = True
    if message.text == 'Контакты' or message.text == 'контакты':
        text += ' Наш телефон: 8-926-521-69-89'
    await message.answer(text, reply_markup=keyboard)
    await state.set_state('start')


@dp.callback_query_handler(support_callback.filter(messages="many", as_user="yes"),
                           state=['pre_wait_in_support', 'start'])
async def send_to_support_call(call: types.CallbackQuery, state: FSMContext):
    cur_state = dp.current_state(user=call.from_user.id, chat=call.from_user.id)
    if str(await cur_state.get_state()) == 'wait_in_support':
        await call.message.edit_text('Вы следующий на очереди к тех. поддержке!')
        item_id = -1
    elif str(await state.get_state()) == 'pre_wait_in_support':
        item_id = await state.get_data()
        await call.message.edit_reply_markup()
        item_id = item_id.get('item_id')
    else:
        await call.message.edit_reply_markup()
        item_id = -1
    await state.set_state("wait_in_support")
    global contact_ids, another_time, queue, flagochek
    try:
        if call.from_user.id not in queue:
            if item_id != -1:
                queue.append(str(call.from_user.id) + ' ' + str(call.from_user.full_name) + ' ' + str(item_id))
            else:
                queue.append(str(call.from_user.id) + ' ' + str(call.from_user.full_name))
            if (len(queue) - 1) % 10 == 1 and (len(queue) - 1) != 11:
                await bot.send_message(chat_id=call.from_user.id,
                                       text=f'Вы обратились в техподдержку. Перед вами находится {len(queue) - 1}'
                                            f' пользователь',
                                       reply_markup=all_cancels_keyboard)
            elif 1 < (len(queue) - 1) % 10 < 5 and (
                    len(queue) - 1 < 11 or len(queue) - 1 > 19):
                await bot.send_message(chat_id=call.from_user.id,
                                       text=f'Вы обратились в техподдержку. Перед вами находится {len(queue) - 1}'
                                            f' пользователя',
                                       reply_markup=all_cancels_keyboard)
            elif len(queue) - 1 > 0:
                await bot.send_message(chat_id=call.from_user.id,
                                       text=f'Вы обратились в техподдержку. Перед вами находится {len(queue) - 1}'
                                            f' пользователей',
                                       reply_markup=all_cancels_keyboard)
            else:
                await bot.send_message(chat_id=call.from_user.id,
                                       text=f'Тех. поддержка готова вас принять', reply_markup=all_cancels_keyboard)
    except NameError:
        queue = list()
        queue.append(str(call.from_user.id) + ' ' + str(call.from_user.full_name))
        await bot.send_message(chat_id=call.from_user.id,
                               text=f'Тех. поддержка готова вас принять', reply_markup=all_cancels_keyboard)
    try:
        if another_time or not another_time:
            pass
    except NameError:
        another_time = False
    if len(queue) == 1 or another_time:
        flagochek = True
    else:
        flagochek = False
    if flagochek:
        flagochek = False
        contact_ids = await get_support_manager()
        if contact_ids:
            '''queue[0] = str(call.from_user.id) + ' ' + str(len(contact_ids))'''
            for i in range(len(contact_ids)):
                keyboard1 = await support_keyboard(messages='many', user_id=call.from_user.id, free_id=contact_ids[i])
                await bot.send_message(chat_id=contact_ids[i],
                                       text=f"С вами хочет связаться пользователь {call.from_user.full_name}",
                                       reply_markup=keyboard1)


@dp.callback_query_handler(support_callback.filter(messages="many", as_user="no"))
async def answer_support_call(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    global queue, another_time
    second_id = callback_data.get("user_id")
    user_state = dp.current_state(user=second_id, chat=second_id)
    if str(await user_state.get_state()) != "wait_in_support":
        await call.message.edit_text(
            "С пользователем разговаривает другой представитель тех. "
            "поддержки или он ушёл прежде чем подключился к тех. поддержке.")
        return
    await state.set_state("in_support")
    await user_state.set_state("in_support")
    await state.update_data(second_id=second_id)
    await user_state.update_data(second_id=call.from_user.id)
    await call.message.edit_reply_markup()
    await bot.send_message(call.from_user.id, "Вы на связи с пользователем!\n"
                                              "Чтобы завершить общение нажмите на кнопку.",
                           reply_markup=all_cancels_keyboard
                           )
    await bot.send_message(second_id,
                           "Техподдержка на связи! Можете писать сюда свое сообщение. \n"
                           "Чтобы завершить общение нажмите на кнопку.",
                           reply_markup=all_cancels_keyboard
                           )
    if str(queue[0])[-1].isdigit():
        item_id = queue[0].split()[-1]
        item = await get_item(int(item_id))
        media1 = []
        if item.photo:
            for photo_id in item.photo.split(','):
                media1.append(InputMediaPhoto(photo_id))
            media1.pop()
            await call.message.answer_media_group(media1)
            await call.message.answer(f'Пользователь хочет проконсультироваться по товару:\n'
                                      f'Категория: {item.category_name}\n'
                                      f'Подкатегория: {item.subcategory_name}\n'
                                      f'Имя товара: {item.name}\n'
                                      f'Описание товара:{item.inscription}', reply_markup=all_cancels_keyboard)
        else:
            await call.message.answer(f'Пользователь хочет проконсультироваться по товару:\n'
                                      f'Категория: {item.category_name}\n'
                                      f'Подкатегория: {item.subcategory_name}\n'
                                      f'Имя товара: {item.name}\n'
                                      f'Описание товара:{item.inscription}', reply_markup=all_cancels_keyboard)

    del queue[0]
    if queue and len(contact_ids) - 1 > 0:
        another_time = True
        await next_one(queue[0])
    else:
        another_time = False


@dp.message_handler(Text(equals=['Завершить вызов']), state=["in_support", 'wait_in_support'])
async def exit_support(message: types.Message, state: FSMContext):
    iterator = 0
    second_state = dp.current_state(user=message.from_user.id, chat=message.from_user.id)
    data = await second_state.get_data()
    user_id = data.get('second_id')
    if str(await state.get_state()) == 'wait_in_support':
        cur_el = 'qwerty'
        for el in range(len(queue)):
            if str(message.from_user.id) in str(queue[el]):
                cur_el = str(el)
                break
        if cur_el != '0':
            iterator = 1
        try:
            del queue[int(cur_el)]
        except ValueError:
            pass
    if await state.get_state() == 'in_support':
        second_state = dp.current_state(user=user_id, chat=user_id)
        await second_state.reset_state()
        await bot.send_message(chat_id=user_id, text='Пользователь завершил сеанс тех.поддержки',
                               reply_markup=start_keyboard)
    else:
        iterator = 1
    await message.answer('Вы завершили сеанс тех.поддержки', reply_markup=start_keyboard)
    await state.reset_state()
    global another_time
    if iterator == 0 and (not another_time) and queue and message.from_user.id not in queue:
        another_time = True
        await asyncio.sleep(5)
        await next_one(str(queue[0]))


@dp.message_handler(state=["wait_in_support", "start", "pre_wait_in_support"], content_types=types.ContentTypes.ANY)
async def not_supported(message: types.Message, state: FSMContext):
    if await state.get_state() == 'start' or await state.get_state() == 'pre_wait_in_support':
        await message.answer('Нажмите на кнопку "Написать оператору" или отмените вызов')
    else:
        data = await state.get_data()
        second_id = data.get("second_id")
        if not second_id and message.from_user.id not in support_ids:
            await message.answer("Дождитесь ответа оператора или отмените сеанс")


@dp.callback_query_handler(cancel_support_callback.filter(),
                           state=['start', 'pre_wait_in_support'])
async def exit_support(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.message.edit_text("Вы завершили сеанс")


@dp.callback_query_handler(text_contains="support_from_items", state=[None])
async def ask_support_call(call: CallbackQuery, state: FSMContext):
    item_id = call.data.split(':')[-1]
    text = "Нажмите на кнопку написать оператору и он ответит на любые вопросы."
    keyboard = await support_keyboard(messages="many")
    await state.set_state('pre_wait_in_support')
    await state.update_data(item_id=item_id)
    return await call.message.answer(text, reply_markup=keyboard)


async def next_one(inf: str):
    sup_id = await get_support_manager()
    if sup_id:
        '''queue[0] = str(call.from_user.id) + ' ' + str(len(contact_ids))'''
        for i in range(len(sup_id)):
            x = inf.split()
            keyboard1 = await support_keyboard(messages='many', user_id=str(x[0]),
                                               free_id=sup_id[i])
            await bot.send_message(chat_id=sup_id[i],
                                   text=f"С вами хочет связаться пользователь\n"
                                        f" {inf[str(queue[0]).find(' '):inf.rfind(' ')]}",
                                   reply_markup=keyboard1)
