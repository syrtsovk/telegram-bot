from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import yt_dlp
from dotenv import load_dotenv
import os
from moviepy.editor import VideoFileClip

# Загрузка переменных окружения
load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')  # Получаем токен из переменной окружения
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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

        # Теперь обрабатываем видео, чтобы избежать ошибки fps
        try:
            video = VideoFileClip("downloaded_video.mp4")
            fps = video.fps if video.fps else 30  # Если fps не найден, ставим 30
        except Exception as e:
            print(f"Ошибка при обработке видео: {e}")
            fps = 30  # Устанавливаем безопасное значение FPS

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
