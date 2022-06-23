import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji
from aiogram.utils.callback_data import CallbackData

from utils.db_api.db_commands import get_subcategories, count_items, get_categories, get_items

menu_cd = CallbackData("show_menu", "level", "category", "subcategory", "item_id")
show_photo = CallbackData("show_paint", "item_id", 'position', 'photo', 'pre_photo')
supports_item = CallbackData("sup", 'support_from_items', "item_id")
proceed = CallbackData('continue', 'calc', 'category', 'subcategory')
all_in_category = CallbackData('all', 'category', 'calc')
del_callback = CallbackData('delete', 'id')


def make_callback_data(level, category="0", subcategory="0", item_id="0"):
    return menu_cd.new(level=level, category=category, subcategory=subcategory, item_id=item_id)


async def categories_keyboard():
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup(row_width=1)
    categories = await get_categories()
    for category in categories:
        number_of_items = await count_items(category.category_code)
        button_text = f"{category.category_name} ({number_of_items} шт)"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, category=category.category_code)
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    return markup


async def subcategories_keyboard(category, state: FSMContext):
    CURRENT_LEVEL = 1
    cur_state = str(await state.get_state())
    markup = InlineKeyboardMarkup(row_width=1)
    subcategories = await get_subcategories(category)
    if str(subcategories).isdigit():
        return str(subcategories)
    number_of_items1 = await count_items(category_code=category)
    for subcategory in subcategories:
        number_of_items = await count_items(category_code=category, subcategory_code=subcategory.subcategory_code)
        button_text = f"{subcategory.subcategory_name} ({number_of_items} шт)"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1,
                                           category=category, subcategory=subcategory.subcategory_code)
        markup.row(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    if cur_state not in ['NewItem:Category', 'altering', 'NewItem:cat']:
        markup.row(
            InlineKeyboardButton(text=f'Все товары этой категории ({number_of_items1} шт)',
                                 callback_data=all_in_category.new(category=category, calc=0))
        )
    if cur_state not in ['altering', 'NewItem:cat']:
        markup.row(
            InlineKeyboardButton(
                text="Назад",
                callback_data=make_callback_data(level=CURRENT_LEVEL - 1))
        )
    return markup


async def items_keyboard(call, category, subcategory, cur_state):
    CURRENT_LEVEL = 2
    stop = 0
    items = await get_items(category, subcategory)
    length = len(items)
    for item in items:
        markup = InlineKeyboardMarkup(row_width=5)
        if cur_state == 'None':
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
                        callback_data=show_photo.new(item_id=item.id, position=0,
                                                     photo=0, pre_photo=0))
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
                                     callback_data=del_callback.new(id=item.id),
                                     ))
        if stop != 5:
            if item.photo.split(',')[0][-5:]=='ВИДЕО':
                await call.message.answer_video(item.photo.split(',')[0][:-5], reply_markup=markup, caption=item.inscription)
            else:
                await call.message.answer_photo(item.photo.split(',')[0], reply_markup=markup, caption=item.inscription)
            await asyncio.sleep(1)
            stop += 1
            if stop == length:
                x = 1
                if '-' in category:
                    x = 2
                markup4 = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=emoji.emojize(':right_arrow_curving_left:') + "Назад",
                            callback_data=make_callback_data(level=CURRENT_LEVEL - x,
                                                             category=call.data.split(':')[-3]))]])
                await call.message.answer(f'Показано {length} из {length} товаров', reply_markup=markup4)
        else:
            x = 1
            if '-' in category:
                x = 2
            markup1 = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=emoji.emojize(':right_arrow_curving_left:') + "Назад",
                        callback_data=make_callback_data(level=CURRENT_LEVEL - x,
                                                         category=category)),
                    InlineKeyboardButton(
                        text=emoji.emojize(':right_arrow_curving_down:') + 'Показать ещё',
                        callback_data=proceed.new(
                            calc=1,
                            category=category,
                            subcategory=subcategory,
                        )
                    )
                ]
            ]
            )

            await call.message.answer(f'Показано 5 из {length} товаров', reply_markup=markup1)
            break
