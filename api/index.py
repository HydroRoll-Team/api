import asyncio
import aiohttp

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse

from bs4 import BeautifulSoup


app = FastAPI()

repo_url = "https://github.com/HydroRoll-Team/HydroRoll"

# concurrent limit
semaphore = asyncio.Semaphore(10)
# timeout after 3s
timeout = aiohttp.ClientTimeout(total=3)


@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}


@app.get("/api/github_og")
async def image(request: Request):
    repo = request.query_params.get("repo", None)
    if repo:
        repo_url = f"https://github.com/{repo}"
    else:
        repo_url = request.query_params.get("url", repo_url)

    conn = aiohttp.TCPConnector(verify_ssl=False)
    async with semaphore:
        try:
            async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
                async with session.get(repo_url) as resp:
                    if not resp.ok:
                        return Response(
                            content={
                                "url": repo_url,
                                "message": "It is not an error from the Hydroroll server, " +
                                            " but the request did not return a 200 response." +
                                            " Please check the URL and try again"
                            },
                            status_code=resp.status)

                    text = await resp.text()
                    soup = BeautifulSoup(text, "html.parser")
                    og_image = soup.find("meta", property="og:image")[
                        "content"]

                    if request.headers.get("Content-Type") == "application/json":
                        return {"url": og_image}
                    else:
                        return RedirectResponse(url=og_image)

        except asyncio.TimeoutError as e:
            return Response(
                content={
                    "url": repo_url,
                    "Exception": "Request timed out",
                },
                status_code=status.HTTP_408_REQUEST_TIMEOUT)

        except aiohttp.ClientConnectorError as e:
            return Response(
                content={
                    "url": repo_url,
                    "Exception": "Request timed out",
                },
                status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                content={
                    "url": repo_url,
                    "Exception": "Request timed out",
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
