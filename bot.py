import os
import yt_dlp
import openai
from moviepy.editor import VideoFileClip
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from googletrans import Translator

# 🔑 Получаем токены из переменных окружения (чтобы они были скрыты)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 🎥 Функция для скачивания видео
def download_video(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_video.mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "downloaded_video.mp4"

# 🎵 Функция для извлечения аудио
def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio_path = "audio.wav"
    video.audio.write_audiofile(audio_path)
    return audio_path

# 📝 Функция для транскрибации (Whisper AI)
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)
    return response["text"]

# 🌍 Функция для перевода текста
def translate_text(text):
    translator = Translator()
    translation = translator.translate(text, src='en', dest='ru')
    return translation.text

# 📩 Обрабатываем команду /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Отправь мне ссылку на видео, и я сделаю транскрибацию и перевод 🚀")

# 📩 Обрабатываем ссылки на видео
@dp.message_handler()
async def handle_video(message: types.Message):
    url = message.text
    await message.reply("⏳ Загружаю видео...")

    try:
        video_path = download_video(url)
        audio_path = extract_audio(video_path)
        transcript = transcribe_audio(audio_path)
        translated_text = translate_text(transcript)

        await message.reply(f"📝 Транскрипция:\n{transcript}\n\n🌍 Перевод:\n{translated_text}")

        # Удаляем файлы после обработки
        os.remove(video_path)
        os.remove(audio_path)

    except Exception as e:
        await message.reply(f"❌ Ошибка: {str(e)}")

# 🚀 Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
