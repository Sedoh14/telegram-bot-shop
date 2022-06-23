import asyncio
import logging

import emoji
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, InputMediaPhoto, InputMediaVideo)
from aiogram.utils.callback_data import CallbackData

from loader import dp, bot
from typing import Union
from keyboards.default.new_keyboard import back_keyboard, back1_keyboard, start_keyboard
from keyboards.inline.menu_keyboards import menu_cd, categories_keyboard, subcategories_keyboard, items_keyboard, \
    show_photo, proceed, make_callback_data, supports_item, del_callback
from states.state import NewItem, DeleteItem
from utils.db_api.db_commands import get_item, get_short_items

support_item = CallbackData("sup", 'support_from_items', "item_id")
all_continue = CallbackData('proc', 'category', 'calc')
new_call = CallbackData('new', 'category')

add_item = {'cat': [],
            'subcat': [],
            'name': [],
            'photo': [],
            'inscription': [],
            }


@dp.message_handler(
    Text(equals=["товары", "Товары", "интересуют товары из категории", "Интересуют товары из категории"]))
async def show_menu(message: types.Message, state: FSMContext):
    markup1 = types.ReplyKeyboardMarkup(keyboard=[
        [
            types.KeyboardButton('Закончить добавление'),
            types.KeyboardButton('Выйти'),
        ]
    ], resize_keyboard=True)
    if await state.get_state() in ['NewItem:Category', 'DeleteItem:First']:
        await message.answer('Если вы хотите закончить ввод нажмите на кнопку внизу экрана', reply_markup=markup1)
    await list_categories(message, state)


@dp.message_handler(Text(equals=['Назад в категорию']),
                    state=[NewItem.Category, NewItem.Photo, NewItem.Caption, NewItem.Confirm, NewItem.Category_code,
                           NewItem.Another1, NewItem.Another, NewItem.Subcategory, NewItem.Subcategory_code])
async def back_to_category(message: Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(keyboard=[
        [
            types.KeyboardButton('Закончить добавление'),
            types.KeyboardButton('Выйти'),
        ]
    ], resize_keyboard=True)
    await message.answer('Вы перешли в категории', reply_markup=markup)
    cur_state = str(await state.get_state())
    if cur_state in ['NewItem:Subcategory']:
        add_item.get('cat').pop()
    elif cur_state == 'NewItem:Category_code':
        add_item.get('cat').pop()
        add_item.get('subcat').pop()
    elif cur_state == 'NewItem:Photo':
        add_item.get('cat').pop()
        add_item.get('subcat').pop()
        add_item.get('name').pop()
        if len(add_item.get('photo')) != len(add_item.get('name')):
            add_item.get('photo').pop()
    elif cur_state == 'NewItem:Caption':
        add_item.get('cat').pop()
        add_item.get('subcat').pop()
        add_item.get('name').pop()
        if len(add_item.get('photo')) != len(add_item.get('name')):
            add_item.get('photo').pop()
    await NewItem.Category.set()
    await list_categories(message, state)


async def list_categories(message: Union[CallbackQuery, Message], state: FSMContext, **kwargs):
    markup = await categories_keyboard()
    if await state.get_state() in ['NewItem:Category', 'NewItem:cat']:
        markup.row(
            types.InlineKeyboardButton(
                text='Новая категория',
                callback_data=new_call.new(
                    category=0,
                )
            )
        )
        markup.row(
            types.InlineKeyboardButton(
                text='Новая категория без подкатегории',
                callback_data=new_call.new(
                    category=2,
                )
            )
        )
    if isinstance(message, Message):
        await message.answer("Вот, что у нас есть", reply_markup=markup)
    elif isinstance(message, CallbackQuery):
        call = message
        if '-' in str(message.data.split(':')[2]):
            await call.message.edit_text('Вот, что у нас есть', reply_markup=markup)
        else:
            await call.message.edit_reply_markup(markup)


@dp.message_handler(Text(equals=['Выйти']),
                    state=[NewItem.Category, NewItem.Another1, NewItem.Subcategory,
                           NewItem.Subcategory_code, NewItem.Change, 'altering', NewItem.cat])
async def exit(message: types.Message, state: FSMContext):
    for i in add_item.keys():
        add_item[i] = []
    await message.answer('Вы не добавили ни один товар в базу данных', reply_markup=start_keyboard)
    await state.reset_state()


@dp.message_handler(Text(equals=['Назад в подкатегорию']),
                    state=[NewItem.Category, NewItem.Photo, NewItem.Caption, NewItem.Confirm, NewItem.Category_code,
                           NewItem.Another1, NewItem.Another, NewItem.Subcategory, NewItem.Subcategory_code])
async def back_to_sub(message: Message, state: FSMContext):
    category = add_item.get('cat')[-1].split()[-1]
    cur_state = str(await state.get_state())
    if cur_state == 'NewItem:Category_code':
        add_item.get('subcat').pop()
    elif cur_state == 'NewItem:Photo':
        add_item.get('subcat').pop()
        add_item.get('name').pop()
        if len(add_item.get('photo')) != len(add_item.get('name')):
            add_item.get('photo').pop()
    elif cur_state == 'NewItem:Caption':
        add_item.get('subcat').pop()
        add_item.get('name').pop()
        if len(add_item.get('photo')) != len(add_item.get('name')):
            add_item.get('photo').pop()
    if cur_state == 'NewItem:Confirm':
        add_item.get('cat').append(add_item.get('cat')[-1])
    markup = await subcategories_keyboard(str(category), state)
    markup.row(
        InlineKeyboardButton(
            text='Новая подкатегория',
            callback_data=new_call.new(
                category=1
            )
        )
    )
    await NewItem.Category.set()
    markup1 = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton('Закончить добавление'),
                types.KeyboardButton('Выйти'),
            ],
        ], resize_keyboard=True
    )
    await message.answer('Вы перешли в список подкатегорий', reply_markup=markup1)
    await message.answer(text='Вот, что у нас есть', reply_markup=markup)


