from fastapi import FastAPI

app = FastAPI()

@app.get("/api/version")
@app.get("/api/versions")
def hello_world():
    return {"version": "v0.1.4"}