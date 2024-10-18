from uuid import UUID, uuid1
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from modules import database, user, admin

router = APIRouter()


@router.get('/list_types')
async def get_list_item_types(session: database.SessionDep,
                              _: UUID = Depends(user.must_extract_uid)):
    # Extract the item type list.
    item_types = session.exec(select(database.ItemType)).all()
    # Convert item types into classes.
    return {'types':[{"id": item.tid, "name": item.name, "icon": item.icon}
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
    return item_type
