import logging
from datetime import datetime
from threading import Thread
import time
import telebot

# Импортируем токен и хранилище
from config import BOT_TOKEN, messages_storage

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаём бота
bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище chat_id для отправки сообщений
user_chats = set()

# Флаг для остановки потока
stop_scheduler = False

# Дни недели
DAYS_RU = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    3: 'thursday',
    4: 'friday',
    5: 'saturday',
    6: 'sunday'
}

DAYS_NAME_RU = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник',
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье'
}


@bot.message_handler(commands=['start'])
def start(message):
    """Команда /start - показывает список доступных команд"""
    user_chats.add(message.chat.id)
    
    help_text = """
🤖 *Добро пожаловать в бот!*

Доступные команды:

*📤 /send* - Отправить текстовое сообщение (текущее значение)
    Используется для отправки заготовленного текста

*⏰ /set_schedule* - Установить время и текст для автоотправки
    Пример: `/set_schedule 10:30 Привет, это автоматическое сообщение`

*📝 /get_scheduled* - Показать текущее запланированное сообщение и время

*✏️ /edit_text* - Изменить текст для отправки
    Пример: `/edit_text Новый текст сообщения`

*🕐 /edit_time* - Изменить время отправки
    Пример: `/edit_time 15:45`

*📅 /week_schedule* - Управление расписанием на неделю

*📋 /status* - Показать статус всех настроек

*ℹ️ /help* - Показать эту справку
    """
    
    bot.reply_to(message, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['set_group'])
