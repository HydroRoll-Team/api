from fastapi import FastAPI

app = FastAPI()

@app.get("/api/version")
def hello_world():
    return {"hydroroll": "v0.1.4"}