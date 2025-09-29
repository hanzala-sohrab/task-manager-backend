from fastapi import FastAPI, Request, Response
from app.database import Base, engine
from app.routers import users, items, tasks, llm
from fastapi.middleware.cors import CORSMiddleware
import hashlib

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response: Response = await call_next(request)
    if not request.url.path.startswith("/tasks"):
        return response
    # Read response body (StreamingResponse has .body_iterator)
    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    # Create a fresh Response with captured body
    new_response = Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),  # copy original headers
        media_type=response.media_type,
    )

    # Generate ETag based on response content
    etag = hashlib.md5(body).hexdigest()
    new_response.headers["ETag"] = etag

    # Check if the ETag matches the If-None-Match header
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match == etag:
        return Response(status_code=304)

    # Set Cache-Control header for 5 minutes
    new_response.headers["Cache-Control"] = "private, max-age=300"

    return new_response


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(llm.router, prefix="/llm", tags=["llm"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