def set_group(message):
    """Команда /set_group - Установить ID группы для отправки"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        bot.reply_to(message, 
            "❌ Пожалуйста, укажите ID группы!\n\n"
            "Используйте: `/set_group -1001234567890`\n\n"
            "📖 Как получить ID группы:\n"
            "1. Добавьте бота в группу\n"
            "2. Напишите в группе: `/get_group_id`\n"
            "3. Бот покажет ID группы",
            parse_mode='Markdown')
        return
    
    group_id_str = args[1]
    
    try:
        group_id = int(group_id_str)
        messages_storage['group_id'] = group_id
        
        bot.reply_to(message, 
            f"✅ Группа установлена!\n\n"
            f"📋 ID группы: `{group_id}`",
            parse_mode='Markdown')
        logger.info(f"Группа установлена: {group_id}")
    except ValueError:
        bot.reply_to(message, 
            "❌ Неправильный ID группы!\n\n"
            "ID должен быть числом (например: -1001234567890)",
            parse_mode='Markdown')


@bot.message_handler(commands=['get_group_id'])
def get_group_id(message):
    """Команда /get_group_id - Показать ID текущей группы"""
    bot.send_message(
        chat_id=message.chat.id,
        text=f"🆔 ID этой группы/чата: `{message.chat.id}`\n\n"
             f"Используйте эту команду:\n`/set_group {message.chat.id}`",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['get_group'])
def get_group(message):
    """Команда /get_group - Показать текущую установленную группу"""
    if messages_storage['group_id'] is None:
        bot.reply_to(message, 
            "❌ Группа не установлена!\n\n"
            "Используйте: `/set_group -1001234567890`",
            parse_mode='Markdown')
    else:
        bot.reply_to(message, 
            f"📋 Текущая группа для отправки:\n`{messages_storage['group_id']}`",
            parse_mode='Markdown')


@bot.message_handler(commands=['send'])
def send_message_cmd(message):
    """Команда /send - Отправить заготовленное сообщение"""
    if messages_storage['group_id'] is None:
        bot.reply_to(message, 
            "❌ Группа не установлена!\n\n"
            "Используйте команду `/set_group` чтобы установить группу",
            parse_mode='Markdown')
        return
    
    message_text = messages_storage['send_message_text']
    try:
        bot.send_message(
            chat_id=messages_storage['group_id'],
            text=f"📤 {message_text}",
            parse_mode='Markdown'
        )
        bot.reply_to(message, f"✅ Сообщение отправлено в группу!\n\n{message_text}", 
                     parse_mode='Markdown')
        logger.info(f"Сообщение отправлено в группу {messages_storage['group_id']}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при отправке: {str(e)}", parse_mode='Markdown')
        logger.error(f"Ошибка при отправке: {e}")


@bot.message_handler(commands=['set_schedule'])
def set_schedule(message):
    """Команда /set_schedule - Установить время и текст для автоотправки"""
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        bot.reply_to(message, 
            "❌ Неправильный формат!\n\n"
            "Используйте: `/set_schedule ВремяВ:МИН Текст сообщения`\n\n"
            "Пример: `/set_schedule 10:30 Привет, это автоматическое сообщение`",
            parse_mode='Markdown')
        return
    
    time_str = args[1]
    message_text = args[2]
    
    # Проверка формата времени
    try:
        datetime.strptime(time_str, '%H:%M')
        messages_storage['scheduled_time'] = time_str
        messages_storage['scheduled_text'] = message_text
        
        bot.reply_to(message, 
            f"✅ Запланировано!\n\n"
            f"⏰ Время: {time_str}\n"
            f"📝 Текст: {message_text}",
            parse_mode='Markdown')
        logger.info(f"Расписание установлено: {time_str} - {message_text}")
    except ValueError:
        bot.reply_to(message, 
            "❌ Неправильный формат времени!\n\n"
            "Используйте формат: `ЧЧ:МИН` (например: `10:30`)",
            parse_mode='Markdown')


@bot.message_handler(commands=['get_scheduled'])
def get_scheduled(message):
    """Команда /get_scheduled - Показать текущее запланированное сообщение"""
    scheduled_time = messages_storage['scheduled_time']
    scheduled_text = messages_storage['scheduled_text']
    
    bot.reply_to(message, 
        f"📋 *Текущее расписание:*\n\n"
        f"⏰ Время: `{scheduled_time}`\n"
        f"📝 Текст:\n`{scheduled_text}`",
        parse_mode='Markdown')


@bot.message_handler(commands=['edit_text'])
def edit_text(message):
    """Команда /edit_text - Изменить текст для отправки"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        bot.reply_to(message, 
            "❌ Пожалуйста, укажите новый текст!\n\n"
            "Используйте: `/edit_text Новый текст`",
            parse_mode='Markdown')
        return
    
    new_text = args[1]
    messages_storage['send_message_text'] = new_text
    
    bot.reply_to(message, 
        f"✅ Текст обновлён!\n\n"
        f"📝 Новый текст для `/send`:\n`{new_text}`",
        parse_mode='Markdown')
    logger.info(f"Текст изменён на: {new_text}")


@bot.message_handler(commands=['edit_time'])
def edit_time(message):
    """Команда /edit_time - Изменить время отправки"""
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        bot.reply_to(message, 
            "❌ Пожалуйста, укажите время!\n\n"
            "Используйте: `/edit_time 14:30`",
            parse_mode='Markdown')
        return
    
    time_str = args[1]
    
    # Проверка формата времени
    try:
        datetime.strptime(time_str, '%H:%M')
        messages_storage['scheduled_time'] = time_str
        
        bot.reply_to(message, 
            f"✅ Время обновлено!\n\n"
            f"⏰ Новое время отправки: `{time_str}`",
            parse_mode='Markdown')
        logger.info(f"Время изменено на: {time_str}")
    except ValueError:
        bot.reply_to(message, 
            "❌ Неправильный формат времени!\n\n"
            "Используйте формат: `ЧЧ:МИН` (например: `14:30`)",
            parse_mode='Markdown')


