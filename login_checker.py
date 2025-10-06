import asyncio
import requests
import datetime
import time
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

LOGIN_ATTEMPTS = Counter('login_attempts_total', 'Total login attempts', ['status'])
LOGIN_DURATION = Histogram('login_duration_seconds', 'Login request duration')
SERVICE_UP = Gauge('service_up', 'Service status (1=up, 0=down)')

LOGIN_URL = os.getenv('LOGIN_URL')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 8000))

required_vars = {
    'LOGIN_URL': LOGIN_URL,
    'EMAIL': EMAIL,
    'PASSWORD': PASSWORD,
    'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
    'GROUP_ID': GROUP_ID
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    logger.error(f"❌ ОШИБКА: Отсутствуют переменные окружения: {', '.join(missing_vars)}")
    sys.exit(1)

logger.info("✅ Все переменные окружения загружены")
logger.info(f"🔗 Login URL: {LOGIN_URL}")
logger.info(f"📊 Prometheus port: {PROMETHEUS_PORT}")

bot = Bot(token=TELEGRAM_TOKEN)


async def send_telegram(msg):
    try:
        await bot.send_message(chat_id=GROUP_ID, text=msg, parse_mode="Markdown")
        logger.info(f"✅ Сообщение отправлено в {datetime.datetime.now()}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в Telegram: {e}")


async def check_login():
    logger.info(f"🔍 Проверка логина в {datetime.datetime.now()}")
    
    timestamp_start = datetime.datetime.now()
    start_time = time.time()

    payload = {"email": EMAIL, "password": PASSWORD}

    try:
        with LOGIN_DURATION.time():
            response = requests.post(LOGIN_URL, json=payload, timeout=10)
        
        timestamp_end = datetime.datetime.now()
        elapsed = time.time() - start_time

        if response.status_code == 200:
            LOGIN_ATTEMPTS.labels(status='success').inc()
            SERVICE_UP.set(1)
            logger.info(f"✅ Успешный логин (status: 200, время: {elapsed:.2f}s)")
        else:
            LOGIN_ATTEMPTS.labels(status='error').inc()
            SERVICE_UP.set(0)
            
            msg = (
                f"🔴 *Ошибка входа*\n"
                f"⏱ Время начала: `{timestamp_start.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"⏱ Время окончания: `{timestamp_end.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"⏳ Длительность: `{elapsed:.2f} сек.`\n"
                f"⚠️ Статус: {response.status_code}\n"
                f"📄 Ответ сервера:\n```{response.text[:500]}```"
            )
            logger.error(f"❌ Ошибка логина (status: {response.status_code}, время: {elapsed:.2f}s)")
            await send_telegram(msg)

    except requests.exceptions.RequestException as e:
        timestamp_end = datetime.datetime.now()
        elapsed = time.time() - start_time
        LOGIN_ATTEMPTS.labels(status='exception').inc()
        SERVICE_UP.set(0)
        
        msg = (
            f"⚠️ *Ошибка при подключении*\n"
            f"⏱ Время начала: `{timestamp_start.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"⏱ Время окончания: `{timestamp_end.strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"⏳ Длительность: `{elapsed:.2f} сек.`\n"
            f"❌ Ошибка: `{str(e)[:200]}`"
        )
        logger.error(f"⚠️ Ошибка подключения: {e}")
        await send_telegram(msg)
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка в check_login: {e}")
        SERVICE_UP.set(0)


async def main():
    print("=" * 60)
    print("Login Checker Bot запущен")
    print(f"Prometheus метрики на порту {PROMETHEUS_PORT}")
    print(f"Сервер: {LOGIN_URL}")
    print(f"Интервал проверки: 30 минут")
    print("=" * 60)
    
    try:
        start_http_server(PROMETHEUS_PORT)
        logger.info(f"✅ HTTP сервер для метрик запущен на порту {PROMETHEUS_PORT}")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска HTTP сервера: {e}")
        sys.exit(1)
    
    tz = timezone('Asia/Bishkek')
    
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(check_login, 'interval', minutes=30)
    scheduler.start()
    logger.info("✅ Планировщик запущен")
    
    await send_telegram("*Бот запущен и мониторинг начат*\n\n"
                       f"URL: `{LOGIN_URL}`\n"
                       f"Интервал: каждые 30 минут\n")
    
    logger.info("🔄 Выполняю первую проверку...")
    await check_login()
    
    try:
        logger.info("✅ Бот работает. Нажмите Ctrl+C для остановки")
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n🛑 Получен сигнал остановки...")
        scheduler.shutdown()
        await send_telegram("🛑 *Бот остановлен*")
        logger.info("✅ Бот успешно остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в main: {e}")
        await send_telegram(f"🛑 *Бот аварийно остановлен*\nОшибка: `{str(e)[:200]}`")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске: {e}")
        sys.exit(1)