async def list_subcategories(callback: CallbackQuery, category, state: FSMContext, **kwargs):
    markup = await subcategories_keyboard(category, state)
    if str(await state.get_state()) == 'NewItem:Category':
        if abs(len(add_item.get('cat')) - len(add_item.get('subcat'))) > 0:
            add_item['cat'] = add_item.get('cat')[:len(add_item.get('subcat'))]
        for i in callback.message.reply_markup.inline_keyboard:
            if i[0]['callback_data'] == str(callback.data):
                add_item.get('cat').append(' '.join(i[0]['text'].split()[:-2]) + ' ' + str(callback.data.split(':')[2]))
                break
    if isinstance(markup, InlineKeyboardMarkup) and '-' not in str(category) and await state.get_state() in [
        'NewItem:Category', 'NewItem:cat', 'altering']:
        markup.row(
            InlineKeyboardButton(
                text='Новая подкатегория',
                callback_data=new_call.new(
                    category=1,
                )
            )
        )
    if await state.get_state() == 'NewItem:cat':
        for i in callback.message.reply_markup.inline_keyboard:
            if i[0]['callback_data'] == str(callback.data):
                data = await state.get_data()
                data = data.get('pos')

                add_item['cat'][int(data)] = (
                            ' '.join(i[0]['text'].split()[:-2]) + ' ' + str(callback.data.split(':')[2]))
                add_item['cat'].append(int(data))
                break
    if str(markup).isalpha():
        await callback.message.edit_text('Вот что у нас есть')
    if str(markup).isdigit():
        if await state.get_state() == 'NewItem:cat':
            data = await state.get_data()
            data = data.get('pos')
            add_item['subcat'][int(data)] = category + ' ' + category
            add_item['cat'].pop()
            from handlers.users.admin_panel import change
            await change(callback, state)

        else:
            cur_state = await state.get_state()
            await list_items(callback, category, cur_state, '-' + str(markup))
    else:
        callback_data = callback.data
        logging.info(f"callback_data='{callback_data}'")
        await callback.message.edit_text('Вот что у нас есть', reply_markup=markup)


