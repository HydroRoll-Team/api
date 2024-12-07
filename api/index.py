from fastapi import Depends, FastAPI

from .routers import github_og, version

app = FastAPI()

app.include_router(github_og.router)
app.include_router(version.router)

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}
