
# mock_github

Test mocking the host used by ghapi

We maintain an in-memory database of releases and files
Pull and issues are a no-op since we just need to set and forget

TODO: exercise all of these APIs using ghapi and requests.
Once that is done we have a drop-in to replace our use of dry-run for GitHub
interactions.
Then we can actually test all of our actions.
