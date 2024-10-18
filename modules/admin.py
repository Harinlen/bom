from typing import Union
from uuid import UUID
from fastapi import APIRouter, Cookie, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from modules import user, database, template
from modules.user import UserNotLogin


def must_be_admin(mtc_token: Union[str, None] = Cookie(default=None)) -> UUID:
    uid: UUID | None = user.must_extract_uid(mtc_token)
    try:
        with Session(database.engine) as session:
            admin_check = session.exec(select(database.Admin).where(database.Admin.uid == uid)).first()
            return admin_check.uid
    except Exception as e:
        # Admin is not login, this will bring back to homepage or user page.
        raise UserNotLogin()


router = APIRouter()

@router.get('/admin')
async def page_admin(_: UUID = Depends(must_be_admin)):
    return template.render('admin.html')


class AdminManage(BaseModel):
    username: str


@router.post('/admin_add')
async def admin_add(admin_info: AdminManage,
                    session: database.SessionDep, _: UUID = Depends(must_be_admin)):
    # Check whether UID exist.
    target = session.exec(select(database.User).where(database.User.username == admin_info.username)).first()
    if target is None:
        return {'result': 'No user named {} found in database.'.format(admin_info.username)}
    # Check whether it is already an admin.
    admin_user = session.exec(select(database.Admin).where(database.Admin.uid == target.uid)).first()
    if admin_user is not None:
        return {'result': 'User {} is already admin.'.format(target.username)}
    admin_user = database.Admin(uid=target.uid)
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)
    return {'result': 'ok'}


@router.post('/admin_remove')
async def admin_remove(admin_info: AdminManage,
                       session: database.SessionDep, _: UUID = Depends(must_be_admin)):
    # Check the username is admin.
    target = session.exec(select(database.User).where(database.User.username == admin_info.username)).first()
    if target is None:
        return {'result': 'No user named {} found in database.'.format(admin_info.username)}
    # Check whether it is already an admin.
    admin_user = session.exec(select(database.Admin).where(database.Admin.uid == target.uid)).first()
    if admin_user is None:
        return {'result': 'User {} is not an admin.'.format(target.username)}
    session.delete(admin_user)
    session.commit()
    return {'result': 'ok'}
