from uuid import UUID
from datetime import datetime
from typing import Annotated
from fastapi import Depends
from sqlalchemy import table, Integer
from sqlmodel import Field, Session, SQLModel, create_engine, Column, DateTime


class User(SQLModel, table=True):
    uid: UUID = Field(primary_key=True)
    username: str = Field(index=True, primary_key=True)
    password: str = Field(nullable=False)
    nickname: str
    avatar: str
    date_created: datetime = Field(sa_column=Column(DateTime, default=datetime.now()))
    date_modified: datetime = Field(sa_column=Column(DateTime, default=datetime.now(), onupdate=datetime.now()))


class Admin(SQLModel, table=True):
    uid: UUID = Field(primary_key=True)


class Player(SQLModel, table=True):
    uid: UUID = Field(primary_key=True)
    v_hp: float = Field(nullable=False)
    v_lv: int = Field(nullable=False)
    v_exp: float = Field(nullable=False)
    v_atk: float = Field(nullable=False)
    v_def: float = Field(nullable=False)
    v_eva: float = Field(nullable=False)
    v_spd: float = Field(nullable=False)
    v_luk: float = Field(nullable=False)
    date_created: datetime = Field(sa_column=Column(DateTime, default=datetime.now()))
    date_modified: datetime = Field(sa_column=Column(DateTime, default=datetime.now(), onupdate=datetime.now()))


class FailedCounter(SQLModel, table=True):
    uid: UUID = Field(primary_key=True)
    fails: int = Field(sa_column=Column(Integer, nullable=False))


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///storage/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
