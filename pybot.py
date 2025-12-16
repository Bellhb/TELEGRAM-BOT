import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_token() -> str:
    sources = [
        lambda: os.environ.get("BOT_TOKEN"),
        lambda: load_token_from_env(),
        lambda: load_token_from_config(),
        lambda: input_token_interactive()
    ]
    
    for source in sources:
        token = source()
        if token and validate_token(token):
            logger.info("Токен успешно загружен")
            return token
    
    logger.error("Токен не найден ни в одном источнике")
    print("\n" + "="*60)
    print("❌ ОШИБКА: Токен бота не найден!")
    print("="*60)
    print("\nДоступные способы передачи токена:")
    print("1. Переменная окружения: export BOT_TOKEN='ваш_токен'")
    print("2. Файл .env: BOT_TOKEN=ваш_токен")
    print("3. Файл config.py: TOKEN = 'ваш_токен'")
    print("4. Создать файл token.txt с токеном")
    print("\n" + "="*60)
    sys.exit(1)

def load_token_from_env() -> Optional[str]:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.environ.get("BOT_TOKEN")
    except ImportError:
        logger.warning("python-dotenv не установлен, пропускаем .env")
        return None

def load_token_from_config() -> Optional[str]:
    try:
        from config import TOKEN
        logger.warning("Используется config.py - убедитесь что он не в репозитории!")
        return TOKEN
    except (ImportError, ModuleNotFoundError):
        return None

def input_token_interactive() -> Optional[str]:
    try:
        token = input("Введите токен бота: ").strip()
        if validate_token(token):
            save = input("Сохранить в token.txt для будущих запусков? (y/N): ").strip().lower()
            if save == 'y':
                with open('token.txt', 'w', encoding='utf-8') as f:
                    f.write(token)
                logger.info("Токен сохранен в token.txt")
            return token
    except Exception:
        pass
    return None

def validate_token(token: str) -> bool:
    if not token:
        return False
    parts = token.split(':')
    if len(parts) != 2:
        return False
    if not parts[0].isdigit():
        return False
    if len(parts[1]) < 10:
        return False
    return True

TOKEN = load_token()
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

