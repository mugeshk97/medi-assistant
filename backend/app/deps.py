from fastapi import Request, Header, HTTPException, Security
from fastapi.security import APIKeyHeader
from app.settings import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """
    Validate the X-API-Key header against the configured API_KEY setting.
    If API_KEY is not configured, this check is skipped entirely.
    """
    settings = get_settings()
    if settings.API_KEY is None:
        return
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_current_user(
    x_user_id: str = Header(..., description="The ID of the user"),
) -> str:
    """
    Dependency to consistently extract the user_id from the X-User-ID header.
    Validates that the header is present.
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header missing")
    return x_user_id


def get_graph(request: Request):
    """
    Dependency to retrieve the compiled graph from the app state.
    """
    return request.app.state.graph
