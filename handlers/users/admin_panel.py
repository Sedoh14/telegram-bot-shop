import asyncio
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import ChatNotFound, Unauthorized
from aiogram.types import ReplyKeyboardRemove
from data.config import admins
from handlers.users.menu_handlers import show_menu, add_item, list_subcategories, list_categories
from loader import dp, bot
from states.state import NewItem, DeleteItem, Add_supporter, Remove_supporter
from utils.db_api.db_commands import get_the_only_item, updating, updating1, updating2
from utils.db_api.models import Item
from keyboards.default.new_keyboard import start_keyboard
from data.config import support_ids

change_callback = CallbackData('item_change', 'cur_pos', 'delete')
change_item = CallbackData('alter', 'pos', 'cat', 'subcat', 'name', 'photo', 'caption')


def make_callback_data(pos, cat='0', subcat='0', name='0', photo='0', caption='0'):
    return change_item.new(pos=pos, cat=cat, subcat=subcat, name=name, photo=photo, caption=caption)


@dp.message_handler(Text(equals=['Закончить добавление']), user_id=admins, state=[NewItem.Confirm, NewItem.Category])
async def confirm(message: types.Message):
    if len(add_item['cat']) > len(add_item['cat']):
        add_item.get('cat').pop()
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton('Да'),
                types.KeyboardButton('Нет')
            ]
        ], resize_keyboard=True
    )
    await message.answer('Хотите исправить', reply_markup=markup)
    await NewItem.Change.set()


@dp.message_handler(user_id=admins, commands=["cancel"], state=NewItem)
async def cancel(message: types.Message, state: FSMContext):
    for i in add_item.keys():
        add_item[i] = []
    await message.answer('Вы не добавили ни один товар в базу данных', reply_markup=start_keyboard)
    await state.reset_state()


@dp.message_handler(user_id=admins, commands=["cancel"], state=DeleteItem)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили удаление товара")
    await state.reset_state()


@dp.message_handler(user_id=admins, commands=["cancel"], state=Add_supporter)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили добавление id ")
    await state.reset_state()


@dp.message_handler(user_id=admins, commands=["cancel"], state=Remove_supporter)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Вы отменили удаление id ")
    await state.reset_state()


@dp.message_handler(user_id=admins, commands=["add_item"])
async def add_item1(message: types.Message, state: FSMContext):
    await NewItem.Category.set()
    await show_menu(message, state)


@dp.message_handler(user_id=admins,
                    state=[NewItem.Category_code, NewItem.Confirm, NewItem.Subcategory, NewItem.Subcategory_code,
                           NewItem.Another, NewItem.Another1, 'NewItem:Another2', 'NewItem:Subcategory_code1',
                           'NewItem:Subcategory1'])
