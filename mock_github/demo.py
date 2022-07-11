import os
os.environ['GH_HOST'] = "http://127.0.0.1:8000"

from ghapi.core import GhApi

owner = "foo"
repo_name = "bar"
auth = "hi"

gh = GhApi(owner=owner, repo=repo_name, token=auth)
print(list(gh.repos.list_releases()))

here = os.path.dirname(os.path.abspath(__file__))
files = [os.path.join(here, f) for f in os.listdir(here)]
files = [f for f in files if not os.path.isdir(f)]

release = gh.create_release(
        "v1.0.0",
        "main",
        "v1.0.0",
        "body",
        True,
        True,
        files=files,
)

print(release.html_url)


release = gh.repos.update_release(
    release['id'],
    release['tag_name'],
    release['target_commitish'],
    release['name'],
    'body',
    False,
    release['prerelease']
)
assert release.draft == False


pull = gh.pulls.create('title', 'head', 'base', 'body', True, False, None)
gh.issues.add_labels(pull.number, ["documentation"])