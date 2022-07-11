import atexit
import tempfile
from typing import List, Any

from fastapi import FastAPI, UploadFile, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

static_dir = tempfile.TemporaryDirectory()
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
    uploader: None
    browser_download_url: str = ""
    created_at: str = ""
    updated_at: str = ""


class ReleaseModel(BaseModel):
    assets_url: str = ""
    upload_url: str = ""
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
    model = ReleaseModel(tag_name=model['tag_name'], draft=model['draft'], id=id, url=url, html_url=html_url, prerelease=model['prerelease'], target_commitish=model['target_commitish'], assets=[])
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
async def create_release(request: Request) -> ReleaseModel:
    """https://docs.github.com/en/rest/releases/releases#create-a-release"""
    data = await request.json()
    info = request.path_params
    return create_release_model(info['owner'], info['repo'], data)


@app.patch("/repos/{owner}/{repo}/releases/{id}")
async def update_release(request: Request) -> ReleaseModel:
    """https://docs.github.com/en/rest/releases/releases#update-a-release"""
    data = await request.json()
    params = request.path_params
    model = releases[int(params['id'])]
    for name, value in data.items():
        setattr(model, name, value)
    return model


@app.post("/repos/{owner}/{repo}/releases/{release_id}/assets")
def upload_release_assets(owner: str, repo: str, release_id: int, name: str, upload_file: UploadFile):
    """https://docs.github.com/en/rest/releases/assets#upload-a-release-asset"""
    global global_id
    model = releases[release_id]
    asset_id = global_id
    global_id += 1
    with open(f"{static_dir}/{id}", "wb") as fid:
        fid.write(upload_file.file.read())
    url = f"/static/{id}"
    asset = Asset(id=asset_id, name=name, size=len(upload_file.file), url=url, content_type=upload_file.content_type)
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
