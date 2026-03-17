import asyncio
import json
import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Класс состояний для FSM
class FindWorkForm(StatesGroup):
    name = State()
    age = State()
    exp = State()
    area = State()
    phone = State()

class VacancyForm(StatesGroup):
    text = State()

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="🔍 Найти работу"),
        KeyboardButton(text="📢 Оставить вакансию"),
        KeyboardButton(text="📋 Правила группы"),
        KeyboardButton(text="👤 Связаться с администратором")
    )
    builder.adjust(2) 
    return builder.as_markup(resize_keyboard=True)


def get_back_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔙 Главное меню"))
    return builder.as_markup(resize_keyboard=True)


def get_phone_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📲 Отправить контакт", request_contact=True),
        KeyboardButton(text="🔙 Главное меню"),
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def validate_phone(phone):
    cleaned = re.sub(r'[^\d+]', '', phone)
    pattern = r'^(\+7|8|7)?\d{10}$'
    return re.match(pattern, cleaned) is not None


def is_private_chat(message: types.Message) -> bool:
    return message.chat.type == "private"

user_last_message = {}

def check_spam(user_id):
    import time
    current_time = time.time()
    if user_id in user_last_message:
        if current_time - user_last_message[user_id] < 1:
            return False
    user_last_message[user_id] = current_time
    return True

