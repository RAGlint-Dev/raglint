"""
OAuth 2.0 implementation for SSO (Google, GitHub)
"""

import os

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request

# OAuth configuration
oauth = OAuth()

# Google OAuth
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# GitHub OAuth
oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    access_token_url="https://github.com/login/oauth/access_token",
    access_token_params=None,
    authorize_url="https://github.com/login/oauth/authorize",
    authorize_params=None,
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


async def google_login(request: Request):
    """Initiate Google OAuth flow"""
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def google_callback(request: Request):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")

        # user_info contains: email, name, picture
        return user_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")


async def github_login(request: Request):
    """Initiate GitHub OAuth flow"""
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


async def github_callback(request: Request):
    """Handle GitHub OAuth callback"""
    try:
        token = await oauth.github.authorize_access_token(request)

        # Get user info from GitHub API
        resp = await oauth.github.get("user", token=token)
        user_info = resp.json()

        # user_info contains: login (username), email, name, avatar_url
        return user_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
