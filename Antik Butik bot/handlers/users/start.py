from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text

from data.config import admins
from keyboards.default.new_keyboard import start_keyboard
from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    if str(message.from_user.id) == str(admins):
        await message.answer(f"Привет, {message.from_user.full_name}!\n"
                             f" Чтобы добавить новый товар нажмите /add_item\n"
                             f" Чтобы удалить товар нажмите /remove_item\n"
                             f' Чтобы добавить нового представителя тех. поддержки нажмите /add_supporter\n'
                             f' Чтобы удалить id представителя тех. поддержки нажмите /remove_supporter',
                             reply_markup=start_keyboard)
    else:
        await message.answer(f"Привет, {message.from_user.full_name}!"
                             f" Я бот Антикъ-Бутикъ. Что вас интересует?", reply_markup=start_keyboard)


@dp.message_handler(Text(equals=['доставка и оплата', 'Доставка и оплата', 'Доставка и оплата📦']))
async def deliver(message: types.Message):
    await message.answer('Бронирование \n'
                         '1. Бесплатное бронирование на любой товар ставится не более, чем на двое суток. '
                         f'При внесении предоплаты сроки бронирования обсуждаются индивидуально с покупателем.\n'
                         f' Оплата\n'
                         f'1. Дистанционная оплата производится на карту СберБанка или Тинькофф.\n'
                         f'2. При покупке товара в магазине оплату можно произвести наличными или через '
                         f'банковский терминал.\n'
                         f'3. На понравившийся Вам товар, можем предоставить любую имеющуюся у нас информацию, '
                         f'а также дополнительные фотографии и видео.\n'
                         f'<b>Все вопросы просьба задавать до момента оплаты. '
                         f'Данная группа товаров обмену и возврату не подлежит.</b>\n'
                         f'Доставка\n'
                         f'1. Посылки отправляются почтой России, курьеровской доставкой СДЭК'
                         f' или "Курьер Сервис Экспресс" с обязательным предоставлением '
                         f'номера трека для отслеживания посылки.\n'
                         f'2. Для отправки требуется ФИО и точный адрес получателя с индексом.\n'
                         f'3. Отправка посылок ежедневно, кроме воскресенья.\n'
                         f' Мы гарантируем качественную и надёжную упаковку.')
