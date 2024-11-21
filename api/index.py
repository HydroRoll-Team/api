from fastapi import FastAPI, Request, Response, status
from fastapi.responses import RedirectResponse

from bs4 import BeautifulSoup

from util.hydrohttp import http_request, HttpMethod, ContentType

app = FastAPI()


@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}


@app.get("/api/github_og")
async def image(request: Request) -> Response:
    repo_url = "https://github.com/HydroRoll-Team/HydroRoll"
    repo = request.query_params.get("repo", None)
    if repo:
        repo_url = f"https://github.com/{repo}"
    else:
        repo_url = request.query_params.get("url", repo_url)

    result = await http_request(url=repo_url,
                                method=HttpMethod.GET,
                                content_type=ContentType.HTML,
                                timeout=10,
                                limit=10,
                                verify_ssl=False)

    if not result.status_code == 200:
        return Response(content=result, status_code=result.status_code)

    text = result.content
    soup = BeautifulSoup(text, "html.parser")
    og_image = soup.find("meta", property="og:image")["content"]

    if request.headers.get("Content-Type") == "application/json":
        return Response({"url": og_image})
    else:
        return RedirectResponse(url=og_image)