async def enter_name(message: types.Message, state: FSMContext):
    flag = 0
    ch = 0
    if await state.get_state() == 'NewItem:Confirm':
        add_item.get('cat').append(add_item.get('cat')[-1])
        add_item.get('subcat').append(add_item.get('subcat')[-1])
    elif await state.get_state() in ['NewItem:Subcategory', 'NewItem:Subcategory1']:
        try:
            l = await get_the_only_item()
            if await state.get_state() == 'NewItem:Subcategory':
                add_item.get('subcat').append(message.text.split('^')[0] + ' ' + l.subcategory_code)
                ch += 1
                add_item.get('name').append(message.text.split('^')[1])
                ch += 1
                flag = 1
                await NewItem.Category.set()
            else:
                data = await state.get_data()
                data = int(data.get('pos'))
                add_item['subcat'][data] = message.text.split('^')[0] + ' ' + l.subcategory_code
                await change(message, state)
            if ord(l.subcategory_code[2]) != 123:
                await updating1(l.subcategory_code[:2] + chr(ord(l.subcategory_code[2]) + 1))
            elif ord(l.subcategory_code[2]) == 123 and ord(l.subcategory_code[1]) != 123:
                await updating1(l.subcategory_code[0] + chr(ord(l.subcategory_code[1]) + 1) + 'a')
            else:
                await updating1(chr(ord(l.subcategory_code[0]) + 1) + 'a' + 'a')

        except IndexError:
            await message.answer('Вы ввели некорректно, попробуйте ещё раз')
            for i in add_item.keys():
                if ch == 0:
                    break
                ch -= 1
                add_item.get(i).pop()
            # await NewItem.Another.set()
    elif await state.get_state() in ['NewItem:Subcategory_code', 'NewItem:Subcategory_code1']:
        try:
            l = await get_the_only_item()
            if await state.get_state() == 'NewItem:Subcategory_code':
                add_item.get('cat').append(message.text.split('^')[0] + ' ' + l.subcategory_name)
                ch += 1
                add_item.get('subcat').append(message.text.split('^')[1] + ' ' + l.subcategory_code)
                ch += 1
                add_item.get('name').append(message.text.split('^')[2])
                ch += 1
                await NewItem.Category.set()
            else:
                data = await state.get_data()
                data = int(data.get('pos'))
                # проверяю на правильность ввода чтобы не добавлялось заранее
                add_item['cat'][data] = message.text.split('^')[0] + ' ' + l.subcategory_name
                add_item['subcat'][data] = message.text.split('^')[1] + ' ' + l.subcategory_code
                await change(message, state)
            flag = 1
            if ord(l.subcategory_code[2]) != 123:
                await updating1(l.subcategory_code[:2] + chr(ord(l.subcategory_code[2]) + 1))
            elif ord(l.subcategory_code[2]) == 123 and ord(l.subcategory_code[1]) != 123:
                await updating1(l.subcategory_code[0] + chr(ord(l.subcategory_code[1]) + 1) + 'a')
            else:
                await updating1(chr(ord(l.subcategory_code[0]) + 1) + 'a' + 'a')
            if ord(l.subcategory_name[2]) != 123:
                await updating(l.subcategory_name[:2] + chr(ord(l.subcategory_name[2]) + 1))
            elif ord(l.subcategory_name[2]) == 123 and ord(l.subcategory_name[1]) != 123:
                await updating(l.subcategory_name[0] + chr(ord(l.subcategory_name[1]) + 1) + 'a')
            else:
                await updating(chr(ord(l.subcategory_name[0]) + 1) + 'a' + 'a')
        except IndexError:
            await message.answer('Вы ввели некорректно, попробуйте ещё раз')
            for i in add_item.keys():
                if ch == 0:
                    break
                ch -= 1
                add_item.get(i).pop()
    elif await state.get_state() in ['NewItem:Another1', 'NewItem:Another2']:
        try:
            l = await get_the_only_item()
            if await state.get_state() == 'NewItem:Another1':
                add_item.get('cat').append(message.text.split('^')[0] + ' ' + l.name)
                ch += 1
                add_item.get('subcat').append(l.name + ' ' + l.name)
                ch += 1
                add_item.get('name').append(message.text.split('^')[1])
                ch += 1
                await NewItem.Category.set()
            else:
                data = await state.get_data()
                data = int(data.get('pos'))
                add_item['cat'][data] = message.text.split('^')[0] + ' ' + l.name
                add_item['subcat'][data] = l.name + ' ' + l.name
                await change(message, state)
            await updating2('-' + str(int(l.name.split('-')[1]) + 1))
            flag = 1
        except IndexError:
            await message.answer('Вы ввели некорректно, попробуйте ещё раз')
            for i in add_item.keys():
                if ch == 0:
                    break
                add_item.get(i).pop()
                ch -= 1
    if await state.get_state() not in ['NewItem:Subcategory', 'NewItem:Subcategory_code', 'NewItem:Another1',
                                       'NewItem:Subcategory1', 'NewItem:Subcategory_code1', 'NewItem:Another2',
                                       'altering']:
        name = message.text

        await message.answer(("Название: {name}"
                              "\nПришлите мне медиа товара (фотография или видео) или нажмите /cancel. "
                              "Вы можете присылать медиа товара несколькими сообщениями. "
                              "Введите caption после того, как всё пришлёте.").format(
            name=name))
        if flag == 0:
            add_item.get('name').append(str(name))
        await NewItem.Photo.set()


