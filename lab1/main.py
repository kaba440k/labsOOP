import os
import asyncio
import logging
import requests
import yt_dlp
from aiogram import F, Router, types, Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Токены API
IMAGE_TOKEN = "YOUR_IMAGE_TOKEN"
BOT_TOKEN = 'YOUR_TOKEN'

# Инициализация бота и диспетчера
bot_instance = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher()
bot_router = Router()

# Клавиатура с основными кнопками
main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🖼️ Создать изображение', callback_data='create_image')],
    [InlineKeyboardButton(text="🎶 Найти музыку", callback_data='search_music')],
    [InlineKeyboardButton(text="🔗 Исходный код проекта", callback_data='project_url')]
])

# Класс состояний для FSM
class UserState(StatesGroup):
    waiting_for_prompt = State()  # Ожидание запроса для создания изображения
    waiting_for_audio = State()  # Ожидание запроса для поиска музыки

# Обработчик команды /start
@bot_router.message(CommandStart())
async def on_start(message: Message):
    await message.reply(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Что хотите сделать? 🤔",
        reply_markup=main_keyboard
    )

# Обработчик для кнопки с ссылкой на GitHub
@bot_router.callback_query(F.data == 'project_url')
async def redirect_to_github(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('https://github.com/kaba440k/labsOOP.git', reply_markup=main_keyboard)

# Функция для скачивания аудио по запросу
async def download_audio_by_query(query: str) -> str:
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    download_options = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': f'downloads/{query}.mp3',
    }

    try:
        with yt_dlp.YoutubeDL(download_options) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{query}", download=True)
            if search_results['entries']:
                audio_path = f"downloads/{query}.mp3"
                return audio_path if os.path.exists(audio_path) else None
            return None
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        return None

# Обработчик для кнопки "Найти музыку"
@bot_router.callback_query(F.data == 'search_music')
async def request_audio_query(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите запрос для поиска музыки. 🎶")
    await state.set_state(UserState.waiting_for_audio)
    await callback_query.answer()

# Обработчик получения названия музыки от пользователя
@bot_router.message(UserState.waiting_for_audio)
async def process_audio_request(message: types.Message, state: FSMContext):
    audio_file_path = await download_audio_by_query(message.text)
    if audio_file_path and os.path.exists(audio_file_path):
        with open(audio_file_path, 'rb') as audio_file:
            audio_file_io = FSInputFile(audio_file_path)
            await state.clear()
            await message.answer_audio(
                audio=audio_file_io,
                caption="Вот найденное аудио по вашему запросу.",
                reply_markup=main_keyboard
            )
        os.remove(audio_file_path)  # Удаляем файл после отправки
    else:
        await message.reply("Не удалось найти подходящее аудио.")

# Обработчик для кнопки "Создание изображения"
@bot_router.callback_query(F.data == "create_image")
async def request_image_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите запрос для создания изображения. 🖼")
    await state.set_state(UserState.waiting_for_prompt)

# Обработчик получения запроса на изображение от пользователя
@bot_router.message(UserState.waiting_for_prompt)
async def process_image_request(message: Message, state: FSMContext):
    user_query = message.text.strip()
    image_url = fetch_image_url(user_query)

    if image_url:
        await message.answer_photo(
            photo=image_url,
            caption="Вот изображение по вашему запросу.",
            reply_markup=main_keyboard
        )
    else:
        await message.reply(
            "Не удалось найти изображение. Попробуйте уточнить запрос.",
            reply_markup=main_keyboard
        )
    await state.clear()


# Функция для получения URL изображения по запросу через API Unsplash
def fetch_image_url(query: str) -> str:
    api_url = f"https://api.unsplash.com/photos/random?query={query}&client_id={IMAGE_TOKEN}"
    response = requests.get(api_url)
    response.raise_for_status()  # Проверка на ошибки HTTP
    data = response.json()
    return data.get("urls", {}).get("regular", "")


# Основная функция для запуска бота
async def run_bot():
    dispatcher.include_router(bot_router)
    await dispatcher.start_polling(bot_instance)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_bot())
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
