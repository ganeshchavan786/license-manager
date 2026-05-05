from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import mimetypes
mimetypes.add_type('text/css', '.css')
from app.config import settings
from app.database import create_tables
from app.routers import auth, license, payment, admin

app = FastAPI(
    title="SalaryPay License Server",
    description="Subscription & License management for SalaryPay HRMS",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",
)

# CORS — React frontend साठी
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers include करा
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

# API Routes आधी असावेत
app.include_router(auth.router, prefix="/api")
app.include_router(license.router, prefix="/api")
app.include_router(payment.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# जर 'dist' फोल्डर असेल तर ते serve करा
frontend_path = os.path.join(os.getcwd(), "frontend", "dist")

if os.path.exists(frontend_path):
    # सर्व static files (css, js, images) serve करण्यासाठी
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

    # Client-side routing साठी (React)
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc: Exception):
        if not request.url.path.startswith("/api"):
            return FileResponse(os.path.join(frontend_path, "index.html"))
        return JSONResponse(status_code=404, content={"detail": "Not Found"})


@app.on_event("startup")
def startup():
    create_tables()
    print("✅ SalaryPay License Server started!")
    print(f"📖 API Docs: http://localhost:8661/docs")


@app.get("/")
def root():
    return {
        "app": "SalaryPay License Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