@dp.message(Command("start"))
async def start(message: types.Message):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    await message.answer(
        "👋 Добро пожаловать в *Разнорабочие Ростов | Работа каждый день*!\n\n"
        "Выберите нужный пункт меню:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.message(lambda m: m.text == "🔍 Найти работу")
async def start_find_work(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    await state.set_state(FindWorkForm.name)
    await message.answer("📝 Введите ваше имя:", reply_markup=get_back_menu())

@dp.message(FindWorkForm.name)
async def process_name(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    if message.text == "🔙 Главное меню":
        await state.clear()
        await message.answer("Возвращаю в главное меню.", reply_markup=get_main_menu())
        return
    if not message.text or not message.text.strip():
        await message.answer("❌ Пожалуйста, введите текст (имя).")
        return
    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer("❌ Имя должно быть от 2 до 50 символов. Попробуйте снова:")
        return
    
    await state.update_data(name=message.text)
    await state.set_state(FindWorkForm.age)
    await message.answer("📅 Введите ваш возраст (только цифры):", reply_markup=get_back_menu())

@dp.message(FindWorkForm.age)
async def process_age(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    if message.text == "🔙 Главное меню":
        await state.clear()
        await message.answer("Возвращаю в главное меню.", reply_markup=get_main_menu())
        return
    if not message.text:
        await message.answer("❌ Введите возраст цифрами.")
        return
    if not message.text.isdigit():
        await message.answer("❌ Возраст должен быть числом. Попробуйте снова:")
        return
    
    age = int(message.text)
    if age < 14 or age > 100:
        await message.answer("❌ Возраст должен быть от 14 до 100 лет. Попробуйте снова:")
        return
    
    await state.update_data(age=message.text)
    await state.set_state(FindWorkForm.exp)
    await message.answer("💼 Опыт работы (например: '1 год' или 'без опыта'):", reply_markup=get_back_menu())

@dp.message(FindWorkForm.exp)
async def process_exp(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    if message.text == "🔙 Главное меню":
        await state.clear()
        await message.answer("Возвращаю в главное меню.", reply_markup=get_main_menu())
        return
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст (опыт работы).")
        return
    if len(message.text) > 200:
        await message.answer("❌ Слишком длинное описание опыта (максимум 200 символов). Попробуйте короче:")
        return
    
    await state.update_data(exp=message.text)
    await state.set_state(FindWorkForm.area)
    await message.answer("📍 Район Ростова (например: 'Центр', 'Западный'):", reply_markup=get_back_menu())

@dp.message(FindWorkForm.area)
async def process_area(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    if message.text == "🔙 Главное меню":
        await state.clear()
        await message.answer("Возвращаю в главное меню.", reply_markup=get_main_menu())
        return
    if not message.text:
        await message.answer("❌ Пожалуйста, введите район.")
        return
    if len(message.text) > 100:
        await message.answer("❌ Слишком длинное название района (максимум 100 символов). Попробуйте короче:")
        return
    
    await state.update_data(area=message.text)
    await state.set_state(FindWorkForm.phone)
    await message.answer(
        "📞 Ваш номер телефона (например: +7XXX или 8XXX)\n"
        "Или нажмите кнопку «📲 Отправить контакт»:",
        reply_markup=get_phone_menu(),
    )

@dp.message(FindWorkForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    # Обработка возврата в главное меню (только для текстовых сообщений)
    if message.text == "🔙 Главное меню":
        await state.clear()
        await message.answer("Возвращаю в главное меню.", reply_markup=get_main_menu())
        return

    # Получаем номер из контакта или текста
    phone_value = None
    if message.contact and message.contact.phone_number:
        phone_value = message.contact.phone_number
    elif message.text:
        phone_value = message.text

    if not phone_value:
        await message.answer("❌ Пожалуйста, отправьте номер телефона или контакт.")
        return

    if not validate_phone(phone_value):
        await message.answer(
            "❌ Некорректный номер телефона.\n"
            "Введите российский номер в формате: +7XXXXXXXXXX или 8XXXXXXXXXX"
        )
        return
    
    data = await state.get_data()
    
    text = (
        f"📌 *Новая заявка от соискателя*\n\n"
        f"👤 *Имя:* {data['name']}\n"
        f"📅 *Возраст:* {data['age']}\n"
        f"💼 *Опыт:* {data['exp']}\n"
        f"📍 *Район:* {data['area']}\n"
        f"📞 *Телефон:* {phone_value}\n"
        f"🆔 *ID:* {message.from_user.id}"
    )
    profile_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Открыть профиль", url=f"tg://user?id={message.from_user.id}")]
    ])

    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="Markdown", reply_markup=profile_kb)
        await message.answer(
            "✅ Ваша заявка успешно отправлена работодателю!\n\n"
            "Ожидайте звонка или сообщения.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_menu()
        )
        print(f"Error sending to admin: {e}")
    
    await state.clear()

@dp.message(lambda m: m.text == "📢 Оставить вакансию")
async def start_vacancy(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    await state.set_state(VacancyForm.text)
    await message.answer(
        "📢 Отправьте текст вакансии одним сообщением.\n\n"
        "Рекомендуем указать:\n"
        "• Название вакансии\n"
        "• Требования\n"
        "• Условия работы\n"
        "• Зарплата\n"
        "• Контакты",
        reply_markup=get_back_menu(),
    )

@dp.message(VacancyForm.text)
async def process_vacancy(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    if message.text == "🔙 Главное меню":
        await state.clear()
        await message.answer("Возвращаю в главное меню.", reply_markup=get_main_menu())
        return
    if not message.text:
        await message.answer("❌ Пожалуйста, отправьте текст вакансии сообщением.")
        return
    if len(message.text) < 10:
        await message.answer("❌ Текст вакансии слишком короткий (минимум 10 символов). Опишите подробнее:")
        return
    
    if len(message.text) > 4000:
        await message.answer("❌ Текст вакансии слишком длинный (максимум 4000 символов). Сократите описание:")
        return
    
    vacancy_text = (
        f"📢 *Новая вакансия*\n\n"
        f"{message.text}\n\n"
        f"👤 *Автор:* {message.from_user.full_name}"
    )
    profile_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Открыть профиль", url=f"tg://user?id={message.from_user.id}")]
    ])
    try:
        await bot.send_message(
            GROUP_ID,
            vacancy_text,
            parse_mode="Markdown",
            reply_markup=profile_kb,
        )
        await message.answer(
            "✅ Вакансия успешно опубликована в группе!",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при публикации. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_menu()
        )
        print(f"Error sending to channel: {e}")
    
    await state.clear()

@dp.message(lambda m: m.text == "📋 Правила группы")
async def rules(message: types.Message):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    rules_text = (
        "📋 *Правила группы*\n\n"
        "1️⃣ Без спама и рекламы\n"
        "2️⃣ Указывайте актуальный номер телефона\n"
        "3️⃣ Уважайте других участников\n"
        "4️⃣ Запрещен флуд и оскорбления\n"
        "5️⃣ Вакансии должны соответствовать тематике канала\n\n"
        "Нарушение правил ведет к блокировке!"
    )
    await message.answer(rules_text, parse_mode="Markdown")

@dp.message(lambda m: m.text == "👤 Связаться с администратором")
async def contact_admin(message: types.Message):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    await message.answer(
        f"👤 *Связь с администратором*\n\n"
        f"{ADMIN_CONTACT}\n\n"
        f"Или напишите в личные сообщения боту.",
        parse_mode="Markdown"
    )

# Обработчик для отмены действий
@dp.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    if not is_private_chat(message):
        return
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        "❌ Действие отменено. Возвращаю в главное меню.",
        reply_markup=get_main_menu()
    )

# Обработчик для всех остальных сообщений
@dp.message()
async def unknown_message(message: types.Message):
    if not is_private_chat(message):
        return
    if not check_spam(message.from_user.id):
        return
    await message.answer(
        "❓ Я не понимаю эту команду.\n"
        "Пожалуйста, используйте кнопки меню.",
        reply_markup=get_main_menu()
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