async def list_items(callback: CallbackQuery, category, state, subcategory, **kwargs):
    if '-' not in subcategory:
        cur_state = str(await state.get_state())
    else:
        cur_state = str(state)
    if 'NewItem:Category' in cur_state:
        await NewItem.Category_code.set()
        await callback.message.delete()
        if '-' in category:
            add_item.get('subcat').append(category + ' ' + category)
        else:
            for i in callback.message.reply_markup.inline_keyboard:
                if i[0]['callback_data'] == str(callback.data):
                    add_item.get('subcat').append(
                        ' '.join(i[0]['text'].split()[:-2]) + ' ' + str(callback.data.split(':')[3]))
                    break
        if '-' not in subcategory:
            await bot.send_message(chat_id=callback.from_user.id, text='Введите имя товара, медиа, caption.',
                                   reply_markup=back_keyboard)
        else:
            await bot.send_message(chat_id=callback.from_user.id, text='Введите имя товара, медиа, caption.',
                                   reply_markup=back1_keyboard)
    elif cur_state == 'altering':
        data = await state.get_data()
        data = data.get('pos')
        for i in callback.message.reply_markup.inline_keyboard:
            if i[0]['callback_data'] == str(callback.data):
                add_item.get('subcat')[int(data)] = (
                            ' '.join(i[0]['text'].split()[:-2]) + ' ' + str(callback.data.split(':')[3]))
                break
        from handlers.users.admin_panel import change
        await change(callback, state)
    elif cur_state == 'NewItem:cat':
        data = add_item['cat'][-1]
        add_item['cat'].pop()
        for i in callback.message.reply_markup.inline_keyboard:
            if i[0]['callback_data'] == str(callback.data):
                add_item.get('subcat')[int(data)] = (
                        ' '.join(i[0]['text'].split()[:-2]) + ' ' + str(callback.data.split(':')[3]))
                break
        from handlers.users.admin_panel import change
        await change(callback, state)
    else:
        await callback.message.edit_reply_markup()
        markup = await items_keyboard(callback, category, subcategory, cur_state)


@dp.callback_query_handler(menu_cd.filter(), state=[NewItem.Category, NewItem.Photo, NewItem.Caption, NewItem.Confirm,
                                                    NewItem.Category_code, 'altering', NewItem.cat, DeleteItem.First,
                                                    None])
@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: CallbackQuery, callback_data: dict, state: FSMContext):
    """

    :param call: Тип объекта CallbackQuery, который прилетает в хендлер
    :param callback_data: Словарь с данными, которые хранятся в нажатой кнопке
    """

    # Получаем текущий уровень меню, который запросил пользователь
    current_level = callback_data.get("level")

    # Получаем категорию, которую выбрал пользователь (Передается всегда)
    category = callback_data.get("category")

    # Получаем подкатегорию, которую выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    subcategory = callback_data.get("subcategory")

    # Получаем айди товара, который выбрал пользователь (Передается НЕ ВСЕГДА - может быть 0)
    item_id = int(callback_data.get("item_id"))
    # Прописываем "уровни" в которых будут отправляться новые кнопки пользователю
    levels = {
        "0": list_categories,  # Отдаем категории
        "1": list_subcategories,  # Отдаем подкатегории
        "2": list_items,  # Отдаем товары
    }
    current_level_function = levels[current_level]
    await current_level_function(
        call,
        category=category,
        state=state,
        subcategory=subcategory,
        item_id=item_id,
    )


@dp.callback_query_handler(text_contains='show_paint')
async def show_picture(call: CallbackQuery):
    pre_photo = call.data.split(':')[-1]
    new_photo = call.data.split(':')[-2]
    cur_pos = int(call.data.split(':')[2])
    if pre_photo == new_photo:
        await call.answer()
        pass
    else:
        cur_photo = ''
        item = await get_item(int(call.data.split(':')[1]))
        markup = InlineKeyboardMarkup(row_width=5)
        var = int(new_photo)
        position = 0
        if new_photo == '0':
            markup.insert(
                InlineKeyboardButton(
                    text='• ' + str(1) + ' •',
                    callback_data=show_photo.new(item_id=item.id, position=0, photo=0, pre_photo=int(new_photo))
                )
            )
            cur_photo = item.photo.split(',')[0]
            var = int(new_photo) + 1
        else:
            markup.insert(
                InlineKeyboardButton(
                    text=emoji.emojize(':left_arrow:') + str(1),
                    callback_data=show_photo.new(item_id=item.id, position=0, photo=0, pre_photo=int(new_photo))
                )
            )
        if var == 1:
            pass
        elif var == len(item.photo.split(',')) - 3:
            var -= 2
            if var == 0:
                var += 1
        elif var == len(item.photo.split(',')) - 2:
            var -= 3
            if var <= 0:
                var = 1
        elif cur_pos == 1 and var > 1:
            var -= 1
        elif cur_pos == 3 and len(item.photo.split(',')) - 2 - var > 1:
            var -= 1
        elif cur_pos == 2:
            var -= 1
        for i in range(var, len(item.photo.split(',')) - 2):
            position += 1
            if i == int(new_photo):
                k = '• ' + str(i + 1) + ' •'
                cur_photo = item.photo.split(',')[i]
            else:
                k = i + 1
            markup.insert(
                InlineKeyboardButton(
                    text=str(k),
                    callback_data=show_photo.new(item_id=item.id, position=position, photo=i, pre_photo=int(new_photo))
                )
            )
            if i == var + 2:
                break
        if cur_photo == '':
            markup.insert(
                InlineKeyboardButton(
                    text='• ' + str(len(item.photo.split(',')) - 1) + ' •',
                    callback_data=show_photo.new(item_id=item.id, position=4, photo=new_photo,
                                                 pre_photo=int(new_photo))
                )
            )
            cur_photo = item.photo.split(',')[-2]
        else:
            markup.insert(
                InlineKeyboardButton(
                    text=str(len(item.photo.split(',')) - 1) + emoji.emojize(':right_arrow:'),
                    callback_data=show_photo.new(item_id=item.id, position=4,
                                                 photo=len(item.photo.split(',')) - 2, pre_photo=int(new_photo))
                )
            )
        markup.row(
            InlineKeyboardButton(
                text='Купить',
                callback_data=support_item.new(support_from_items='support_from_items',
                                               item_id=item.id),
            )
        )
        if cur_photo != '':
            if cur_photo[-5:] == 'ВИДЕО':
                await call.message.edit_media(media=InputMediaVideo(str(cur_photo)[:-5], caption=f'{item.inscription}'),
                                              reply_markup=markup)
            else:
                await call.message.edit_media(media=InputMediaPhoto(str(cur_photo), f'{item.inscription}'),
                                              reply_markup=markup)
            await call.answer()