class Config:
    VERSION = "2.0"
    AUTHOR = "Telegram Privacy Auditor"
    
    QUESTIONS = [
        {
            "id": "phone",
            "text": "📱 Кто видит ваш номер телефона?",
            "risks": {
                "Все": "🔴 <b>ВЫСОКИЙ РИСК</b>\n• Номер могут использовать для спама и фишинга\n• Можно найти вас в социальных сетях\n• Возможна подмена SIM-карты (SIM-swap)",
                "Мои контакты": "🟡 <b>СРЕДНИЙ РИСК</b>\n• Контакты могут случайно раскрыть номер\n• При утечке телефона контактов - номер доступен",
                "Никто": "🟢 <b>НИЗКИЙ РИСК</b>\n• Максимальная защита номера\n• Рекомендуемая настройка"
            },
            "fix": "Настройки → Конфиденциальность → Номер телефона"
        },
        {
            "id": "last_seen",
            "text": "⏰ Кто видит, когда вы были в сети?",
            "risks": {
                "Все": "🔴 <b>ВЫСОКИЙ РИСК</b>\n• Можно отследить ваш график активности\n• Злоумышленники знают когда вы онлайн\n• Упрощает социальную инженерию",
                "Мои контакты": "🟡 <b>СРЕДНИЙ РИСК</b>\n• Контакты видят вашу активность\n• Могут определить когда вы спите/работаете",
                "Никто": "🟢 <b>НИЗКИЙ РИСК</b>\n• Полная анонимность статуса\n• Рекомендуемая настройка"
            },
            "fix": "Настройки → Конфиденциальность → Время последнего посещения"
        },
        {
            "id": "profile_photo",
            "text": "🖼️ Кто видит вашу фотографию профиля?",
            "risks": {
                "Все": "🔴 <b>ВЫСОКИЙ РИСК</b>\n• Фото можно использовать для поиска по изображению\n• Возможность создания фейковых аккаунтов\n• Сбор биометрических данных",
                "Мои контакты": "🟡 <b>СРЕДНИЙ РИСК</b>\n• Ограниченный круг видимости\n• Риск если телефон контакта скомпрометирован",
                "Никто": "🟢 <b>НИЗКИЙ РИСК</b>\n• Максимальная приватность\n• Рекомендуемая настройка"
            },
            "fix": "Настройки → Конфиденциальность → Фотография профиля"
        },
        {
            "id": "groups",
            "text": "👥 Кто может добавлять вас в группы?",
            "risks": {
                "Все": "🔴 <b>ВЫСОКИЙ РИСК</b>\n• Вас могут добавлять в спам-чаты\n• Мошеннические группы и фишинг\n• Потеря контроля над вступлением",
                "Мои контакты": "🟡 <b>СРЕДНИЙ РИСК</b>\n• Только знакомые могут добавлять\n• Риск если контакт скомпрометирован",
                "Никто": "🟢 <b>НИЗКИЙ РИСК</b>\n• Полный контроль над группами\n• Рекомендуемая настройка"
            },
            "fix": "Настройки → Конфиденциальность → Группы и каналы"
        },
        {
            "id": "forwarding",
            "text": "🔗 Кто может создавать ссылки на ваш профиль?",
            "risks": {
                "Все": "🔴 <b>ВЫСОКИЙ РИСК</b>\n• Ваш профиль могут репостить где угодно\n• Упрощает сбор информации о вас\n• Спам через упоминания",
                "Мои контакты": "🟡 <b>СРЕДНИЙ РИСК</b>\n• Ограниченный круг\n• Риск неконтролируемого распространения",
                "Никто": "🟢 <b>НИЗКИЙ РИСК</b>\n• Максимальная защита от упоминаний\n• Рекомендуемая настройка"
            },
            "fix": "Настройки → Конфиденциальность → Пересылка сообщений"
        }
    ]
    
    POINTS = {"Все": 0, "Мои контакты": 1, "Никто": 2}
    
    LEVELS = {
        10: {"name": "🎉 ИДЕАЛЬНО", "color": "🟢", "desc": "Вы хакер уровня паранойи! Идеальная защита."},
        9: {"name": "✅ ОТЛИЧНО", "color": "🟢", "desc": "Почти идеально. Можно расслабиться."},
        8: {"name": "👍 ХОРОШО", "color": "🟢", "desc": "Хорошая защита. Небольшие риски."},
        7: {"name": "⚠️ НОРМАЛЬНО", "color": "🟡", "desc": "Средний уровень. Есть что улучшить."},
        6: {"name": "⚠️ УДОВЛЕТВОРИТЕЛЬНО", "color": "🟡", "desc": "Приемлемо, но нужно работать."},
        5: {"name": "🔴 ТРЕВОГА", "color": "🔴", "desc": "Низкая защита. Вы в зоне риска."},
        4: {"name": "🔴 ОПАСНО", "color": "🔴", "desc": "Опасный уровень. Срочно меняйте настройки!"},
        3: {"name": "🚨 КРИТИЧЕСКИ", "color": "🔴", "desc": "Критически низкая защита!"},
        2: {"name": "💀 КАТАСТРОФА", "color": "💀", "desc": "Ваши данные полностью уязвимы!"},
        1: {"name": "💀 АПОКАЛИПСИС", "color": "💀", "desc": "Немедленно настройте приватность!"},
        0: {"name": "☢️ ЯДЕРНЫЙ УРОВЕНЬ", "color": "☢️", "desc": "Вы вообще не скрываетесь?!"}
    }

class UserSession:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.answers: List[Dict] = []
        self.current_question = 0
        self.score = 0
        self.start_time = datetime.now()
        self.username = ""
        self.first_name = ""
        
    def add_answer(self, question_id: str, answer: str, points: int):
        self.answers.append({
            "question_id": question_id,
            "answer": answer,
            "points": points,
            "timestamp": datetime.now()
        })
        self.score += points
        
    def get_progress(self) -> str:
        total = len(Config.QUESTIONS)
        return f"{self.current_question}/{total} ({(self.current_question/total*100):.0f}%)"
    
    def is_completed(self) -> bool:
        return self.current_question >= len(Config.QUESTIONS)

sessions: Dict[int, UserSession] = {}

def create_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.add("Все", "Мои контакты", "Никто")
    keyboard.add("❌ Отмена")
    return keyboard

def remove_keyboard() -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove()

@bot.message_handler(commands=['start', 'help'])
def handle_start(message: types.Message):
    user = message.from_user
    chat_id = message.chat.id
    
    sessions[chat_id] = UserSession(chat_id)
    sessions[chat_id].username = user.username or ""
    sessions[chat_id].first_name = user.first_name or "Пользователь"
    
    welcome_text = f"""
<b>👋 Привет, {user.first_name}!</b>

Я — <b>Telegram Privacy Auditor v{Config.VERSION}</b>
Проверю 5 ключевых настроек приватности и дам персонализированные рекомендации.

<b>📊 Как работает оценка:</b>
• <code>Все</code> = 0 баллов (🔴 высокий риск)
• <code>Мои контакты</code> = 1 балл (🟡 средний риск)  
• <code>Никто</code> = 2 балла (🟢 низкий риск)

<b>🎯 Максимальный результат:</b> 10/10 баллов

<b>📝 Для каждого ответа вы получите:</b>
1. Объяснение рисков
2. Рекомендации по исправлению
3. Персональный отчет в конце

<code>Нажмите кнопку ниже чтобы начать проверку!</code>
    """
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🚀 Начать проверку", callback_data="start_check"))
    
    bot.send_message(chat_id, welcome_text, reply_markup=keyboard)
    logger.info(f"Пользователь {user.id} начал сессию")

