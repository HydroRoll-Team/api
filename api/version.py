from fastapi import FastAPI, HTTPException
import aiohttp

app = FastAPI()


@app.get("/api/version")
async def get_version():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pypi.org/pypi/hydroroll/json") as response:
                data = await response.json()
                return {"HydroRoll": {"version": data["info"]["version"]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
