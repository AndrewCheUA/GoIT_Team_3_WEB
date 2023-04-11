from fastapi import APIRouter, Request, Response, status, HTTPException
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/docs", tags=["Documents"])
templates = Jinja2Templates(directory="docs/build/html")


# Create a route that serves the index.html file
@router.get("/")
async def read_docs(request: Request) -> Response:
    """
    Returns the Sphinx documentation index.html file.

    :param request: Request: The incoming request.
    :return: Response: The response containing the index.html file.
    """
    docs_dir = Path("docs/build/html")
    index_path = docs_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documentation not found.")
    return templates.TemplateResponse("index.html", {"request": request})