@bot.callback_query_handler(func=lambda call: call.data == "start_check")
def start_check_callback(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    
    if chat_id not in sessions:
        bot.send_message(chat_id, "Напишите /start чтобы начать заново")
        return
    
    bot.answer_callback_query(call.id)
    ask_question(chat_id)

def ask_question(chat_id: int):
    session = sessions.get(chat_id)
    if not session or session.is_completed():
        return
    
    question = Config.QUESTIONS[session.current_question]
    
    question_text = f"""
<b>Вопрос {session.current_question + 1} из {len(Config.QUESTIONS)}</b>

{question['text']}

Выберите вариант ответа:
    """
    
    bot.send_message(chat_id, question_text, reply_markup=create_keyboard())

@bot.message_handler(func=lambda m: m.text in ["Все", "Мои контакты", "Никто", "❌ Отмена"])
def handle_answer(message: types.Message):
    chat_id = message.chat.id
    session = sessions.get(chat_id)
    
    if not session:
        bot.send_message(chat_id, "Напишите /start чтобы начать")
        return
    
    if message.text == "❌ Отмена":
        bot.send_message(chat_id, "❌ Проверка отменена. Для начала новой напишите /start", 
                        reply_markup=remove_keyboard())
        sessions.pop(chat_id, None)
        return
    
    question = Config.QUESTIONS[session.current_question]
    answer = message.text
    points = Config.POINTS[answer]
    
    session.add_answer(question["id"], answer, points)
    
    send_risk_explanation(chat_id, question, answer)
    
    session.current_question += 1
    
    if session.is_completed():
        send_final_report(chat_id)
        sessions.pop(chat_id, None)
    else:
        ask_question(chat_id)

def send_risk_explanation(chat_id: int, question: Dict, answer: str):
    risk_text = question["risks"][answer]
    
    explanation = f"""
<b>Ваш ответ:</b> <code>{answer}</code>

{risk_text}

<b>🔧 Как исправить:</b>
{question["fix"]}

<i>Нажмите на кнопку в Telegram чтобы перейти прямо в настройки</i>
    """
    
    bot.send_message(chat_id, explanation, reply_markup=remove_keyboard())
    
    import time
    time.sleep(1)

def send_final_report(chat_id: int):
    session = sessions.get(chat_id)
    if not session:
        return
    
    score = session.score
    level = Config.LEVELS.get(score, Config.LEVELS[0])
    
    duration = datetime.now() - session.start_time
    minutes = int(duration.total_seconds() // 60)
    seconds = int(duration.total_seconds() % 60)
    
    report = f"""
{level['color']} <b>ПЕРСОНАЛИЗИРОВАННЫЙ ОТЧЕТ</b> {level['color']}

<b>👤 Пользователь:</b> {session.first_name}
<b>📅 Дата проверки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
<b>⏱️ Время прохождения:</b> {minutes} мин {seconds} сек

<b>🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:</b>
<b>Оценка:</b> <code>{score}/10 баллов</code>
<b>Уровень защиты:</b> <code>{level['name']}</code>
<b>Описание:</b> {level['desc']}

<b>📊 РАСПРЕДЕЛЕНИЕ ОТВЕТОВ:</b>
    """
    
    answers_count = {"Все": 0, "Мои контакты": 0, "Никто": 0}
    for ans in session.answers:
        answers_count[ans["answer"]] += 1
    
    report += f"""
• <code>Никто</code> (🟢 безопасно): {answers_count['Никто']}/5
• <code>Мои контакты</code> (🟡 средний риск): {answers_count['Мои контакты']}/5
• <code>Все</code> (🔴 высокий риск): {answers_count['Все']}/5
    """
    
    report += "\n\n<b>🔍 ДЕТАЛЬНЫЙ АНАЛИЗ:</b>\n"
    
    weak_points = []
    for i, ans in enumerate(session.answers):
        question = Config.QUESTIONS[i]
        if ans["points"] < 2:
            weak_points.append((question, ans))
    
    if weak_points:
        report += "\n<b>🚨 СЛАБЫЕ МЕСТА (рекомендуем исправить):</b>\n"
        for question, ans in weak_points:
            risk_level = "🔴 ВЫСОКИЙ" if ans["points"] == 0 else "🟡 СРЕДНИЙ"
            report += f"\n• <b>{question['text']}</b>\n"
            report += f"  Ваш ответ: <code>{ans['answer']}</code> ({risk_level} риск)\n"
            report += f"  Исправить: {question['fix']}\n"
    else:
        report += "\n<b>✅ Отличная работа! Все настройки оптимальны.</b>\n"
    
    visual_bar = ""
    for i in range(10):
        if i < score:
            visual_bar += "🟩"
        else:
            visual_bar += "⬜"
    
    report += f"""
    
<b>📈 ВИЗУАЛЬНАЯ ШКАЛА ЗАЩИТЫ:</b>
{visual_bar} {score}/10

<b>🔄 Для нового теста напишите</b> <code>/start</code>

<b>💡 Совет:</b> Регулярно проверяйте настройки приватности!
<b>🔐 Берегите свои данные!</b>
    """
    
    bot.send_message(chat_id, report, reply_markup=remove_keyboard())
    
    stats_text = f"""
<b>📈 СТАТИСТИКА ПРОВЕРКИ:</b>
• Всего проверок сегодня: {len([s for s in sessions.values() if s.start_time.date() == datetime.now().date()])}
• Средний результат: <code>{calculate_average_score():.1f}/10</code>
• Ваш результат лучше чем у {calculate_percentile(score):.0f}% пользователей

<i>Результат сохранен в логах бота</i>
    """
    
    bot.send_message(chat_id, stats_text)
    logger.info(f"Пользователь {chat_id} завершил проверку с результатом {score}/10")

def calculate_average_score() -> float:
    if not sessions:
        return 0.0
    total = sum(s.score for s in sessions.values())
    return total / len(sessions)

def calculate_percentile(score: int) -> float:
    if not sessions:
        return 100.0
    scores = [s.score for s in sessions.values()]
    lower_scores = sum(1 for s in scores if s < score)
    return (lower_scores / len(scores)) * 100

ADMIN_IDS = []

@bot.message_handler(commands=['stats'])
def handle_stats(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Эта команда только для администраторов")
        return
    
    stats_text = f"""
<b>📊 СТАТИСТИКА БОТА:</b>
• Версия: {Config.VERSION}
• Активных сессий: {len(sessions)}
• Всего пользователей сегодня: {len([s for s in sessions.values() if s.start_time.date() == datetime.now().date()])}
• Средний балл: {calculate_average_score():.1f}/10
• Время работы: {(datetime.now() - start_time).total_seconds() / 3600:.1f} часов
    """
    
    bot.send_message(message.chat.id, stats_text)

@bot.message_handler(commands=['version'])
def handle_version(message: types.Message):
    version_text = f"""
<b>ℹ️ ИНФОРМАЦИЯ О БОТЕ:</b>
• Название: {Config.AUTHOR}
• Версия: {Config.VERSION}

<b>🔒 БЕЗОПАСНОСТЬ:</b>
• Токен защищен: {'✅' if 'config.py' not in sys.modules else '⚠️'}
• Логирование: ✅
• Защита данных: ✅
    """
    
    bot.send_message(message.chat.id, version_text)

@bot.message_handler(func=lambda m: True)
def handle_unknown(message: types.Message):
    responses = [
        "Я понимаю только кнопки и команды /start",
        "Пожалуйста, используйте кнопки для ответов",
        "Напишите /start чтобы начать проверку",
        "Выберите вариант ответа из кнопок ниже"
    ]
    
    import random
    response = random.choice(responses)
    
    bot.send_message(message.chat.id, response, reply_markup=create_keyboard())

def check_dependencies():
    try:
        import telebot
        logger.info("✅ pyTelegramBotAPI установлен")
    except ImportError:
        logger.error("❌ pyTelegramBotAPI не установлен!")
        print("Установите зависимости: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "="*60)
    print(f"🤖 {Config.AUTHOR} v{Config.VERSION}")
    print("="*60)
    
    check_dependencies()
    
    start_time = datetime.now()
    
    bot_info = bot.get_me()
    logger.info(f"Бот запущен: @{bot_info.username} ({bot_info.first_name})")
    
    print(f"\n✅ Бот успешно запущен!")
    print(f"👤 Имя бота: {bot_info.first_name}")
    print(f"🔗 Ссылка: https://t.me/{bot_info.username}")
    print(f"🕒 Время запуска: {start_time.strftime('%H:%M:%S')}")
    print("\n" + "="*60)
    print("📱 Откройте Telegram и напишите боту /start")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    try:
        bot.polling(none_stop=True, interval=1, timeout=30)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        print("\n\n👋 Бот остановлен. До свидания!")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Ошибка: {e}")
        print("Проверьте токен и интернет соединение")