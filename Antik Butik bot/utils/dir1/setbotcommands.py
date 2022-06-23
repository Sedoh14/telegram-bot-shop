from aiogram import types
from aiogram.types import BotCommandScope

from data.config import admins


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Начать диалог"),
        types.BotCommand("help", "Помощь")])


