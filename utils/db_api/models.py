from sqlalchemy import (Column, Integer, String, Sequence)
from sqlalchemy import sql
from utils.db_api.database import db


class Item(db.Model):
    __tablename__ = 'item'
    query: sql.Select
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    category_code = Column(String(50))
    category_name = Column(String(50))
    subcategory_code = Column(String(50))
    subcategory_name = Column(String(50))
    name = Column(String(50))
    photo = Column(String(1100))
    inscription=Column(String(700))

    def __repr__(self):
        return f'Товар № "{self.id}" - "{self.name}"'

