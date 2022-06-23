from aiogram.dispatcher.filters import Text

from handlers.users.menu_handlers import show_menu
from keyboards.default.new_keyboard import start_keyboard
from loader import dp
from aiogram import types
from data.config import admins
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from states.state import DeleteItem
from utils.db_api.db_commands import delete_item, get_item

del_item = {
    'id': []
}
ret_call = CallbackData('ret', 'pos')


@dp.message_handler(Text(equals=['Выйти']), user_id=admins, state=[DeleteItem, 'returning'])
async def exit_(message: types.Message, state: FSMContext):
    for i in del_item.keys():
        del_item[i] = []
    await message.answer('Вы ничего не удалили', reply_markup=start_keyboard)
    await state.reset_state()


@dp.message_handler(commands=['remove_item'], user_id=admins)
async def remove(message: types.Message, state: FSMContext):
    await DeleteItem.First.set()
    await show_menu(message, state)


@dp.callback_query_handler(text_contains='delete', user_id=admins, state=DeleteItem.First)
async def delete(call: types.CallbackQuery):
    if len(del_item['id']) >= 10:
        await call.message.answer('Вы поместили в очередь 10 товаров, максимум. Дальнейшие '
                                  'удаления засчитываться не будут.')
    else:
        await call.message.delete()
        del_item['id'].append(call.data.split(':')[-1])


@dp.message_handler(Text(equals=['Закончить добавление']), user_id=admins, state=DeleteItem.First)
async def last(message: types.Message):
    markup = types.ReplyKeyboardMarkup(keyboard=[
        [
            types.KeyboardButton('Да'),
            types.KeyboardButton('Нет')
        ]
    ], resize_keyboard=True)
    await message.answer('Вы уверены?', reply_markup=markup)


@dp.message_handler(Text(equals=['Закончить изменения']), user_id=admins, state='returning')
@dp.message_handler(Text(equals=['Да']), user_id=admins, state=DeleteItem.First)
async def yes(message: types.Message, state: FSMContext):
    for i in range(len(del_item.get('id'))):
        await delete_item(int(del_item['id'][i]))
    await state.reset_state()
    if len(del_item.get('id')) == 0:
        await message.answer('Вы ничего не удалили', reply_markup=start_keyboard)
    else:
        await message.answer('Товары успешно удалены', reply_markup=start_keyboard)
    del_item['id'] = []


@dp.message_handler(Text(equals=['Нет']), user_id=admins, state=DeleteItem.First)
async def no(message: types.Message, state: FSMContext):
    await state.set_state('returning')
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton('Закончить изменения'),
                types.KeyboardButton('Выйти')
            ]
        ], resize_keyboard=True
    )
    await message.answer('Выберите, что вы не хотите удалять', reply_markup=keyboard)
    for i in range(len(del_item.get('id'))):
        item = await get_item(int(del_item['id'][i]))
        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text='Вернуть товар', callback_data=ret_call.new(pos=i))
                ]
            ]
        )
        await message.answer_photo(item.photo.split(',')[0], reply_markup=markup,
                                   caption=f'Категория и код категории: {item.category_name}, {item.category_code}\n'
                                           f'Подкатегория и код подкатегории: {item.subcategory_name}, '
                                           f'{item.subcategory_code}\n'
                                           f'Имя: {item.name}\n'
                                           f'Caption: {item.inscription}')


@dp.callback_query_handler(text_contains='ret', user_id=admins, state='returning')
async def ret2(call: types.CallbackQuery):
    await call.message.delete()
    del_item.get('id').pop(int(str(call.data.split(':')[-1])))
