# Настройка GigaChat для системы тестирования промптов

## 🔧 Получение учетных данных GigaChat

### 1. Регистрация и получение доступа

1. Перейдите на сайт [GigaChat](https://developers.sber.ru/portal/products/gigachat)
2. Зарегистрируйтесь или войдите в личный кабинет
3. Создайте новое приложение в разделе "Мои приложения"
4. Получите **Client Credentials** (client_id и client_secret)

### 2. Формирование строки авторизации

Учетные данные для GigaChat должны быть в формате Base64:

```bash
# Формат: client_id:client_secret
# Пример: abc123:def456
echo -n "your_client_id:your_client_secret" | base64
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните следующие переменные:

```bash
# Учетные данные GigaChat (Base64 строка)
GIGACHAT_CREDENTIALS=your_base64_credentials_here

# Область доступа (обычно GIGACHAT_API_PERS для персонального использования)
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# Проверка SSL сертификатов (рекомендуется false для тестирования)
GIGACHAT_VERIFY_SSL_CERTS=false
```

### 4. Доступные модели GigaChat

Система поддерживает следующие модели:

- **GigaChat** - базовая модель
- **GigaChat-Plus** - улучшенная модель
- **GigaChat-Pro** - профессиональная модель (рекомендуется)

### 5. Проверка настройки

Запустите тест подключения:

```bash
python -c "
import os
from langchain_community.chat_models import GigaChat

# Проверка переменных окружения
credentials = os.getenv('GIGACHAT_CREDENTIALS')
if not credentials:
    print('❌ GIGACHAT_CREDENTIALS не установлен')
    exit(1)

# Создание клиента
try:
    client = GigaChat(
        credentials=credentials,
        scope=os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS'),
        verify_ssl_certs=False
    )
    print('✅ GigaChat настроен успешно')
except Exception as e:
    print(f'❌ Ошибка настройки GigaChat: {e}')
"
```

## 🚨 Важные замечания

### Безопасность
- Никогда не коммитьте файл `.env` в репозиторий
- Храните учетные данные в безопасном месте
- Используйте разные учетные данные для разработки и продакшена

### Лимиты и квоты
- GigaChat имеет лимиты на количество запросов
- Следите за использованием квот в личном кабинете
- При превышении лимитов система автоматически обработает ошибки

### Производительность
- GigaChat-Pro рекомендуется для продакшена
- Настройте параметры `temperature` и `max_tokens` под ваши задачи
- Используйте кэширование для часто используемых запросов

## 🔧 Устранение неполадок

### Ошибка авторизации
```
Решение: Проверьте правильность GIGACHAT_CREDENTIALS в файле .env
```

### Ошибка SSL
```
Решение: Установите GIGACHAT_VERIFY_SSL_CERTS=false
```

### Превышение лимитов
```
Решение: Проверьте квоты в личном кабинете GigaChat
```

### Медленные ответы
```
Решение: Уменьшите max_tokens или используйте более быструю модель
```

## 📞 Поддержка

- 📚 [Документация GigaChat](https://developers.sber.ru/docs/ru/gigachat/overview)
- 💬 [Техническая поддержка](https://developers.sber.ru/help)
- 🐛 [Сообщить об ошибке](https://github.com/your-repo/issues)