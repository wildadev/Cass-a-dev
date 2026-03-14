from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from cass.services.google_auth import GoogleAuthService

router = APIRouter()


@router.get("/google")
async def google_auth():
    auth_service = GoogleAuthService()
    url = auth_service.get_auth_url()
    return RedirectResponse(url=url)


@router.get("/google/callback")
async def google_callback(code: str):
    auth_service = GoogleAuthService()
    await auth_service.handle_callback(code)
    return RedirectResponse(url="http://localhost:5173/?auth=success")


@router.get("/google/status")
async def google_status():
    auth_service = GoogleAuthService()
    try:
        creds = await auth_service.get_credentials()
        return {"connected": creds is not None and creds.valid}
    except Exception:
        return {"connected": False}
