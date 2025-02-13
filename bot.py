import logging
logging.basicConfig(level=logging.INFO)
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp
import subprocess
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Получаем токен из переменной окружения
API_TOKEN = os.getenv('BOT_TOKEN')

# Проверка, что токен был загружен правильно
if not API_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

print(f"Loaded API_TOKEN: {API_TOKEN}")  # Это поможет убедиться, что токен правильно загружен

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Функция для получения FPS с помощью ffmpeg
def get_fps(video_path):
    try:
        # Используем ffmpeg для извлечения данных о видео
        result = subprocess.run(
            ['ffmpeg', '-i', video_path],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        for line in result.stderr.splitlines():
            if 'fps' in line:
                fps = float(line.split('fps')[0].strip().split()[-1])
                print(f"FPS получено через ffmpeg: {fps}")
                return fps
        # Если не удается найти fps, установим дефолтное значение
        print("FPS не найден, установлено значение по умолчанию: 30")
        return 30
    except Exception as e:
        print(f"Ошибка при получении FPS: {e}")
        return 30  # Возвращаем 30 по умолчанию в случае ошибки

# Функция для скачивания видео
def download_video(url):
    try:
        ydl_opts = {
            'format': 'bv+ba/best',  # Скачать лучшее видео и аудио
            'merge_output_format': 'mp4',  # Формат файла
            'outtmpl': 'downloaded_video.%(ext)s',  # Имя файла с расширением
            'noplaylist': True,  # Отключить скачивание плейлистов
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # Скачиваем видео по ссылке

        # Получаем FPS с помощью ffmpeg
        fps = get_fps('downloaded_video.mp4')
        print(f"Видео скачано успешно! FPS: {fps}")
    except Exception as e:
        print(f"Ошибка при скачивании видео: {e}")

# Обработчик команды /download
@dp.message_handler(commands=['download'])
async def cmd_download(message: types.Message):
    try:
        url = message.text.split(" ", 1)[1]  # Получаем ссылку после команды
        download_video(url)  # Загружаем видео
        await message.reply(f"Видео скачано: {url}")
    except IndexError:
        await message.reply("Пожалуйста, предоставьте ссылку в формате: /download <ссылка>")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
