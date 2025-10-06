# 🔐 Login Checker Bot

Автоматизированная система мониторинга доступности сервиса входа с интеграцией Telegram уведомлений и Prometheus метрик.

## 📋 Описание

Бот выполняет периодическую проверку работоспособности эндпоинта авторизации, отслеживает метрики производительности и отправляет уведомления в Telegram при возникновении проблем.

## ✨ Основные возможности

- 🔄 Автоматическая проверка каждые 30 минут
- 📊 Сбор метрик Prometheus (количество попыток, время ответа, статус сервиса)
- 💬 Уведомления в Telegram только при ошибках
- 🐳 Полная контейнеризация с Docker Compose
- 📈 Визуализация метрик через Grafana
- 🚀 Автоматический деплой через GitHub Actions

## 🛠 Технологический стек

- **Python 3.11** - основной язык разработки
- **APScheduler** - планировщик задач
- **Prometheus** - система мониторинга
- **Grafana** - визуализация данных
- **Telegram Bot API** - уведомления
- **Docker & Docker Compose** - контейнеризация

## 📦 Структура проекта

```
login-checker/
├── main.py                 # Основной скрипт бота
├── Dockerfile             # Образ для login-checker
├── docker-compose.yml     # Оркестрация сервисов
├── prometheus.yml         # Конфигурация Prometheus
├── requirements.txt       # Python зависимости
├── .env                   # Переменные окружения
└── .github/
    └── workflows/
        └── deploy.yml     # CI/CD пайплайн
```

## ⚙️ Настройка

### Переменные окружения

Создайте файл `.env` со следующими параметрами:

```env
LOGIN_URL=https://your-api.com/login
EMAIL=your-email@example.com
PASSWORD=your-password
TELEGRAM_TOKEN=your-telegram-bot-token
GROUP_ID=your-telegram-group-id
PROMETHEUS_PORT=8000
```

### Получение Telegram токена

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен в `.env`
4. Добавьте бота в вашу группу и получите `GROUP_ID`

## 🚀 Запуск

### Локальный запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
python main.py
```

### Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down
```

## 📊 Доступ к сервисам

После запуска доступны следующие интерфейсы:

| Сервис | URL | Описание |
|--------|-----|----------|
| **Prometheus** | http://localhost:9091 | Метрики и мониторинг |
| **Grafana** | http://localhost:3001 | Дашборды визуализации |
| **Login Checker** | http://localhost:8000 | Эндпоинт метрик |

**Grafana credentials:** admin / admin

## 📈 Метрики Prometheus

Бот экспортирует следующие метрики:

- `login_attempts_total` - общее количество попыток входа (по статусу)
- `login_duration_seconds` - гистограмма времени выполнения запросов
- `service_up` - статус доступности сервиса (1=работает, 0=недоступен)

## 🔔 Уведомления Telegram

Бот отправляет сообщения в следующих случаях:

- ❌ Ошибка авторизации (не 200 статус)
- ⚠️ Проблемы с подключением
- ✅ Запуск/остановка бота

## 🤖 CI/CD с GitHub Actions

Автоматический деплой настроен через GitHub Actions. Необходимо добавить следующие секреты в репозитории:

```
SERVER_HOST - IP адрес сервера
SERVER_USER - имя пользователя
SERVER_PASSWORD - пароль для SSH
LOGIN_URL - URL эндпоинта
EMAIL - email для авторизации
PASSWORD - пароль для авторизации
TELEGRAM_TOKEN - токен Telegram бота
GROUP_ID - ID группы для уведомлений
```

Деплой происходит автоматически при пуше в ветку `main` или `master`.

## 🔧 Настройка Grafana

1. Откройте Grafana по адресу http://localhost:3001
2. Войдите (admin/admin)
3. Добавьте Prometheus как Data Source:
   - URL: `http://prometheus:9090`
   - Access: Server (default)
4. Импортируйте дашборд или создайте свой


---

⭐ Если проект оказался полезным, поставьте звезду на GitHub!
