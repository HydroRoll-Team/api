from fastapi import FastAPI, HTTPException, Query
import aiohttp

app = FastAPI()

@app.get("/api/version")
@app.post("/api/version")
async def get_version(
    project: str = Query(None),
    repo: str = Query(None),
    type: str = Query(None)
):
    try:
        if type == "pypi" and project:
            projects = project.split(";")
            if len(projects) == 1:
                return await get_pypi_version(projects[0])
            results = await get_pypi_versions(projects)
        elif type == "github-releases" and repo:
            repos = repo.split(";")
            if len(repos) == 1:
                return await get_github_release(repos[0])
            results = await get_github_releases(repos)
        elif type == "github-releases-latest" and repo:
            repos = repo.split(";")
            if len(repos) == 1:
                return await get_github_latest_release(repos[0])
            results = await get_github_latest_releases(repos)
        else:
            hydroroll = await get_target_version("hydroroll")
            iamai = await get_target_version("iamai")
            psi = await get_target_version("psi")
            infini = await get_target_version("infini")
            oneroll = await get_target_version("oneroll")
            results = hydroroll | iamai | psi | oneroll | infini
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def get_pypi_version(project: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://pypi.org/pypi/{project}/json") as response:
            return await response.json()

async def get_pypi_versions(projects: list) -> dict:
    async with aiohttp.ClientSession() as session:
        results = {}
        for project in projects:
            async with session.get(f"https://pypi.org/pypi/{project}/json") as response:
                try:
                    data = await response.json()
                    latest_version = data["info"]["version"]
                    details = data["releases"][latest_version]
                    results[project] = {"version": latest_version, "details": details}
                except Exception as e:
                    results[project] = f"{e}"
        return results

async def get_github_release(repo: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/repos/{repo}/releases") as response:
            return await response.json()

async def get_github_releases(repos: list) -> dict:
    async with aiohttp.ClientSession() as session:
        results = {}
        for repo in repos:
            async with session.get(f"https://api.github.com/repos/{repo}/releases") as response:
                try:
                    data = await response.json()
                    results[repo] = data
                except Exception as e:
                    results[repo] = f"{e}"
        return results

async def get_github_latest_release(repo: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/repos/{repo}/releases/latest") as response:
            return await response.json()

async def get_github_latest_releases(repos: list) -> dict:
    async with aiohttp.ClientSession() as session:
        results = {}
        for repo in repos:
            async with session.get(f"https://api.github.com/repos/{repo}/releases/latest") as response:
                try:
                    data = await response.json()
                    results[repo] = data
                except Exception as e:
                    results[repo] = f"{e}"
        return results

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
