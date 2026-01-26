import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменной окружения или замените напрямую
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Хранилище данных о сообщениях
messages_storage = {
    'scheduled_text': 'Ваше первое сообщение',
    'scheduled_time': '09:00',  # Формат: HH:MM
    'send_message_text': 'Стандартное сообщение',
    'group_id': None,  # ID группы для отправки сообщений
    
    # Новое: Расписание по дням недели
    'weekly_schedule': {
        'monday': {},      # Пн
        'tuesday': {},     # Вт
        'wednesday': {},   # Ср
        'thursday': {},    # Чт
        'friday': {},      # Пт
        'saturday': {},    # Сб
        'sunday': {}       # Вс
    }
    # Формат: 'monday': {'09:00': 'Утро', '13:00': 'Обед', '21:00': 'Ночь'}
}
