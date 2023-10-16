from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse


from hana.router import router as hana_router
from pages.router import router as pages_router
from search_drv.router import router as search_drv_router
from data_storage.router import router as data_storage_router
from create_prjct_pages.router import router as create_project_router

app = FastAPI(
    title="HANA SCHEMA"
)

# TODO: падает main если нет коннекта к бд

app.include_router(hana_router)
app.include_router(pages_router)
app.include_router(search_drv_router)
app.include_router(data_storage_router)
app.include_router(create_project_router)
app.mount('/static', StaticFiles(directory='pages/static'), name='static')

@app.get('/ping')
def ping():
    response = 'pong'
    return {"response": response, "code": 200}

@app.get('/',  response_class=RedirectResponse)
def start_page(reqest:Request):
    url = '/pages/prjct'
    return url



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


