from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .routes import router

# Создание FastAPI приложения
app = FastAPI(
    title="Многоагентная система тестирования промптов",
    description="API для автоматизации жизненного цикла тестирования промптов с использованием Gigachain и LangChain",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(router, prefix="/api/v1")

# Логирование
logger.add("logs/api.log", rotation="1 day", retention="7 days", level="INFO")

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("API сервер запущен")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("API сервер остановлен")

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Многоагентная система тестирования промптов",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }