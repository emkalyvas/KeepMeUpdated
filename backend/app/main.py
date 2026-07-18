import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, channels, notifications, repositories
from app.database import engine, Base
from app.scheduler import start_scheduler

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production, use Alembic migrations instead)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    start_scheduler()
    
    yield

app = FastAPI(title="KeepMeUpdated API", lifespan=lifespan)

# CORS
origins = [
    "http://localhost",
    "http://localhost:5173", # Vue dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
