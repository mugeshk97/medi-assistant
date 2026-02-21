from fastapi import Request, Header, HTTPException


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
