from aiogram.dispatcher.filters.state import StatesGroup, State


class NewItem(StatesGroup):
    Category = State()
    Subcategory = State()
    Photo = State()
    Caption = State()
    Confirm = State()
    Category_code = State()
    Subcategory_code = State()
    Category_for_sub=State()
    Another=State()
    Another1 = State()
    Change=State()
    New_photo=State()
    cat=State()
    cat_no_sub=State()


class DeleteItem(StatesGroup):
    First=State()


class Item_suppport(StatesGroup):
    Item_id = State()


class Add_supporter(StatesGroup):
    sup_id = State()


class Remove_supporter(StatesGroup):
    supp_id = State()


class support_states(StatesGroup):
    wait_in_support = State()
