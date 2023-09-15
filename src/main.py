from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

from hanadb import get_session
from hana.models import HanaMARA 

from sqlalchemy import select, Insert

from hana.router import router as hana_router
from pages.router import router as pages_router

app = FastAPI(
    title="HANA SCHEMA"
)

# TODO: падает main если нет коннекта к бд

app.include_router(hana_router)
app.include_router(pages_router)
app.mount('/static', StaticFiles(directory='pages/static'), name='static')

@app.get('/ping')
def ping():
    response = 'pong'
    return {"response": response, "code": 200}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8778, reload=True)


