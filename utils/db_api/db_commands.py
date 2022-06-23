from sqlalchemy import and_
from utils.db_api.models import Item
from utils.db_api.database import db


async def get_categories():
    return await Item.query.distinct(Item.category_name).where(Item.category_code != ')').gino.all()


async def get_subcategories(category):
    if '-' in category:
        category = category.split('-')
        return str(category[1])
    return await Item.query.distinct(Item.subcategory_name).where(Item.category_code == category).gino.all()


async def count_items(category_code, subcategory_code=None):
    conditions = [Item.category_code == category_code]
    if subcategory_code:
        conditions.append(Item.subcategory_code == subcategory_code)
    total = await db.select([db.func.count()]).where(
        and_(*conditions)
    ).gino.scalar()
    return total


async def get_items(category_code, subcategory_code):
    item = await Item.query.where(
        and_(Item.category_code == category_code,
             Item.subcategory_code == subcategory_code)
    ).gino.all()
    return item


async def get_item(id):
    return await Item.query.where(Item.id == id).gino.first()


async def get_the_only_item():
    return await Item.query.where(Item.category_name == ')').gino.first()


async def get_items_in_subcategory(category):
    return await Item.query.distinct(Item.subcategory_code).where(Item.category_code == category).gino.all()


async def get_short_items(category_code, subcategory_code, calc):
    if subcategory_code != 'all':
        item = await Item.query.where(
            and_(Item.category_code == category_code,
                 Item.subcategory_code == subcategory_code)
        ).gino.all()
        for i in range(int(calc) * 5):
            item.pop(0)
    else:
        item = await Item.query.where(
            and_(Item.category_code == category_code)
        ).gino.all()
        for i in range(int(calc) * 5):
            item.pop(0)
    return item


async def updating(value):
    status, result = (
        await Item.update.values(subcategory_name=value)
            .where(Item.category_code == ')')
            .gino.status()
    )


async def updating1(value):
    status, result = (
        await Item.update.values(subcategory_code=value)
            .where(Item.category_code == ')')
            .gino.status()
    )


async def updating2(value):
    status, result = (
        await Item.update.values(name=value)
            .where(Item.category_code == ')')
            .gino.status()
    )


async def delete_item(id):
    await Item.delete.where(Item.id == id).gino.status()
