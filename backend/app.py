"""Main FastAPI application for FIN-DASH backend."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import traceback

from config import config
from routers import transactions, categories, accounts, summary, budgets, goals, import_router, debts, reports, recurring, currency, investment, export, analytics, cards, demo
from services.scheduler import scheduler_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    scheduler_service.start()
    yield
    # Shutdown
    scheduler_service.stop()


# Create FastAPI app
app = FastAPI(
    title="FIN-DASH API",
    description="Personal Finance Dashboard API - CSV-based local-first application with automated recurring transactions",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all exceptions and log them."""
    print(f"\n{'='*60}")
    print(f"GLOBAL EXCEPTION HANDLER CAUGHT:")
    print(f"Request URL: {request.url}")
    print(f"Request method: {request.method}")
    print(f"Exception type: {type(exc).__name__}")
    print(f"Exception message: {str(exc)}")
    print(f"Traceback:")
    traceback.print_exc()
    print(f"{'='*60}\n")

    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)}"}
    )

# Include routers
app.include_router(summary.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")
app.include_router(goals.router, prefix="/api")
app.include_router(import_router.router, prefix="/api")
app.include_router(debts.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(recurring.router, prefix="/api")
app.include_router(currency.router, prefix="/api")
app.include_router(investment.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(cards.router, prefix="/api")
app.include_router(demo.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "FIN-DASH API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # Ensure data directory exists
    config.ensure_data_dir()
    
    # Run server
    uvicorn.run(
        "app:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True
    )

