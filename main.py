import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from googletrans import Translator
from config import TOKEN, WEATHER_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

translator = Translator()  # Инициализация переводчика

# Список городов для прогноза
CITIES = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Ташкент", "Паттайя"]

# Создаем клавиатуру с городами
city_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text=city)] for city in CITIES]
)

# Функция для получения прогноза погоды
async def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data['main']['temp']
                    description = data['weather'][0]['description']
                    return f"Погода в {city}: {temp}°C, {description.capitalize()}"
                else:
                    return f"Ошибка {response.status}: Не удалось получить данные о погоде."
    except aiohttp.ClientConnectorError:
        return "Ошибка: Не удалось подключиться к серверу."
    except asyncio.TimeoutError:
        return "Ошибка: Превышен таймаут ожидания ответа от сервера."
    except Exception as e:
        return f"Неизвестная ошибка: {e}"


@dp.message(Command("weather"))
async def weather(message: Message):
    await message.answer("Выберите город для прогноза погоды:", reply_markup=city_keyboard)

@dp.message(F.text.in_(CITIES))
async def city_weather(message: Message):
    city = message.text
    forecast = await get_weather(city)
    await message.answer(forecast)

@dp.message(Command("video"))
async def video(message: Message):
    await bot.send_chat_action(message.chat.id, 'upload_video')
    video = FSInputFile("video_2024-12-12_00-32-27.mp4")
    await bot.send_video(message.chat.id, video)

@dp.message(Command("audio"))
async def audio(message: Message):
    audio = FSInputFile("audio_2024-12-12_00-29-24.ogg")
    await bot.send_audio(message.chat.id, audio)


@dp.message(Command("photo", prefix='/'))
async def photo(message: Message):
    photos = [
        'http://cdn.fishki.net/upload/post/201508/06/1619927/3_2.jpg',
        'http://cdn.fishki.net/upload/post/201508/06/1619927/4_4.jpg',
        'http://cdn.fishki.net/upload/post/201508/06/1619927/4_1.jpg',
        'http://cdn.fishki.net/upload/post/201508/06/1619927/3_3.jpg',
        'http://cdn.fishki.net/upload/post/201508/06/1619927/3_6.jpg',
        'http://cdn.fishki.net/upload/post/201508/06/1619927/26.jpg'
    ]
    rand_photo = random.choice(photos)
    await message.answer_photo(photo=rand_photo, caption='Это крутая фотка!')

@dp.message(F.photo)
async def react_photo(message: Message):
    responses = [
        'Ого, какая непонятная фотка!',
        'Не вкурил, а что это такое?!',
        'Не отправляй мне такое больше!'
    ]
    rand_response = random.choice(responses)
    await message.answer(rand_response)
    await bot.download(message.photo[-1], destination=f'img/{message.photo[-1].file_id}.jpg')

@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer('Иску́сственный интелле́кт (англ. artificial intelligence; AI) в самом широком смысле — это интеллект, демонстрируемый машинами...')

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer('Этот бот умеет выполнять команды: \n /start \n /help \n /weather \n /photo')


@dp.message(F.text & ~F.text.startswith("/"))  # Исключаем команды
async def translate_text(message: Message):
    """Перевод текста пользователя на английский"""
    try:
        translated = translator.translate(message.text, src='auto', dest='en')
        await message.answer(f"Перевод на английский:\n{translated.text}")
    except Exception as e:
        await message.answer(f"Произошла ошибка при переводе: {e}")


@dp.message(CommandStart)
async def start(message: Message):
    await message.answer(f'Приветики, {message.from_user.first_name}! Я бот! Могу показать погоду, фотки и многое другое!')



async def main():
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
