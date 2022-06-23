from gino import Gino
from gino.schema import GinoSchemaVisitor
from data.config import POSTGRES_URI


db = Gino()


async def create_db():
    await db.set_bind(POSTGRES_URI)
    db.gino: GinoSchemaVisitor
    await db.gino.create_all()
    #await db.gino.drop_all()
