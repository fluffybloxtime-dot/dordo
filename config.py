import os
import json
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Файл для хранения расписания
SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), 'schedule_data.json')

# Хранилище данных о сообщениях (всё в памяти, как раньше)
messages_storage = {
    'scheduled_text': 'Ваше первое сообщение',
    'scheduled_time': '09:00',
    'send_message_text': 'Стандартное сообщение',
    'group_id': None,
    'daily_schedule': {},
    'one_off': {},
    'weekly_schedule': {
        'monday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        },
        'tuesday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        },
        'wednesday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        },
        'thursday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        },
        'friday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        },
        'saturday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        },
        'sunday': {
            '09:00': 'Доброе утро!',
            '12:00': 'Обеденный перерыв',
            '19:00': 'Добрый вечер!'
        }
    }
}


def load_schedule(defaults: dict) -> dict:
    """Пытается загрузить `schedule_data.json`, возвращает объединённый словарь."""
    try:
        if os.path.exists(SCHEDULE_FILE):
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Объединяем: значения из файла заменяют дефолтные
                merged = defaults.copy()
                merged.update(data)
                # Убедимся, что все ключи существуют
                for k, v in defaults.items():
                    if k not in merged:
                        merged[k] = v
                return merged
    except Exception:
        # При ошибке чтения возвращаем дефолты
        pass

    return defaults


def save_schedule(data: dict) -> None:
    """Сохраняет текущее расписание в `schedule_data.json`."""
    try:
        # Сохраняем только нужные ключи (чтобы не писать секреты и лишние объекты)
        to_save = {
            'scheduled_text': data.get('scheduled_text'),
            'scheduled_time': data.get('scheduled_time'),
            'send_message_text': data.get('send_message_text'),
            'group_id': data.get('group_id'),
            'daily_schedule': data.get('daily_schedule', {}),
            'weekly_schedule': data.get('weekly_schedule', {})
        }
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(to_save, f, ensure_ascii=False, indent=2)
    except Exception:
        # Не фейлим исполнение бота при ошибке записи
        pass


# Попробуем загрузить сохранённые данные (если есть), иначе используем текущие defaults
messages_storage = load_schedule(messages_storage)
