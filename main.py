
from datetime import datetime
from importlib import import_module

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse


from src.github_util import REPOS, OWNER
from src.github_util import call_issues_endpoint, call_pulls_endpoint

from src.notion_util import DEFAULT_DB, fetch_notion_database

from src.redash_util import q1

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "raptor server v0.1"}

@app.get("/github/issues")
async def fetch_issues(repos: str='', force: int=0):
    """Fetch all issues from pre-defined list of repos.

    List of repos can be modified by setting the optional `repos` query parameter.
    For example: ?repos=server,sync-server

    This list will be added to the pre-defined list of repos.

    The pre-defined list of repos can be overwritten by setting the `force` query parameter.
    For example: ?force=1

    0: False | Do not overwrite pre-defined list
    1: True | Overwrite pre-defined list

    Default is 0.
    """

    accumulator = []
    column_filter = [
        "url", "id", "number", "state", "locked", "title",
        "body", "created_at", "updated_at", "closed_at",
        "assignee", "assignees", "labels", "milestone", "repo",
        "user", "is_pr", "pr_number"
    ]

    list_of_repos = repos.split(',')
    if not force:
        list_of_repos.extend(REPOS)

    for repo in list_of_repos:
        issues = call_issues_endpoint(OWNER, repo)
        accumulator.extend(issues)
    
    df = pd.DataFrame(accumulator)
    csv = df.to_csv(index=False, encoding='utf-8', columns=column_filter)

    return Response(csv)

@app.get("/github/pulls")
async def fetch_pulls(repos: str='', force: int=0):
    """Fetch all pull requests from pre-defined list of repos.

    List of repos can be modified by setting the optional `repos` query parameter.
    For example: ?repos=server,sync-server

    This list will be added to the pre-defined list of repos.

    ---
    The pre-defined list of repos can be overwritten by setting the `force` query parameter.
    For example: ?force=1

    0: False | Do not overwrite pre-defined list
    1: True | Overwrite pre-defined list

    Default is 0.
    """
    accumulator = []
    column_filter = [
        "url", "id", "number", "state", "locked", "title",
        "body", "created_at", "updated_at", "closed_at", "merged_at",
        "assignee", "assignees", "labels", "milestone", "repo", "user"
    ]

    list_of_repos = repos.split(',')
    if not force:
        list_of_repos.extend(REPOS)

    for repo in list_of_repos:
        pull_requests = call_pulls_endpoint(OWNER, repo)
        accumulator.extend(pull_requests)
    
    df = pd.DataFrame(accumulator)
    csv = df.to_csv(index=False, encoding='utf-8', columns=column_filter)
    
    return Response(csv)

@app.get("/notion/database")
async def notion_database(id: str=DEFAULT_DB) -> Response:
    """Fetch all records from a pre-determined Notion Database.
    
    The target Notion Database can be modified by setting the optional `id` parameter.
    """

    database = fetch_notion_database(id)
    df = pd.DataFrame(database)
    csv = df.to_csv(index=False, encoding='utf-8')

    return Response(csv)

@app.get("/redash")
async def redash_info(q: int=None) -> Response:
    """Return a descriptive message for this set of queries: /redash/*
    
    When query parameter `q` is provided, help message belonging to that particular query is returned.
    Example /redash?q=1
    """

    response = {"message": "Run redash-like queries"}
    if q:
        query = import_module(f'src.redash_util.q{q}')
        info = query.info()

        response = JSONResponse(info)
    
    return response

@app.get("/redash/1")
async def run_redash_query(start_date: datetime, end_date: datetime):
    """Run query with id: 1"""

    result = q1.result(start_date, end_date)

    response = Response(result)
    return response
