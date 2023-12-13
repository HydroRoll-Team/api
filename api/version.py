from fastapi import FastAPI, HTTPException
import aiohttp

app = FastAPI()


@app.get("/api/version")
async def get_version():
    try:
        hydroroll = await get_target_version("hydroroll")
        iamai = await get_target_version("iamai")
        psi = await get_target_version("psi")
        hydrorollcore = await get_target_version("infini")
        oneroll = await get_target_version("oneroll")
        return hydroroll | iamai | psi | oneroll | hydrorollcore
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


async def get_target_version(pkg_name: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://pypi.org/pypi/{pkg_name}/json") as response:
            try:
                data = await response.json()
                latest_version = data["info"]["version"]
                details = data["releases"][latest_version]
                return {pkg_name: {"version": latest_version, "details": details}}
            except Exception as e:
                return {pkg_name: f"{e}"}
