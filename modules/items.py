from uuid import UUID, uuid1
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select, col
from modules import database, user, admin, template

router = APIRouter()


@router.get('/')
async def page_items(_: UUID = Depends(user.must_extract_uid)):
    # Provide the page back.
    return template.render('items.html')


@router.get('/list_types')
async def get_list_item_types(session: database.SessionDep,
                              _: UUID = Depends(user.must_extract_uid)):
    # Extract the item type list.
    item_types = session.exec(select(database.ItemType)).all()
    # Convert item types into classes.
    return {'types':[{"id": item.tid, "name": item.name, "icon": item.icon}
                     for item in item_types]}


@router.get('/list')
async def get_list_items(session: database.SessionDep,
                         _: UUID = Depends(user.must_extract_uid)):
    # Extract the item list.
    item_types = session.exec(select(database.Item)).all()
    # Convert item types into classes.
    return {'types': [{"iid": item.iid, "tid": item.tid, "name": item.name, "icon": item.icon, "des": item.description, "op": item.operate}
                      for item in item_types]}


class AddItemType(BaseModel):
    name: str
    icon: str


@router.post('/add_type')
async def add_item_type(item_info: AddItemType, session: database.SessionDep,
                        _: UUID = Depends(admin.must_be_admin)):
    item_type = database.ItemType(tid=uuid1(),
                                  name=item_info.name,
                                  icon=item_info.icon)
    session.add(item_type)
    session.commit()
    session.refresh(item_type)
    return {'result': 'ok'}


class UpdateItemType(BaseModel):
    tid: UUID
    name: str
    icon: str


@router.post('/update_type')
async def update_item_type(item_info: UpdateItemType, session: database.SessionDep,
                           _: UUID = Depends(admin.must_be_admin)):
    item_type = session.exec(select(database.ItemType).where(database.ItemType.tid==item_info.tid)).first()
    if item_type is None:
        return {'result': 'no items'}
    item_type.name = item_info.name
    item_type.icon = item_info.icon
    session.add(item_type)
    session.commit()
    session.refresh(item_type)
    return {'result': 'ok'}


class RemoveItemType(BaseModel):
    tid: UUID


@router.post('/remove_type')
async def remove_item_type(item_info: RemoveItemType, session: database.SessionDep,
                           _: UUID = Depends(admin.must_be_admin)):
    item_type = session.exec(select(database.ItemType).where(database.ItemType.tid==item_info.tid)).first()
    if item_type is None:
        return {'result': 'no item type found'}
    session.delete(item_type)
    session.commit()
    return {'result': 'ok'}


class AddItem(BaseModel):
    tid: UUID
    name: str
    icon: str
    description: str
    operate: str


@router.post('/add')
async def add_item(item_info: AddItem, session: database.SessionDep,
                   _: UUID = Depends(admin.must_be_admin)):
    item = database.Item(iid=uuid1(),
                         tid=item_info.tid,
                         name=item_info.name,
                         icon=item_info.icon,
                         description=item_info.description,
                         operate=item_info.operate)
    session.add(item)
    session.commit()
    session.refresh(item)
    return {'result': 'ok'}


class UpdateItem(BaseModel):
    iid: UUID
    tid: UUID
    name: str
    icon: str
    description: str
    operate: str


@router.post('/update')
async def update_item(item_info: UpdateItem, session: database.SessionDep,
                      _: UUID = Depends(admin.must_be_admin)):
    item = session.exec(select(database.Item).where(database.Item.tid==item_info.tid)).first()
    if item is None:
        return {'result': 'no item found'}
    item.tid = item_info.tid
    item.name = item_info.name
    item.icon = item_info.icon
    item.description = item_info.description
    item.operate = item_info.operate
    session.add(item)
    session.commit()
    session.refresh(item)
    return {'result': 'ok'}


class RemoveItem(BaseModel):
    iid: UUID


@router.post('/remove')
async def remove_item(item_info: RemoveItem, session: database.SessionDep,
                      _: UUID = Depends(admin.must_be_admin)):
    item = session.exec(select(database.Item).where(database.Item.iid==item_info.iid)).first()
    if item is None:
        return {'result': 'no item found'}
    session.delete(item)
    session.commit()
    return {'result': 'ok'}


class ItemSearchUid(BaseModel):
    iid: UUID


@router.post('/search_by_id')
async def search_items(item_info: ItemSearchUid, session: database.SessionDep,
                       _: UUID = Depends(admin.must_be_admin)):
    item = session.exec(select(database.Item).where(database.Item.iid == item_info.iid)).first()
    print(item)
    return []


class ItemSearchName(BaseModel):
    name_part: str


@router.post('/search_by_name')
async def search_items(item_info: ItemSearchName, session: database.SessionDep,
                       _: UUID = Depends(admin.must_be_admin)):
    items = session.exec(select(database.Item).where(col(database.Item.name).contains(item_info.name_part)).limit(10)).all()
    return [{
        'iid': item.iid,
        'tid': item.tid,
        'name': item.name,
        'icon': item.icon,
        'description': item.description,
        'op': item.operate
    } for item in items]


class ItemGive(BaseModel):
    uid: UUID
    iid: UUID
    amount: int


def change_user_item(item_info: ItemGive, session: database.SessionDep):
    item = session.exec(select(database.Backpack).where(
        database.Backpack.uid == item_info.uid).where(
        database.Backpack.iid == item_info.iid)).first()
    if item is None:
        # Create a new record.
        item = database.Backpack(uid=item_info.uid, iid=item_info.iid,
                                 amount=item_info.amount)
    else:
        item.amount = item.amount + item_info.amount
    # Save the item.
    session.add(item)
    session.commit()
    session.refresh(item)


@router.post('/force_give')
async def force_give(item_info: ItemGive, session: database.SessionDep,
                     _: UUID = Depends(admin.must_be_admin)):
    change_user_item(item_info, session)
    return {'result': 'ok'}
