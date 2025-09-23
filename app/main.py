from fastapi import FastAPI, Request, Response
from app.database import Base, engine
from app.routers import users, items, llm, tasks
from fastapi.middleware.cors import CORSMiddleware

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
    if response and request.url.path.startswith("/tasks"):
        response.headers["Cache-Control"] = "private, max-age=3000"
    return response


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(llm.router, prefix="/llm", tags=["llm"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
