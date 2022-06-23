from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Контакты'+emoji.emojize(':telephone:')),
            KeyboardButton('Доставка и оплата'+emoji.emojize(':package:'))
        ],
        [
            KeyboardButton('Интересует конкретный товар'),
            KeyboardButton('Интересуют товары из категории')
        ],
    ],
    resize_keyboard=True
)

continue_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Закончить ввод фотографий')
        ],
    ],
    resize_keyboard=True, one_time_keyboard=True, row_width=2
)

all_cancels_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Завершить вызов')
        ]
    ],
    resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Назад в категорию'),
            KeyboardButton('Назад в подкатегорию')
        ]
    ], resize_keyboard=True, row_width=2
)
back1_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton('Назад в категорию')
        ]
    ], resize_keyboard=True, row_width=2
)