@bot.message_handler(commands=['status'])
def status(message):
    """Команда /status - Показать статус всех настроек"""
    status_text = (
        f"📊 *Статус бота:*\n\n"
        f"📝 *Текст для /send:*\n`{messages_storage['send_message_text']}`\n\n"
        f"⏰ *Время автоотправки:* `{messages_storage['scheduled_time']}`\n"
        f"📤 *Текст при автоотправке:*\n`{messages_storage['scheduled_text']}`"
    )
    bot.reply_to(message, status_text, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_command(message):
    """Команда /help - Показать справку"""
    help_text = """
🤖 *Справка по командам:*

*📤 /send* - Отправить текстовое сообщение
Отправляет текст, установленный через `/edit_text`

*⏰ /set_schedule <ВремяВ:МИН> <Текст>* 
Установить время и текст для автоотправки
Пример: `/set_schedule 10:30 Доброе утро!`

*📝 /get_scheduled* - Показать запланированное сообщение

*✏️ /edit_text <Текст>* - Изменить текст отправки
Пример: `/edit_text Новое сообщение`

*🕐 /edit_time <ВремяВ:МИН>* - Изменить время
Пример: `/edit_time 18:00`

*📅 /week_schedule* - Управление расписанием на неделю

*📋 /status* - Показать все текущие настройки

*ℹ️ /help* - Показать эту справку
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['week_schedule'])
def week_schedule_menu(message):
    """Команда /week_schedule - Управление расписанием на неделю"""
    help_text = """
📅 *Управление расписанием на неделю*

Доступные команды:

*➕ /add_schedule* - Добавить время отправки для дня
Пример: `/add_schedule monday 09:00 Доброе утро!`

*❌ /remove_schedule* - Удалить время отправки
Пример: `/remove_schedule monday 09:00`

*📊 /show_week* - Показать всё расписание на неделю

*🔄 /clear_week* - Очистить всё расписание

Дни недели: monday, tuesday, wednesday, thursday, friday, saturday, sunday
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['add_schedule'])
def add_schedule(message):
    """Команда /add_schedule - Добавить время для дня недели"""
    args = message.text.split(maxsplit=3)
    
    if len(args) < 4:
        bot.reply_to(message, 
            "❌ Неправильный формат!\n\n"
            "Используйте: `/add_schedule день время текст`\n\n"
            "Пример: `/add_schedule monday 09:00 Доброе утро!`\n\n"
            "Дни: monday, tuesday, wednesday, thursday, friday, saturday, sunday",
            parse_mode='Markdown')
        return
    
    day = args[1].lower()
    time_str = args[2]
    schedule_text = args[3]
    
    # Проверка дня
    valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if day not in valid_days:
        bot.reply_to(message, 
            f"❌ Неправильный день недели!\n\n"
            f"Допустимые дни: {', '.join(valid_days)}",
            parse_mode='Markdown')
        return
    
    # Проверка времени
    try:
        datetime.strptime(time_str, '%H:%M')
    except ValueError:
        bot.reply_to(message, 
            "❌ Неправильный формат времени!\n\n"
            "Используйте формат: `ЧЧ:МИН` (например: `10:30`)",
            parse_mode='Markdown')
        return
    
    # Добавляем в расписание
    messages_storage['weekly_schedule'][day][time_str] = schedule_text
    
    bot.reply_to(message, 
        f"✅ Добавлено!\n\n"
        f"📅 День: {DAYS_NAME_RU[day]}\n"
        f"⏰ Время: {time_str}\n"
        f"📝 Текст: {schedule_text}",
        parse_mode='Markdown')
    logger.info(f"Добавлено расписание: {day} {time_str} - {schedule_text}")


@bot.message_handler(commands=['remove_schedule'])
def remove_schedule(message):
    """Команда /remove_schedule - Удалить время для дня"""
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        bot.reply_to(message, 
            "❌ Неправильный формат!\n\n"
            "Используйте: `/remove_schedule день время`\n\n"
            "Пример: `/remove_schedule monday 09:00`",
            parse_mode='Markdown')
        return
    
    day = args[1].lower()
    time_str = args[2]
    
    # Проверка дня
    valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if day not in valid_days:
        bot.reply_to(message, 
            "❌ Неправильный день недели!",
            parse_mode='Markdown')
        return
    
    # Удаляем из расписания
    if time_str in messages_storage['weekly_schedule'][day]:
        del messages_storage['weekly_schedule'][day][time_str]
        bot.reply_to(message, 
            f"✅ Удалено!\n\n"
            f"📅 День: {DAYS_NAME_RU[day]}\n"
            f"⏰ Время: {time_str}",
            parse_mode='Markdown')
        logger.info(f"Удалено расписание: {day} {time_str}")
    else:
        bot.reply_to(message, 
            "❌ Время не найдено для этого дня!",
            parse_mode='Markdown')


