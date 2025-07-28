# Многоагентная система автоматизации тестирования промптов

## 🚀 Описание проекта

Эта система представляет собой комплексное решение для автоматизации жизненного цикла тестирования промптов с использованием **Gigachain** и **LangChain**. Система предназначена для поддержки инженеров промптов, создавая оптимизированный процесс генерации, анализа, тестирования и редактирования промптов.

## 🏗️ Архитектура системы

### Фазы работы:

1. **🔧 Генерация** - агенты создают высококачественные промпты на основе спецификаций
2. **📋 Анализ** - агенты оценивают промпты по метрикам качества (ясность, релевантность, адаптивность)
3. **🧪 Тестирование** - агенты проводят тесты с различными параметрами (temperature, top-p, max_tokens)
4. **✏️ Редактирование** - агенты оптимизируют промпты на основе обратной связи

### Основные компоненты:

- `agents/` - специализированные агенты для каждой фазы
- `core/` - основная логика и оркестрация
- `models/` - модели данных и схемы
- `api/` - REST API для взаимодействия
- `config/` - конфигурационные файлы
- `tests/` - тесты системы
- `examples/` - примеры использования

## 🛠️ Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируйте .env файл с вашими API ключами
```

### 3. Запуск API сервера

```bash
python run_api.py
```

### 4. Проверка работы

Откройте браузер:
- 📚 API документация: http://localhost:8000/docs
- 🔍 ReDoc: http://localhost:8000/redoc
- ❤️ Проверка здоровья: http://localhost:8000/health

## 📖 Использование

### Через API

#### Полный жизненный цикл промпта

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
  -d '{"specification": "Создай промпт для анализа текста"}'

# Анализ промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/analyze" \
  -d '{"prompt_id": "your-prompt-id"}'

# Тестирование промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/test" \
  -d '{"prompt_id": "your-prompt-id"}'

# Редактирование промпта
curl -X POST "http://localhost:8000/api/v1/lifecycle/edit" \
  -d '{"prompt_id": "your-prompt-id", "feedback": "Улучшить ясность"}'
```

### Через Python код

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

### Запуск примеров

```bash
# Базовый пример
python examples/basic_usage.py

# Запуск тестов
pytest tests/
```

## 🎯 Ключевые возможности

### 🤖 Многоагентная архитектура

- **GeneratorAgent** - создает промпты на основе спецификаций
- **AnalyzerAgent** - оценивает качество по метрикам
- **TesterAgent** - проводит комплексное тестирование
- **EditorAgent** - оптимизирует на основе обратной связи

### 📊 Комплексное тестирование

- Тестирование с различными параметрами (temperature, top-p, max_tokens)
- Метрики качества (точность, релевантность, время ответа)
- Сравнительный анализ нескольких промптов
- Автоматические рекомендации по улучшению

### 🔄 Полный жизненный цикл

- Автоматическая генерация → анализ → тестирование → редактирование
- Сохранение истории всех изменений
- Возможность запуска отдельных фаз
- Интеграция с различными LLM

### 📈 Мониторинг и аналитика

- Детальная статистика по промптам
- Логирование всех операций
- API для получения метрик
- Сравнительные отчеты

## 🏛️ Структура проекта

```
prompt-testing-system/
├── agents/                 # 🤖 Агенты системы
│   ├── base_agent.py      # Базовый класс агента
│   ├── generator_agent.py # Агент-генератор
│   ├── analyzer_agent.py  # Агент-анализатор
│   ├── tester_agent.py    # Агент-тестер
│   └── editor_agent.py    # Агент-редактор
├── core/                  # ⚙️ Основная логика
│   ├── orchestrator.py    # Оркестратор системы
│   ├── agent_manager.py   # Менеджер агентов
│   └── prompt_store.py    # Хранилище данных
├── models/                # 📋 Модели данных
│   ├── prompt_models.py   # Модели промптов
│   ├── agent_models.py    # Модели агентов
│   └── test_models.py     # Модели тестирования
├── api/                   # 🌐 REST API
│   ├── main.py           # Основное приложение
│   └── routes.py         # Роуты API
├── config/               # ⚙️ Конфигурация
│   ├── agent_config.yaml
│   └── test_config.yaml
├── tests/                # 🧪 Тесты
├── examples/             # 📚 Примеры
├── data/                 # 💾 Данные
├── logs/                 # 📝 Логи
├── requirements.txt      # 📦 Зависимости
├── run_api.py           # 🚀 Скрипт запуска
└── SETUP.md             # 📖 Инструкции
```

## 🔧 Конфигурация

### Агенты

Настройка в `config/agent_config.yaml`:

```yaml
agents:
  generator:
    name: "Prompt Generator"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 1000
    system_prompt: "Ты эксперт по созданию промптов..."
    enabled: true
```

### Тестирование

Настройка в `config/test_config.yaml`:

```yaml
default_parameters:
  temperature: [0.1, 0.5, 0.9]
  max_tokens: [100, 500, 1000]
  top_p: [0.1, 0.5, 0.9]
  iterations: 3
```

## 📊 API Endpoints

### Жизненный цикл
- `POST /api/v1/lifecycle/full` - полный цикл
- `POST /api/v1/lifecycle/generate` - генерация
- `POST /api/v1/lifecycle/analyze` - анализ
- `POST /api/v1/lifecycle/test` - тестирование
- `POST /api/v1/lifecycle/edit` - редактирование

### Управление промптами
- `GET /api/v1/prompts` - список промптов
- `GET /api/v1/prompts/{id}` - получение промпта
- `GET /api/v1/prompts/{id}/history` - история промпта
- `DELETE /api/v1/prompts/{id}` - удаление промпта

### Аналитика
- `POST /api/v1/comparative/analyze` - сравнительный анализ
- `GET /api/v1/stats/overview` - статистика системы
- `GET /api/v1/agents/status` - статус агентов

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest tests/

# Запуск с подробным выводом
pytest tests/ -v

# Запуск конкретного теста
pytest tests/test_orchestrator.py -v
```

## 🔍 Мониторинг

### Логи
- `logs/api.log` - логи API сервера
- `logs/system.log` - общие логи системы

### Статистика
```bash
curl "http://localhost:8000/api/v1/stats/overview"
```

## 🚀 Расширение системы

### Добавление нового агента

1. Создайте класс в `agents/`
2. Наследуйтесь от `BaseAgent`
3. Реализуйте методы `_setup_llm()` и `execute()`
4. Добавьте конфигурацию в `config/agent_config.yaml`

### Интеграция с другими LLM

1. Создайте новый класс агента
2. Обновите `_setup_llm()` метод
3. Добавьте переменные окружения

## 📝 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📞 Поддержка

- 📧 Email: support@example.com
- 🐛 Issues: GitHub Issues
- 📖 Документация: `/docs` endpoint

---

**Создано с ❤️ для сообщества инженеров промптов**