@dp.callback_query_handler(text_contains='continue', state=[None, DeleteItem.First])
async def procceed(call: CallbackQuery, state: FSMContext):
    CURRENT_LEVEL = 2
    await call.message.delete()
    calc = call.data.split(':')[-3]
    stop = 0
    items = await get_short_items(call.data.split(':')[-2], call.data.split(':')[-1], calc)
    for item in items:
        markup = InlineKeyboardMarkup(row_width=5)
        if str(await state.get_state()) == 'None':
            for i in range(len(item.photo.split(',')) - 2):
                if i == 0:
                    k = '• ' + str(i + 1) + ' •'
                else:
                    k = i + 1
                if i == 4:
                    break
                markup.insert(
                    InlineKeyboardButton(
                        text=str(k), callback_data=show_photo.new(item_id=item.id, position=i, photo=i, pre_photo=0))
                )
            if len(item.photo.split(',')) != 2:
                markup.insert(
                    InlineKeyboardButton(
                        text=str(len(item.photo.split(',')) - 1) + emoji.emojize(':right_arrow:'),
                        callback_data=show_photo.new(item_id=item.id, position=len(item.photo.split(',')) - 2,
                                                     photo=len(item.photo.split(',')) - 2, pre_photo=0))
                )
            else:
                markup.insert(
                    InlineKeyboardButton(
                        text='• ' + str(len(item.photo.split(',')) - 1) + ' •',
                        callback_data=show_photo.new(item_id=item.id, position=len(item.photo.split(',')) - 2,
                                                     photo=len(item.photo.split(',')) - 2, pre_photo=0))
                )
            markup.row(
                InlineKeyboardButton(
                    text='Купить',
                    callback_data=supports_item.new(support_from_items='support_from_items',
                                                    item_id=item.id),
                )
            )
        else:
            markup.row(
                InlineKeyboardButton(text='Удалить товар',
                                     callback_data=del_callback.new(id=item.id))
            )
        if stop != 5:
            if item.photo.split(',')[0][-5:]=='ВИДЕО':
                await call.message.answer_video(item.photo.split(',')[0][:-5], reply_markup=markup, caption=item.inscription)
            else:
                await call.message.answer_photo(item.photo.split(',')[0], reply_markup=markup, caption=item.inscription)
            await asyncio.sleep(1)
            stop += 1
            if int(calc) * 5 + stop == len(items) + int(calc) * 5:
                x = 1
                if '-' in call.data.split(':')[-2]:
                    x = 2
                markup1 = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=emoji.emojize(':right_arrow_curving_left:') + "Назад",
                            callback_data=make_callback_data(level=CURRENT_LEVEL - x,
                                                             category=call.data.split(':')[-2])),
                    ]
                ]
                )
                await call.message.answer(f'Показано {int(calc) * 5 + stop} из {len(items) + int(calc) * 5} товаров',
                                          reply_markup=markup1)
                break

        else:
            x = 1
            if '-' in call.data.split(':')[-2]:
                x = 2
            markup1 = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=emoji.emojize(':right_arrow_curving_left:') + "Назад",
                        callback_data=make_callback_data(level=CURRENT_LEVEL - x,
                                                         category=call.data.split(':')[-2])),
                ]
            ]
            )
            if int(calc) * 5 != len(items) + int(calc) * 5:
                markup1.insert(
                    InlineKeyboardButton(
                        text=emoji.emojize(':right_arrow_curving_down:') + 'Показать ещё',
                        callback_data=proceed.new(
                            calc=int(calc) + 1,
                            category=call.data.split(':')[-2],
                            subcategory=call.data.split(':')[-1],
                        )
                    )
                )
            await call.message.answer(f'Показано {(int(calc) + 1) * 5} из {len(items) + int(calc) * 5} товаров',
                                      reply_markup=markup1)
            break


