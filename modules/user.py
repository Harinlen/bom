import math
from typing import Union
from datetime import datetime
from uuid import UUID, uuid1
from fastapi import APIRouter, Depends, Cookie
from pydantic import BaseModel
from sqlmodel import Session, select
from modules import template, database, player
from core import conf
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT


class UserNotLogin(Exception):
    pass


class UserAlreadyLogin(Exception):
    pass


def uid_to_token(uid: UUID) -> str:
    crypt_sm4 = CryptSM4(padding_mode=3)
    crypt_sm4.set_key(conf.TOKEN_KEY[:], SM4_ENCRYPT)
    return crypt_sm4.crypt_cbc(conf.TOKEN_IV[:], uid.hex.encode('ascii')).hex()


def token_to_uid(token: str) -> UUID:
    crypt_sm4 = CryptSM4(padding_mode=3)
    crypt_sm4.set_key(conf.TOKEN_KEY[:], SM4_DECRYPT)
    uid_hex = crypt_sm4.crypt_cbc(conf.TOKEN_IV[:], bytearray.fromhex(token))
    return UUID(uid_hex.decode('ascii'))


def extract_uid(mtc_token: Union[str, None] = Cookie(default=None)) -> UUID | None:
    if mtc_token is None:
        return None
    # Try to decrypt the token.
    try:
        token_uid = token_to_uid(mtc_token)
        # Check whether the user existed.
        with Session(database.engine) as session:
            user = session.exec(select(database.User).where(database.User.uid == token_uid)).first()
            return user.uid
    except Exception as e:
       return None


def must_extract_uid(mtc_token: Union[str, None] = Cookie(default=None)) -> UUID:
    uid: UUID | None = extract_uid(mtc_token)
    if uid is None:
        raise UserNotLogin()
    return uid


def must_not_have_uid(mtc_token: Union[str, None] = Cookie(default=None)):
    uid: UUID | None = extract_uid(mtc_token)
    if uid is not None:
        raise UserAlreadyLogin()


router = APIRouter()


@router.get('/register')
async def page_register(_: None = Depends(must_not_have_uid)):
    return template.render('register.html')


class UserRegisterInfo(BaseModel):
    username: str
    password: str
    nickname: str
    avatar: str


@router.post('/register')
async def user_register(user_info: UserRegisterInfo, session: database.SessionDep,
                        _: None = Depends(must_not_have_uid)):
    # Check whether username existed.
    username_check = session.exec(select(database.User).where(database.User.username == user_info.username)).first()
    if username_check is not None:
        return {'result': 'error'}
    # Create user model.
    user = database.User(uid=uuid1(), username=user_info.username,
                         password=user_info.password, nickname=user_info.nickname,
                         avatar=user_info.avatar)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {'result': 'ok'}


@router.get("/login")
async def page_login(_: None = Depends(must_not_have_uid)):
    return template.render('login.html')


class UserLoginInfo(BaseModel):
    username: str
    password: str


@router.post("/login")
async def user_login(user_info: UserLoginInfo, session: database.SessionDep,
                     _: None = Depends(must_not_have_uid)):
    # Check whether username existed.
    username_check = session.exec(
        select(database.User)
        .where(database.User.username == user_info.username)
        .where(database.User.password == user_info.password)
    ).first()
    if not isinstance(username_check, database.User):
        return {'token': ''}
    # If it matches, create the token of the UID.
    return {'token': uid_to_token(username_check.uid)}


@router.get('/user')
async def user_home(session: database.SessionDep, uid: UUID = Depends(must_extract_uid)):
    # Extract user information.
    user = session.exec(select(database.User).where(database.User.uid == uid)).first()
    # Check the player information from user id.
    player_info = player.get_player(user.uid, session)
    # Render the player page.
    return template.render('user.html', {
        # UI settings.
        'time_interval': conf.EXP_UPDATE_SEC + 2,
        # User info.
        'user_name': user.nickname if len(user.nickname) > 0 else user.username,
        'user_id': user.username,
        'player_lv_text': player_info.level_text(),
        'player_avatar': '/statics/default_avatar.png' if len(user.avatar) == 0 else user.avatar,
        'player_exp': int(player_info.exp),
        'player_hp': int(player_info.hp),
        'player_atk': int(player_info.attack),
        'player_def': int(player_info.defense),
        'player_eva': int(player_info.evasion),
        'player_spd': int(player_info.speed),
        'exp_required_min': math.ceil(player_info.level_info()[1]),
        'percent_lost': int(conf.LEVEL_UP_FAILED_RATIO * 100),
        'exp_up_ratio': math.floor(player_info.level_info()[2] * 100)
    })


