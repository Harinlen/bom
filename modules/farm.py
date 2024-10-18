from uuid import UUID
from fastapi import APIRouter, Depends
from modules import template, user


router = APIRouter()

@router.get('/farm')
async def farm(uid: UUID = Depends(user.must_extract_uid)):
    return template.render('farm.html')
