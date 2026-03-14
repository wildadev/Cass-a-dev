from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from cass.database import init_db
from cass.routes import activity, auth, chat, dashboard, feedback, health, onboarding, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Cass — Executive Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")
app.include_router(auth.router, prefix="/auth")
