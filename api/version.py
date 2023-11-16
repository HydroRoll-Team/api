from fastapi import FastAPI
import aiohttp

app = FastAPI()


@app.get("/api/version")
async def hello_world():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://pypi.org/pypi/hydroroll/json") as response:
            data = await response.json()
            return {"HydroRoll": {"version": data["info"]["version"]}}