@bot.message_handler(commands=['show_week'])
def show_week(message):
    """Команда /show_week - Показать расписание на неделю"""
    schedule_text = "📅 *Расписание на неделю:*\n\n"
    
    has_schedule = False
    for day_eng, day_ru in DAYS_NAME_RU.items():
        day_schedule = messages_storage['weekly_schedule'][day_eng]
        if day_schedule:
            has_schedule = True
            schedule_text += f"*{day_ru}:*\n"
            for time, text in sorted(day_schedule.items()):
                schedule_text += f"  ⏰ {time} - {text}\n"
            schedule_text += "\n"
    
    if not has_schedule:
        schedule_text = "📅 *Расписание пусто!*\n\nДобавьте расписание с помощью `/add_schedule`"
    
    bot.reply_to(message, schedule_text, parse_mode='Markdown')


@bot.message_handler(commands=['clear_week'])
def clear_week(message):
    """Команда /clear_week - Очистить расписание"""
    messages_storage['weekly_schedule'] = {
        'monday': {},
        'tuesday': {},
        'wednesday': {},
        'thursday': {},
        'friday': {},
        'saturday': {},
        'sunday': {}
    }
    bot.reply_to(message, "✅ Расписание очищено!", parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработка текстовых сообщений - только в личном чате"""
    if message.chat.type != 'private':
        return
    
    bot.reply_to(message, 
        "👋 Привет! Используйте команду `/help` чтобы узнать доступные команды.",
        parse_mode='Markdown')


def scheduled_sender():
    """Функция для отправки сообщений по расписанию"""
    global stop_scheduler
    last_sent = {}
    
    while not stop_scheduler:
        group_id = messages_storage['group_id']
        
        # Получаем текущий день и время
        now = datetime.now()
        current_day = DAYS_RU[now.weekday()]
        current_time = now.strftime('%H:%M')
        
        # ОТЛАДКА: Показываем текущее время и расписание каждую минуту
        day_schedule = messages_storage['weekly_schedule'][current_day]
        if now.second == 0:  # Только в начале минуты
            logger.info(f"⏰ Текущее время: {current_time} ({DAYS_NAME_RU[current_day]})")
            logger.info(f"📅 Расписание на сегодня: {day_schedule}")
        
        # Проверяем еженедельное расписание
        if day_schedule and group_id is not None:
            for time_slot, schedule_text in day_schedule.items():
                key = f"{current_day}_{time_slot}"
                
                # Проверяем если время совпадает и мы ещё не отправили в эту минуту
                if time_slot == current_time and key not in last_sent:
                    try:
                        bot.send_message(
                            chat_id=group_id,
                            text=f"🤖 *{schedule_text}*",
                            parse_mode='Markdown'
                        )
                        logger.info(f"✅ ОТПРАВЛЕНО В {current_time}: {schedule_text}")
                        last_sent[key] = True
                    except Exception as e:
                        logger.error(f"❌ Ошибка при отправке: {e}")
                
                # Очищаем память если прошла минута
                elif time_slot != current_time and key in last_sent:
                    del last_sent[key]
        
        time.sleep(1)


def main() -> None:
    """Основная функция"""
    global stop_scheduler
    
    # Запускаем планировщик в отдельном потоке
    scheduler_thread = Thread(target=scheduled_sender, daemon=True)
    scheduler_thread.start()
    
    # Запускаем бота
    logger.info("🚀 Бот запущен...")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
        stop_scheduler = True


if __name__ == '__main__':
    main()
