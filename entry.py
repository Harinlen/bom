from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

from core import conf
from modules import user, admin, template, database, battle, farm


@asynccontextmanager
async def lifespan(app_entry: FastAPI):
    # Load the database.
    database.create_database()
    # Start the app.
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/statics", StaticFiles(directory="statics"), name="statics")
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(farm.router)
app.include_router(battle.router)


@app.get("/")
async def homepage(_: None = Depends(user.must_not_have_uid)):
    return template.render('index.html')


@app.exception_handler(user.UserNotLogin)
async def user_invalid_redirect(request, exc):
    return RedirectResponse(url='/')


@app.exception_handler(user.UserAlreadyLogin)
async def user_already_logged_in_redirect(request, exc):
    return RedirectResponse(url='/user')


@app.exception_handler(404)
async def not_found_redirect(request, exc):
    if not conf.DEBUG:
        return RedirectResponse(url='/user')
    return JSONResponse({'error': '404 Not Found'}, status_code=404)