@dp.callback_query_handler(text_contains='all', state=[None, DeleteItem.First])
@dp.callback_query_handler(text_contains='proc', state=[None, DeleteItem.First])
async def all_show(call: CallbackQuery, state: FSMContext):
    CURRENT_LEVEL = 2
    await call.message.delete()
    calc = call.data.split(':')[-1]
    items = await get_short_items(call.data.split(':')[-2], 'all', calc)
    stop = 0
    for item in items:
        markup = InlineKeyboardMarkup(row_width=5)
        if str(await state.get_state()) == 'None':
            for i in range(len(item.photo.split(',')) - 2):
                if i == 0:
                    k = '• ' + str(i + 1) + ' •'
                else:
                    k = i + 1
                if i == 4:
                    break
                markup.insert(
                    InlineKeyboardButton(
                        text=str(k), callback_data=show_photo.new(item_id=item.id, position=i, photo=i, pre_photo=0))
                )
            if len(item.photo.split(',')) != 2:
                markup.insert(
                    InlineKeyboardButton(
                        text=str(len(item.photo.split(',')) - 1) + emoji.emojize(':right_arrow:'),
                        callback_data=show_photo.new(item_id=item.id, position=len(item.photo.split(',')) - 2,
                                                     photo=len(item.photo.split(',')) - 2, pre_photo=0))
                )
            else:
                markup.insert(
                    InlineKeyboardButton(
                        text='• ' + str(len(item.photo.split(',')) - 1) + ' •',
                        callback_data=show_photo.new(item_id=item.id, position=len(item.photo.split(',')) - 2,
                                                     photo=len(item.photo.split(',')) - 2, pre_photo=0))
                )
            markup.row(
                InlineKeyboardButton(
                    text='Купить',
                    callback_data=supports_item.new(support_from_items='support_from_items',
                                                    item_id=item.id),
                )
            )
        else:
            markup.row(
                InlineKeyboardButton(text='Удалить товар', callback_data=del_callback.new(id=item.id
                                                                                          ))
            )
        if stop != 5:
            if item.photo.split(',')[0][-5:]=='ВИДЕО':
                await call.message.answer_video(item.photo.split(',')[0][:-5], reply_markup=markup, caption=item.inscription)
            else:
                await call.message.answer_photo(item.photo.split(',')[0], reply_markup=markup, caption=item.inscription)
            await asyncio.sleep(1)
            stop += 1
            if int(calc) * 5 + stop == len(items) + int(calc) * 5:
                markup1 = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=emoji.emojize(':right_arrow_curving_left:') + "Назад",
                            callback_data=make_callback_data(level=CURRENT_LEVEL - 1,
                                                             category=call.data.split(':')[-2])),
                    ]
                ]
                )
                await call.message.answer(f'Показано {int(calc) * 5 + stop} из {len(items) + int(calc) * 5} товаров',
                                          reply_markup=markup1)
                break

        else:
            markup1 = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=emoji.emojize(':right_arrow_curving_left:') + "Назад",
                        callback_data=make_callback_data(level=CURRENT_LEVEL - 1,
                                                         category=call.data.split(':')[-2])),
                ]
            ], row_width=2
            )
            if int(calc) * 5 + stop != len(items) + int(calc) * 5:
                markup1.insert(
                    InlineKeyboardButton(
                        text=emoji.emojize(':right_arrow_curving_down:') + 'Показать ещё',
                        callback_data=all_continue.new(
                            category=call.data.split(':')[-2],
                            calc=int(calc) + 1,
                        )
                    )
                )
            await call.message.answer(f'Показано {(int(calc) + 1) * 5} из {len(items) + int(calc) * 5} товаров',
                                      reply_markup=markup1)
            break