@dp.message_handler(user_id=admins, state=[NewItem.Photo, NewItem.New_photo],
                    content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO])
async def add_photo(message: types.Message, state: FSMContext):
    await asyncio.sleep(0.5)
    data = await state.get_data()
    ph = data.get('photo', 'empty')
    k = data.get('quantity')
    if ph == 'empty':
        ph = ''
        k = 0
    if int(k) > 9:
        if int(k) == 10:
            k = int(k) + 1
            await message.answer('Вы также ввели более 10 фотографий. '
                                 'Дальнейшии медиа в базу данных на эту позицию товара не принимаются.')
    else:
        k = int(k) + 1
        if message.photo:
            ph += message.photo[-1].file_id + ','
        else:
            ph += message.video.file_id +'ВИДЕО'+ ','
        await state.update_data(photo=ph, quantity=k)
        if int(k) == 1:
            if str(await state.get_state()) == 'NewItem:New_photo':
                continue_keyboard = types.ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            types.KeyboardButton('Закончить ввод медиа')
                        ],
                    ], resize_keyboard=True
                )
            else:
                continue_keyboard = None
            if continue_keyboard:
                await message.answer("Вы можете присылать медиа товара несколькими сообщениями. "
                                     "Введите caption после того, как всё пришлёте.", reply_markup=continue_keyboard)
            else:
                await message.answer("Вы можете присылать медиа товара несколькими сообщениями. "
                                     "Введите caption после того, как всё пришлёте")


@dp.message_handler(user_id=admins, state=[NewItem.Photo, NewItem.New_photo])
async def enter_caption(message: types.Message, state: FSMContext):
    if await state.get_state() == 'NewItem:New_photo':
        data = await state.get_data()
        data1 = data.get('pos')
        photo = data.get('photo')
        add_item['photo'][int(data1)] = photo
        await state.reset_data()
        await state.update_data(pos=data1)
        await NewItem.Change.set()
        await change(message, state)
    elif await state.get_state() == 'NewItem:Photo':
        data = await state.get_data()
        photo = data.get('photo')
        if not photo:
            await message.answer('Вы не прислали ни одной фотографии')
        else:
            add_item.get('photo').append(photo)
            await state.reset_data()
            add_item.get('inscription').append(str(message.text))
            if '-' not in str(add_item.get('subcat')[-1].split()[-1]):
                markup = types.ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            types.KeyboardButton('Закончить добавление')
                        ],
                        [
                            types.KeyboardButton('Назад в категорию'),
                            types.KeyboardButton('Назад в подкатегорию')
                        ],

                    ], resize_keyboard=True
                )
            else:
                markup = types.ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            types.KeyboardButton('Закончить добавление'),
                            types.KeyboardButton('Назад в категорию'),
                        ],
                    ], resize_keyboard=True
                )
            await message.answer(
                "Товар сохранён , но ещё не создан. Введите имя, фотографии и caption для "
                "добавления ещё одного товара сюда же",
                reply_markup=markup)
            await NewItem.Confirm.set()
            if len(add_item['name']) == 10:
                await message.answer('Вы ввели 10 товаров, это максимум для одной итерации.')
                await confirm(message, state)


@dp.message_handler(Text(equals=['Закончить добавление']), user_id=admins, state=[NewItem.Confirm, NewItem.Category])
async def confirm(message: types.Message):
    if len(add_item['cat']) > len(add_item['cat']):
        add_item.get('cat').pop()
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton('Да'),
                types.KeyboardButton('Нет')
            ]
        ], resize_keyboard=True
    )
    await message.answer('Хотите исправить?', reply_markup=markup)
    await NewItem.Change.set()