@router.get('/logout')
async def user_logout():
    return template.render('logout.html')


@router.post('/add_exp')
async def add_exp(session: database.SessionDep, uid: UUID = Depends(must_extract_uid)):
    # Check the player information from user id.
    target: player.Player = player.get_player(uid, session)
    if (datetime.now() - target.last_mod).seconds < conf.EXP_UPDATE_SEC:
        return {}
    # Increase the exp.
    player.add_exp(target, session)
    # Provide the information back.
    return {
        'lv': target.level_text(),
        'hp': target.hp,
        'exp': target.exp,
        'attack': target.attack,
        'defense': target.defense,
        'evasion': target.evasion,
        'speed': target.speed,
        'exp_required_min': math.ceil(target.level_info()[1]),
        'exp_up_ratio': math.floor(target.level_info()[2] * 100)
    }


@router.post('/level_up')
async def add_exp(session: database.SessionDep, uid: UUID = Depends(must_extract_uid)):
    # Check the player information from user id.
    target: player.Player = player.get_player(uid, session)
    # Increase the exp.
    player.level_up(target, session)
    # Provide the information back.
    return {
        'lv': target.level_text(),
        'hp': target.hp,
        'exp': target.exp,
        'attack': target.attack,
        'defense': target.defense,
        'evasion': target.evasion,
        'speed': target.speed,
        'exp_required_min': math.ceil(target.level_info()[1]),
        'exp_up_ratio': math.floor(target.level_info()[2] * 100)
    }


@router.get('/update_info')
async def page_update_info(session: database.SessionDep, uid: UUID = Depends(must_extract_uid)):
    # Check the player information from user id.
    user = session.exec(select(database.User).where(database.User.uid == uid)).first()
    # Update the information.
    return template.render('update_info.html', {
        'user_name': user.nickname if len(user.nickname) > 0 else user.username,
        'user_id': user.username,
        'user_avatar': user.avatar
    })


class UserInfoUpdate(BaseModel):
    nickname: str
    avatar: str


@router.post('/update_info')
async def update_info(user_info: UserInfoUpdate, session: database.SessionDep,
                      uid: UUID = Depends(must_extract_uid)):
    # Check info validation.
    if len(user_info.nickname) == 0:
        return {'result': 'nickname'}
    if len(user_info.avatar) == 0:
        return {'result': 'avatar'}
    # Extract the user object.
    user = session.exec(select(database.User).where(database.User.uid == uid)).first()
    # Update the user info.
    user.nickname = user_info.nickname
    user.avatar = user_info.avatar
    session.add(user)
    session.commit()
    session.refresh(user)
    return {'result': 'ok'}


@router.get('/update_password')
async def page_update_password(session: database.SessionDep, uid: UUID = Depends(must_extract_uid)):
    # Check the player information from user id.
    user = session.exec(select(database.User).where(database.User.uid == uid)).first()
    # Update the information.
    return template.render('update_password.html', {
        'user_name': user.nickname if len(user.nickname) > 0 else user.username,
        'user_id': user.username,
    })


class UserPasswordUpdate(BaseModel):
    password: str
    n_password: str
    dn_password: str


@router.post('/update_password')
async def update_password(password_info: UserPasswordUpdate,
                          session: database.SessionDep, uid: UUID = Depends(must_extract_uid)):
    # Check password validation.
    if password_info.n_password != password_info.dn_password:
        return {'result': 'not match'}
    # Check original is correct.
    user = session.exec(select(database.User).where(database.User.uid == uid).where(
        database.User.password == password_info.password)).first()
    if user is None:
        return {'result': 'invalid'}
    # Change the user password info.
    user.password = password_info.n_password
    session.add(user)
    session.commit()
    session.refresh(user)
    return {'result': 'ok'}
