from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import router as api_router
from .deps import get_clip_text_model

app = FastAPI()
app.include_router(api_router, prefix="/api")
app.on_event("startup")(get_clip_text_model)  # deprecated, but still works


# these should be serve by server like Nginx, but lets not complicating things
# it's just for demo...
@app.get("/")
async def index() -> FileResponse:
    return FileResponse("static/index.html")


app.mount("/images", StaticFiles(directory="static/val2014"), name="images")
