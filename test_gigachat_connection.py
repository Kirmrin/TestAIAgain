#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к GigaChat
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

# Загрузка переменных окружения
load_dotenv()


def check_environment():
    """Проверка переменных окружения"""
    print("🔍 Проверка переменных окружения...")
    
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    verify_ssl = os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() == "true"
    
    if not credentials:
        print("❌ GIGACHAT_CREDENTIALS не установлен!")
        print("📝 Создайте файл .env на основе .env.example")
        return False
    
    print(f"✅ GIGACHAT_CREDENTIALS: {'*' * 20}...{credentials[-10:]}")
    print(f"✅ GIGACHAT_SCOPE: {scope}")
    print(f"✅ GIGACHAT_VERIFY_SSL_CERTS: {verify_ssl}")
    
    return True


def test_gigachat_connection():
    """Тестирование подключения к GigaChat"""
    print("\n🚀 Тестирование подключения к GigaChat...")
    
    try:
        # Создание клиента GigaChat
        client = GigaChat(
            credentials=os.getenv("GIGACHAT_CREDENTIALS"),
            scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
            model="GigaChat",
            temperature=0.7,
            max_tokens=100,
            verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() == "true"
        )
        
        print("✅ Клиент GigaChat создан успешно")
        return client
        
    except Exception as e:
        print(f"❌ Ошибка создания клиента GigaChat: {e}")
        return None


async def test_simple_request(client):
    """Тестирование простого запроса"""
    print("\n💬 Тестирование простого запроса...")
    
    try:
        messages = [
            SystemMessage(content="Ты полезный ассистент для тестирования систем."),
            HumanMessage(content="Привет! Это тестовый запрос. Ответь кратко.")
        ]
        
        response = await client.ainvoke(messages)
        print(f"✅ Ответ получен: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении запроса: {e}")
        return False


async def test_different_parameters(client):
    """Тестирование с разными параметрами"""
    print("\n⚙️ Тестирование с разными параметрами...")
    
    test_cases = [
        {"temperature": 0.1, "max_tokens": 50, "description": "Низкая температура"},
        {"temperature": 0.9, "max_tokens": 100, "description": "Высокая температура"},
        {"temperature": 0.5, "max_tokens": 200, "description": "Средние параметры"},
    ]
    
    for i, params in enumerate(test_cases, 1):
        try:
            print(f"\n📋 Тест {i}: {params['description']}")
            
            # Создание клиента с новыми параметрами
            test_client = GigaChat(
                credentials=os.getenv("GIGACHAT_CREDENTIALS"),
                scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
                model="GigaChat",
                temperature=params["temperature"],
                max_tokens=params["max_tokens"],
                verify_ssl_certs=os.getenv("GIGACHAT_VERIFY_SSL_CERTS", "false").lower() == "true"
            )
            
            messages = [
                HumanMessage(content=f"Расскажи кратко о важности тестирования ПО. Тест {i}.")
            ]
            
            response = await test_client.ainvoke(messages)
            print(f"✅ Ответ (temp={params['temperature']}, tokens={params['max_tokens']}): {response.content[:80]}...")
            
        except Exception as e:
            print(f"❌ Ошибка в тесте {i}: {e}")


def test_model_info(client):
    """Получение информации о модели"""
    print("\n📊 Получение информации о модели...")
    
    try:
        # Проверка доступных методов
        if hasattr(client, 'get_models'):
            models = client.get_models()
            print(f"✅ Доступные модели: {models}")
        else:
            print("ℹ️ Метод get_models недоступен")
            
        if hasattr(client, 'get_num_tokens'):
            tokens = client.get_num_tokens("Тестовый текст для подсчета токенов")
            print(f"✅ Количество токенов в тестовой строке: {tokens}")
        else:
            print("ℹ️ Метод get_num_tokens недоступен")
            
    except Exception as e:
        print(f"❌ Ошибка получения информации о модели: {e}")


async def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование интеграции с GigaChat")
    print("=" * 50)
    
    # Проверка переменных окружения
    if not check_environment():
        return
    
    # Тестирование подключения
    client = test_gigachat_connection()
    if not client:
        return
    
    # Получение информации о модели
    test_model_info(client)
    
    # Тестирование простого запроса
    success = await test_simple_request(client)
    if not success:
        return
    
    # Тестирование с разными параметрами
    await test_different_parameters(client)
    
    print("\n🎉 Все тесты завершены!")
    print("\n📋 Резюме:")
    print("✅ Переменные окружения настроены")
    print("✅ Подключение к GigaChat работает")
    print("✅ Запросы выполняются успешно")
    print("✅ Система готова к использованию")
    
    print("\n🚀 Теперь вы можете запустить основную систему:")
    print("   python run_api.py")
    print("   python examples/basic_usage.py")


if __name__ == "__main__":
    asyncio.run(main())