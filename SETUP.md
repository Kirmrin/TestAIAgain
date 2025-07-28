# Инструкции по настройке и запуску

## Быстрый старт

### 1. Установка зависимостей

```bash
# Клонирование репозитория (если еще не сделано)
git clone <repository-url>
cd prompt-testing-system

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование файла .env
# Добавьте ваши учетные данные GigaChat
nano .env
```

### 3. Запуск API сервера

```bash
# Запуск сервера
python run_api.py

# Или напрямую через uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Проверка работы

Откройте браузер и перейдите по адресу:
- API документация: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Проверка здоровья: http://localhost:8000/health

## Детальная настройка

### Конфигурация агентов

Агенты настраиваются в файле `config/agent_config.yaml`:

```yaml
agents:
  generator:
    name: "Prompt Generator"
    model_name: "gpt-4"  # или другая модель
    temperature: 0.7
    max_tokens: 1000
    system_prompt: "Ты эксперт по созданию промптов..."
    enabled: true
```

### Конфигурация тестирования

Параметры тестирования настраиваются в `config/test_config.yaml`:

```yaml
default_parameters:
  temperature: [0.1, 0.5, 0.9]
  max_tokens: [100, 500, 1000]
  top_p: [0.1, 0.5, 0.9]
  iterations: 3
```

### Переменные окружения

Основные переменные в файле `.env`:

```bash
# API ключи
GIGACHAT_CREDENTIALS=your_gigachat_credentials_here
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_VERIFY_SSL_CERTS=false
GIGACHAT_API_KEY=your_gigachat_api_key_here

# Настройки сервера
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=logs/system.log
```

## Использование системы

### 1. Через API

#### Запуск полного жизненного цикла

```bash
curl -X POST "http://localhost:8000/api/v1/lifecycle/full" \
  -H "Content-Type: application/json" \
  -d '{
    "specification": "Создай промпт для анализа тональности текста",
    "context": "Анализ для социальных сетей",
    "requirements": ["Высокая точность", "Быстрое выполнение"],
    "test_parameters": {
      "temperature": [0.1, 0.5, 0.9],
      "max_tokens": [200, 500],
      "test_inputs": ["Я рад!", "Я грущу.", "Обычный день."]
    }
  }'
```

#### Отдельные операции

```bash
# Генерация промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/generate" \
  -H "Content-Type: application/json" \
  -d '{"specification": "Создай промпт для анализа текста"}'

# Анализ промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/analyze" \
  -H "Content-Type: application/json" \
  -d '{"prompt_id": "your-prompt-id"}'

# Тестирование промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/test" \
  -H "Content-Type: application/json" \
  -d '{"prompt_id": "your-prompt-id"}'

# Редактирование промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/edit" \
  -H "Content-Type: application/json" \
  -d '{"prompt_id": "your-prompt-id", "feedback": "Улучшить ясность"}'
```

### 2. Через Python код

```python
import asyncio
from core.orchestrator import PromptLifecycleOrchestrator
from models.test_models import TestParameters

async def main():
    orchestrator = PromptLifecycleOrchestrator()
    
    result = await orchestrator.run_full_lifecycle(
        specification="Создай промпт для анализа тональности",
        test_parameters=TestParameters(
            temperature=[0.1, 0.5, 0.9],
            test_inputs=["Я рад!", "Я грущу."]
        )
    )
    
    print(f"Результат: {result}")

asyncio.run(main())
```

### 3. Запуск примеров

```bash
# Базовый пример
python examples/basic_usage.py

# Запуск тестов
pytest tests/

# Запуск конкретного теста
pytest tests/test_orchestrator.py -v
```

## Структура проекта

```
prompt-testing-system/
├── agents/                 # Агенты системы
│   ├── __init__.py
│   ├── base_agent.py      # Базовый класс агента
│   ├── generator_agent.py # Агент-генератор
│   ├── analyzer_agent.py  # Агент-анализатор
│   ├── tester_agent.py    # Агент-тестер
│   └── editor_agent.py    # Агент-редактор
├── core/                  # Основная логика
│   ├── __init__.py
│   ├── orchestrator.py    # Оркестратор системы
│   ├── agent_manager.py   # Менеджер агентов
│   └── prompt_store.py    # Хранилище данных
├── models/                # Модели данных
│   ├── __init__.py
│   ├── prompt_models.py   # Модели промптов
│   ├── agent_models.py    # Модели агентов
│   └── test_models.py     # Модели тестирования
├── api/                   # REST API
│   ├── __init__.py
│   ├── main.py           # Основное приложение
│   └── routes.py         # Роуты API
├── config/               # Конфигурационные файлы
│   ├── agent_config.yaml
│   └── test_config.yaml
├── tests/                # Тесты
│   └── test_orchestrator.py
├── examples/             # Примеры использования
│   └── basic_usage.py
├── data/                 # Данные (создается автоматически)
├── logs/                 # Логи (создается автоматически)
├── requirements.txt      # Зависимости
├── .env.example         # Пример переменных окружения
├── run_api.py           # Скрипт запуска API
└── README.md            # Документация
```

## Мониторинг и логирование

### Логи

Логи сохраняются в директории `logs/`:
- `api.log` - логи API сервера
- `system.log` - общие логи системы

### Статистика

Получение статистики системы:

```bash
curl "http://localhost:8000/api/v1/stats/overview"
```

### Статус агентов

```bash
curl "http://localhost:8000/api/v1/agents/status"
```

## Устранение неполадок

### Частые проблемы

1. **Ошибка API ключа**
   ```
   Решение: Проверьте правильность GIGACHAT_CREDENTIALS в файле .env
   ```

2. **Ошибка импорта модулей**
   ```
   Решение: Убедитесь, что все зависимости установлены: pip install -r requirements.txt
   ```

3. **Ошибка доступа к порту**
   ```
   Решение: Измените порт в .env файле или остановите процесс, использующий порт 8000
   ```

4. **Ошибки в логах**
   ```
   Решение: Проверьте файлы в директории logs/ для детальной информации
   ```

### Отладка

Для включения режима отладки:

```bash
# В файле .env
DEBUG=true
LOG_LEVEL=DEBUG

# Или при запуске
python run_api.py --debug
```

## Расширение системы

### Добавление нового агента

1. Создайте новый файл в `agents/`
2. Наследуйтесь от `BaseAgent`
3. Реализуйте методы `_setup_llm()` и `execute()`
4. Добавьте конфигурацию в `config/agent_config.yaml`
5. Зарегистрируйте агента в `AgentManager`

### Добавление новых метрик

1. Расширьте модели в `models/test_models.py`
2. Обновите логику вычисления в `TesterAgent`
3. Добавьте новые пороговые значения в `config/test_config.yaml`

### Интеграция с другими LLM

1. Создайте новый класс агента с поддержкой нужной модели
2. Обновите `_setup_llm()` метод
3. Добавьте соответствующие переменные окружения

## Лицензия

MIT License - см. файл LICENSE для деталей.