from typing import Any, Coroutine
from urllib.parse import urlencode
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi_sso.sso.base import DiscoveryDocument, SSOBase
from fastapi_sso.sso.github import GithubSSO

api = APIRouter(prefix="/auth", tags=["Auth"])

XYSSO_CLIENT_ID = "DWs6hKMpI28vKg2raLCtoOItNGxoXYeR8Jno47X5"
XYSSO_CLIENT_SECRET = "dFLJ24FR7y4bRjHTDsU4"
XYSSO_AUTHORIZE_ENDPOINT = "https://sso.xinyuanbest.com/login"
XYSSO_TOKEN_ENDPOINT = "https://sso.xinyuanbest.com:28000/api/v1/xytoken"
XYSSO_PROFILE_ENDPOINT = "https://sso.xinyuanbest.com:28000/api/v1/userinfo"