@dp.message_handler(Text(equals=['Да']), user_id=admins, state=[NewItem.Change])
async def change(mess: Union[types.Message, types.CallbackQuery], state: FSMContext):
    min_len = min(len(add_item['cat']), len(add_item['subcat']), len(add_item['name']), len(add_item['photo']),
                  len(add_item['inscription']))
    if len(add_item['cat']) > min_len:
        add_item['cat'].pop()
    elif len(add_item['cat']) != min_len or len(add_item['subcat']) != min_len or len(
            add_item['name']) != min_len or len(
        add_item['photo']) < min_len or len(add_item['inscription']) != min_len:
        pass
    if len(add_item['subcat']) == 0:
        await mess.answer('Нечего изменять, так как вы ничего не добавили', reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
    else:
        await state.set_state('altering')
        length = len(add_item.get('cat'))
        markup = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton('Закончить изменение товаров'),
                    types.KeyboardButton('Выйти')
                ]
            ], resize_keyboard=True
        )
        if isinstance(mess, types.Message):
            await mess.answer('Вот что вы добавили', reply_markup=markup)
        else:
            await mess.message.delete()
            await mess.message.answer('Вот что вы добавили')
        for i in range(length):
            await asyncio.sleep(0.3)
            markup = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text='Изменить товар',
                            callback_data=change_callback.new(
                                cur_pos=i,
                                delete=False
                            )
                        ),
                        types.InlineKeyboardButton(
                            text='Удалить товар',
                            callback_data=change_callback.new(
                                cur_pos=i,
                                delete=True
                            )
                        )
                    ]
                ]
            )
            if isinstance(mess, types.Message):
                await mess.answer_photo(photo=str(str(add_item['photo'][i]).split(',')[0]),
                                        caption=f'Категория и код категории: {", ".join(str(add_item["cat"][i]).split())}\n'
                                                f'Подкатегория и код подкатегории: {", ".join(str(add_item["subcat"][i]).split())}\n'
                                                f'Имя: {", ".join(str(add_item["name"][i]).split())}\n'
                                                f'Caption: {", ".join(str(add_item["inscription"][i]).split())}',
                                        reply_markup=markup)
            else:
                await mess.message.answer_photo(photo=str(str(add_item['photo'][i]).split(',')[0]),
                                                caption=f'Категория и код категории: {", ".join(str(add_item["cat"][i]).split())}\n'
                                                        f'Подкатегория и код подкатегории: {", ".join(str(add_item["subcat"][i]).split())}\n'
                                                        f'Имя: {", ".join(str(add_item["name"][i]).split())}\n'
                                                        f'Caption: {", ".join(str(add_item["inscription"][i]).split())}',
                                                reply_markup=markup)


@dp.callback_query_handler(text_contains='item_change', state='altering', user_id=admins)
async def item_change(call: types.CallbackQuery):
    data = call.data.split(':')
    if data[-1] == 'True':
        add_item.get('cat').pop(int(data[1]))
        add_item.get('subcat').pop(int(data[1]))
        add_item.get('name').pop(int(data[1]))
        add_item.get('photo').pop(int(data[1]))
        add_item.get('inscription').pop(int(data[1]))
        await call.message.delete()
    else:
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.insert(
            types.InlineKeyboardButton(text='Изменить категорию',
                                       callback_data=make_callback_data(pos=data[1], cat='True'))
        )
        if '-' not in str(add_item['subcat'][int(data[1])]):
            markup.insert(
                types.InlineKeyboardButton(text='Изменить подкатегорию',
                                           callback_data=make_callback_data(pos=data[1], cat='0', subcat='True')))
        markup.row(types.InlineKeyboardButton(text='Изменить имя',
                                              callback_data=make_callback_data(pos=data[1], cat='0', subcat='0',
                                                                               name='True')), )
        markup.insert(types.InlineKeyboardButton(text='Изменить фото',
                                                 callback_data=make_callback_data(pos=data[1], cat='0', subcat='0',
                                                                                  name='0',
                                                                                  photo='True')), )
        markup.insert(types.InlineKeyboardButton(text='Изменить caption',
                                                 callback_data=make_callback_data(pos=data[1], cat='0', subcat='0',
                                                                                  name='0',
                                                                                  photo='0', caption='True')), )
        await call.message.reply('Что вы хотите изменить ', reply_markup=markup)


