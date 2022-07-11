import atexit
import os
import tempfile
from typing import List, Any

from fastapi import FastAPI, UploadFile, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

static_dir = tempfile.TemporaryDirectory()
os.makedirs(str(static_dir), exist_ok=True)
atexit.register(static_dir.cleanup)
app.mount("/static", StaticFiles(directory=static_dir.name), name="static")

global_id = 0
releases = {}


class Asset(BaseModel):
    id: int
    name: str
    content_type: str
    size: int
    state: str = "uploaded"
    url: str
    node_id: str = ""
    download_count: int = 0
    label: str = ""
    uploader: None = None
    browser_download_url: str = ""
    created_at: str = ""
    updated_at: str = ""


class ReleaseModel(BaseModel):
    assets_url: str = ""
    upload_url: str
    tarball_url: str = ""
    zipball_url: str = ""
    created_at: str = ""
    published_at: str = ""
    draft: bool
    body: str = ""
    id: int
    node_id: str = ""
    author: str = ""
    html_url: str
    name: str = ""
    prerelease: bool
    tag_name: str
    target_commitish: str
    assets: List[Asset]
    url: str


class PullRequest(BaseModel):
    number: int = 0
    html_url: str = ""


def create_release_model(owner: str, repo: str, model: dict) -> ReleaseModel:
    global global_id
    id = global_id
    global_id += 1
    url = f"/repos/{owner}/{repo}/releases/{id}"
    html_url = f"/{owner}/{repo}/releases/{model['tag_name']}"
    upload_url = f"/repos/{owner}/{repo}/releases/{id}/assets"
    model = ReleaseModel(tag_name=model['tag_name'], draft=model['draft'], id=id, url=url, html_url=html_url, prerelease=model['prerelease'], target_commitish=model['target_commitish'], assets=[], upload_url=upload_url)
    releases[model.id] = model
    return model


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/repos/{owner}/{repo}/releases")
def list_releases(owner: str, repo: str) -> List[ReleaseModel]:
    """https://docs.github.com/en/rest/releases/releases#list-releases"""
    return list(releases.values())


@app.post("/repos/{owner}/{repo}/releases")
async def create_release(owner: str, repo: str, request: Request) -> ReleaseModel:
    """https://docs.github.com/en/rest/releases/releases#create-a-release"""
    data = await request.json()
    info = request.path_params
    return create_release_model(owner, repo, data)


@app.patch("/repos/{owner}/{repo}/releases/{id}")
async def update_release(owner: str, repo: str, id: int, request: Request) -> ReleaseModel:
    """https://docs.github.com/en/rest/releases/releases#update-a-release"""
    data = await request.json()
    model = releases[id]
    for name, value in data.items():
        setattr(model, name, value)
    return model


@app.post("/repos/{owner}/{repo}/releases/{release_id}/assets")
async def upload_release_assets(owner: str, repo: str, release_id: int, request: Request) -> None:
    """https://docs.github.com/en/rest/releases/assets#upload-a-release-asset"""
    global global_id
    model = releases[release_id]
    asset_id = global_id
    global_id += 1
    name = request.query_params['name']
    with open(f"{static_dir.name}/{asset_id}", "wb") as fid:
        async for chunk in request.stream():
            fid.write(chunk)
    headers = request.headers
    url = f"/static/{asset_id}"
    asset = Asset(id=asset_id, name=name, size=headers['content-length'], url=url, content_type=headers['content-type'])
    model.assets.append(asset)


@app.post("/repos/{owner}/{repo}/pulls")
def create_pull(owner: str, repo: str) -> PullRequest:
    """https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request"""
    return PullRequest()


@app.post("/repos/{owner}/{repo}/issues/{issue_number}/labels")
def add_labels(owner: str, repo: str, issue_number: int) -> BaseModel:
    """https://docs.github.com/en/rest/issues/labels#add-labels-to-an-issue"""
    return BaseModel()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, debug=True)
