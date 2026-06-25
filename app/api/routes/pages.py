from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import get_current_user_from_cookie


router = APIRouter()


def protected_page(template_path: str, request: Request, db: Session):
    current_user = get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse(url="/", status_code=302)
    return FileResponse(Path(template_path))


@router.get("/", include_in_schema=False)
def landing_page():
    return FileResponse(Path("app/templates/home.html"))


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(Path("app/static/favicon.ico"), media_type="image/x-icon")


@router.get("/courses", include_in_schema=False)
def courses_page():
    return FileResponse(Path("app/templates/courses.html"))


@router.get("/teachers", include_in_schema=False)
def teachers_page():
    return FileResponse(Path("app/templates/teachers.html"))


@router.get("/personalize", include_in_schema=False)
def personalize_page():
    return FileResponse(Path("app/templates/personalize.html"))


@router.get("/app", include_in_schema=False)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse(url="/app/dashboard", status_code=302)


@router.get("/app/dashboard", include_in_schema=False)
def app_dashboard_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_dashboard.html", request, db)


@router.get("/app/summarizer", include_in_schema=False)
def app_summarizer_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_summarizer.html", request, db)


@router.get("/app/explainer", include_in_schema=False)
def app_explainer_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_explainer.html", request, db)


@router.get("/app/audio", include_in_schema=False)
def app_audio_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_audio.html", request, db)


@router.get("/app/quiz", include_in_schema=False)
def app_quiz_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_quiz.html", request, db)


@router.get("/app/slides", include_in_schema=False)
def app_slides_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_slides.html", request, db)


@router.get("/app/saved", include_in_schema=False)
def app_saved_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_saved.html", request, db)


@router.get("/app/customize", include_in_schema=False)
def app_customize_page(request: Request, db: Session = Depends(get_db)):
    return RedirectResponse(url="/app/profile", status_code=302)


@router.get("/app/profile", include_in_schema=False)
def app_profile_page(request: Request, db: Session = Depends(get_db)):
    return protected_page("app/templates/app_profile.html", request, db)
