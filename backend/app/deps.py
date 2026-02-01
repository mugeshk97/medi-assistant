from fastapi import Request


def get_graph(request: Request):
    """
    Dependency to retrieve the compiled graph from the app state.
    """
    return request.app.state.graph
