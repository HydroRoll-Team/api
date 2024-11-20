import asyncio
import aiohttp

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from bs4 import BeautifulSoup


app = FastAPI()

# concurrent limit
semaphore = asyncio.Semaphore(10)

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}

@app.get("/api/github_og")
async def image(request: Request):
    
    repo_url = "https://github.com/HydroRoll-Team/HydroRoll"
    
    repo = request.query_params.get("repo", None)
    if repo:
        repo_url = f"https://github.com/{repo}"
    else:
        repo_url = request.query_params.get("url", repo_url)
    
    conn=aiohttp.TCPConnector(verify_ssl=False)
    async with semaphore:
        async with aiohttp.request('GET',repo_url, connector=conn) as resp:
            if not resp.ok:
                return { "status":resp.status }
            
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            og_image = soup.find("meta", property="og:image")["content"]
            
            if request.headers.get("Content-Type") == "application/json":
                return {"url": og_image}
            else:
                return RedirectResponse(url=og_image)
   