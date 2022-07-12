
# mock_github

Test mocking the host used by ghapi

We maintain an in-memory database of releases and files
Pull and issues are a no-op since we just need to set and forget

We have a drop-in to replace our use of dry-run for GitHub
interactions.
Then we can actually test all of our actions.

```bash
uvicorn mock_github.api:app --reload
python mock_github/demo.py
````


start_local_pypi() and start_local_github() should be done
as part of conftest and in the actions when dry run is true
dry run shouldn't make its way to the low-level code by default
dry run shouldn't be touching any servers

so, for unit tests and check_release we need to start these servers
and make sure that our git remote target is a temp directory.

Then, we can test the actual actions and dry run only affects which
servers are used.
