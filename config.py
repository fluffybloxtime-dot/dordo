import os
import json
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменной окружения или замените напрямую
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Файл для сохранения расписания
SCHEDULE_FILE = 'schedule_data.json'

def load_schedule():
    """Загружает расписание из файла"""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка при загрузке расписания: {e}")
    
    # Возвращаем значения по умолчанию если файл не существует
    return {
        'scheduled_text': 'Ваше первое сообщение',
        'scheduled_time': '09:00',
        'send_message_text': 'Стандартное сообщение',
        'group_id': None,
        'weekly_schedule': {
            'monday': {},
            'tuesday': {},
            'wednesday': {},
            'thursday': {},
            'friday': {},
            'saturday': {},
            'sunday': {}
        }
    }

def save_schedule(data):
    """Сохраняет расписание в файл"""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка при сохранении расписания: {e}")

# Хранилище данных о сообщениях
messages_storage = load_schedule()
