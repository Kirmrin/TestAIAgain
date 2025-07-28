#!/usr/bin/env python3
"""
Скрипт для запуска API сервера многоагентной системы тестирования промптов
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv
from loguru import logger

# Добавление корневой директории в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загрузка переменных окружения
load_dotenv()

def main():
    """Основная функция запуска API сервера"""
    
    # Проверка наличия API ключа
    if not (os.getenv("GIGACHAT_TOKEN") or os.getenv("GIGACHAT_CREDENTIALS")):
        logger.warning("GIGACHAT_TOKEN не установлен!")
        logger.info("Создайте файл .env и добавьте ваш токен доступа к GigaChat в переменную GIGACHAT_TOKEN")
        logger.info("Для тестирования можно использовать демо-режим либо токен из песочницы Сбера")
    
    # Настройки сервера
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    # Создание директорий для логов
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    logger.info(f"🚀 Запуск API сервера на {host}:{port}")
    logger.info(f"📚 Документация API: http://{host}:{port}/docs")
    logger.info(f"🔍 ReDoc: http://{host}:{port}/redoc")
    
    # Запуск сервера
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )

if __name__ == "__main__":
    main()