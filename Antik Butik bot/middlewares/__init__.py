from aiogram import Dispatcher
from loader import dp
from .throttling import ThrottlingMiddleware
from .support_middleware import SupportMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())


if __name__ == "middlewares":
    # dp.middlewares.setup(ThrottlingMiddleware())
    dp.middleware.setup(SupportMiddleware())
