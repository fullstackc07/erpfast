from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from developers.abdusamad.routers import abdusamad_routes
from developers.yusufjon.routes import yusufjon_routers
from developers.yusufjon.utils.jsonToCryllic import dict_to_nested_class
from security.auth import auth_router
from events import *

app = FastAPI(
    title="F9 Project Demo Edition"
)

app.middleware('http')(catch_exceptions_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return "F9 Project"


@app.post("/json_to_krill")
async def krill_konverter(data_dict: dict = Body(...)):

    return dict_to_nested_class(data_dict)


app.include_router(events_router)
app.include_router(abdusamad_routes)
app.include_router(yusufjon_routers)
app.include_router(auth_router)
