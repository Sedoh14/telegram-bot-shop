from data.config import admins
from utils.db_api.database import create_db
from utils.dir1.setbotcommands import set_default_commands


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)
    await set_default_commands(dp)
    # await asyncio.sleep(10)
    await create_db()
    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup)
