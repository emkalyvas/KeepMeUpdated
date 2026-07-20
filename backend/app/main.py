import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, channels, data_sources, custom_variables, context, notifications, repositories, api_tokens, webhooks
from app.database import engine, Base, SessionLocal
from app.models import Repository
from sqlalchemy.future import select
import os
from app.scheduler import start_scheduler

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB (in production, use Alembic migrations instead)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    default_repo_url = os.environ.get("DEFAULT_PLUGIN_REPO", "https://github.com/emkalyvas/KeepMeUpdated-Plugins")
    async with SessionLocal() as session:
        result = await session.execute(select(Repository).where(Repository.url == default_repo_url))
        repo = result.scalars().first()
        if not repo:
            new_repo = Repository(name="Official Plugins", url=default_repo_url, is_official=True)
            session.add(new_repo)
            await session.commit()
    
    start_scheduler()
    
    yield

app = FastAPI(
    title="KeepMeUpdated API", 
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
)

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
app.include_router(data_sources.router, prefix="/api/data-sources", tags=["data-sources"])
app.include_router(custom_variables.router, prefix="/api/custom-variables", tags=["custom-variables"])
app.include_router(context.router, prefix="/api/context", tags=["context"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
app.include_router(api_tokens.router, prefix="/api/api-tokens", tags=["api-tokens"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