@dp.callback_query_handler(text_contains='alter', state='altering')
async def know_what_to_change(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split(':')
    for i in range(1, len(data)):
        if data[i] == 'True':
            if str(i - 1) in ['3', '5']:
                await call.message.edit_text('Введите текст')
                await state.update_data(update=i, pos=data[1])
            elif i == 5:
                await call.message.edit_text('Пришлите фотографии')
                await NewItem.New_photo.set()
                await state.update_data(pos=data[1])
            elif i == 3:
                cur_pos = data[1]
                await state.update_data(pos=cur_pos)
                await list_subcategories(call, add_item['cat'][int(cur_pos)].split()[-1], state)
            elif i == 2:
                cur_pos = data[1]
                await NewItem.cat.set()
                await state.update_data(pos=cur_pos)
                await list_categories(call, state)


@dp.message_handler(Text(equals=['Закончить изменение товаров']),
                    state=[NewItem.Change, 'altering', 'NewItem:Another2', 'NewItem:Subcategory_code1',
                           'NewItem:Subcategory1'])
@dp.message_handler(Text(equals=['Нет']), user_id=admins, state=[NewItem.Change])
async def not_change(message: types.Message, state: FSMContext):
    length = len(add_item.get('cat'))
    min_len = min(len(add_item['cat']), len(add_item['subcat']), len(add_item['name']), len(add_item['photo']),
                  len(add_item['inscription']))
    if len(add_item['cat']) > min_len:
        add_item['cat'].pop()
    elif len(add_item['cat']) != min_len or len(add_item['subcat']) != min_len or len(
            add_item['name']) != min_len or len(
        add_item['photo']) < min_len or len(add_item['inscription']) != min_len:
        await message.answer('Не добавлено ни одного товара.')
    else:
        for i in range(length):
            item = Item()
            item.category_name = ' '.join(add_item.get('cat')[-1].split()[:-1])
            item.category_code = add_item.get('cat')[-1].split()[-1]
            item.subcategory_name = ' '.join(add_item.get('subcat')[-1].split()[:-1])
            item.subcategory_code = add_item.get('subcat')[-1].split()[-1]
            item.name = add_item.get('name')[-1]
            item.photo = add_item.get('photo')[-1]
            item.inscription = add_item.get('inscription')[-1]
            await item.create()
            add_item.get('cat').pop()
            add_item.get('subcat').pop()
            add_item.get('name').pop()
            add_item.get('photo').pop()
            add_item.get('inscription').pop()
        if length == 0:
            await message.answer('Вы ничего не добавили в базу данных', reply_markup=start_keyboard)
        else:
            await message.answer('Товары добавлены в базу данных', reply_markup=start_keyboard)
        await state.reset_state()


@dp.message_handler(user_id=admins, state='altering')
async def mes_change(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data1 = data.get('update')
    data2 = data.get('pos')
    array = ['name', 'photo', 'inscription']
    if int(data1) > 3 and int(data1) != 5:
        add_item[str(array[int(data1) - 4])][int(data2)] = message.text
        await NewItem.Change.set()
        await change(message, state)


@dp.callback_query_handler(text_contains='new', state=[NewItem.Category, NewItem.cat, 'altering'], user_id=admins)
async def new(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data.split(':')[-1] == '0':
        markup = types.ReplyKeyboardMarkup(keyboard=[
            [
                types.KeyboardButton('Назад в категорию'),

            ]
        ], resize_keyboard=True)

        if await state.get_state() != 'NewItem:Category':
            await state.set_state('NewItem:Subcategory_code1')
            await call.message.answer('Введите через знак "^": категорию, подкатегорию')
        else:
            await call.message.answer(
                'Введите через знак "^": категорию, подкатегорию, имя',
                reply_markup=markup)
            await NewItem.Subcategory_code.set()
    elif call.data.split(':')[-1] == '1':
        markup = types.ReplyKeyboardMarkup(keyboard=[
            [
                types.KeyboardButton('Назад в категорию'),
                types.KeyboardButton('Назад в подкатегорию')

            ]
        ], resize_keyboard=True)

        if await state.get_state() != 'NewItem:Category':
            await state.set_state('NewItem:Subcategory1')
            await call.message.answer(
                'Введите через знак "^": подкатегорию')
        else:
            await call.message.answer(
                'Введите через знак "^": подкатегорию, имя', reply_markup=markup)
            await NewItem.Subcategory.set()
    else:
        markup = types.ReplyKeyboardMarkup(keyboard=[
            [
                types.KeyboardButton('Назад в категорию'),

            ]
        ], resize_keyboard=True)

        if await state.get_state() != 'NewItem:Category':
            await state.set_state('NewItem:Another2')
            await call.message.answer(
                'Введите через знак "^": категорию')
        else:
            await call.message.answer(
                'Введите через знак "^": категорию, имя', reply_markup=markup)
            await NewItem.Another1.set()


@dp.message_handler(user_id=admins, commands=['add_supporter'])
async def add_supporter(message: types.Message):
    await message.answer('Введите id нового представителя тех. поддержки. Помните, что он обязательно '
                         'должен перейти по ссылке на бота @antikvarnyi_magazinbot и нажать на кнопку '
                         '"start" перед тем, '
                         'как вы введёте данный id(для корректной работы бота) '
                         'или нажмите /cancel')
    await Add_supporter.sup_id.set()


@dp.message_handler(user_id=admins, state=Add_supporter.sup_id)
async def add_supporter(message: types.Message, state: FSMContext):
    try:
        await bot.send_message(chat_id=message.text, text='Здравствуйте')
    except ChatNotFound:
        await bot.send_message(chat_id=admins,
                               text=f'Данный id("{message.text}") не существует, т.к. введён некорректно. '
                                    f'Введите ещё раз или нажмите /cancel')
    except Unauthorized:
        await bot.send_message(chat_id=admins, text=f'Данный id("{message.text}") введён корректно, но пользователь не '
                                                    f'перешёл '
                                                    f'по ссылке на бота и не запустил его прежде, как вы попытались '
                                                    f'добавить его id. Если вы хотите добавить его id, то он '
                                                    f'должен перейти по ссылке @antikvarnyi_magazinbot и запустить бота.'
                                                    f' Введите ещё раз или нажмите /cancel')
    else:
        support_ids.append(message.text)
        flag = True
        await message.answer('id добавлен')
        await state.reset_state()


@dp.message_handler(user_id=admins, commands=['remove_supporter'])
async def remove_supporter(message: types.Message):
    await message.answer(f'Введите id, который вы хотите удалить из представителей тех. поддержки или нажмите /cancel\n'
                         f'На данный момент имеются: {str(support_ids)}')
    await Remove_supporter.supp_id.set()


@dp.message_handler(user_id=admins, state=Remove_supporter.supp_id)
async def remove_supporter(message: types.Message, state: FSMContext):
    try:
        support_ids.remove(message.text)
        await message.answer('id удалён')
        await state.reset_state()
    except ValueError:
        await message.answer('Такого id не существует. Веедите ещё раз или нажмите /cancel')
