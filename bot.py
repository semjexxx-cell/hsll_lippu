import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# === ASETUKSET ===
BOT_TOKEN = "8626996527:AAGR6_U-dyiHfy0pctVBHCd9NwVrITf1hlE"
ADMIN_ID = 5359836899

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Глобальная переменная для хранения текущего цвета
current_color = "🟢 Vihreä"
VIDEO_PATH = "lippu.mp4"

# Состояния для FSM (ожидание ввода от админа)
class AdminStates(StatesGroup):
    waiting_for_color = State()
    waiting_for_video = State()

# Valikko käyttäjille (Обычное меню)
user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎨 Päivän väri")],
        [KeyboardButton(text="🎥 Näytä lippu")]
    ],
    resize_keyboard=True
)

# Valikko adminille (Админ-меню)
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎨 Päivän väri"), KeyboardButton(text="🎥 Näytä lippu")],
        [KeyboardButton(text="⚙️ Vaihda väri"), KeyboardButton(text="⚙️ Vaihda video")]
    ],
    resize_keyboard=True
)

# /start -komento
@dp.message(Command("start"))
async def start_cmd(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Terve Admin! Valitse toiminto valikosta:", reply_markup=admin_keyboard)
    else:
        await message.answer("Terve! Valitse toiminto valikosta:", reply_markup=user_keyboard)

# Painike: Päivän väri (Показ цвета)
@dp.message(F.text == "🎨 Päivän väri")
async def day_color(message: Message):
    text = f"<b>Tämän päivän väri:</b>\n\n{current_color}"
    await message.answer(text, parse_mode="HTML")

# Painike: Näytä lippu (Показ видео)
@dp.message(F.text == "🎥 Näytä lippu")
async def show_video(message: Message):
    if os.path.exists(VIDEO_PATH):
        video = FSInputFile(VIDEO_PATH)
        await message.answer_video(video, caption="Tässä on lippusi!")
    else:
        await message.answer("Videotiedostoa ei ole vielä asetettu.")

# === ADMIN-TOINNOT (АДМИН-ФУНКЦИИ) ===

# Нажатие "Vaihda väri" (Смена цвета)
@dp.message(F.text == "⚙️ Vaihda väri")
async def change_color_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_color)
    await message.answer("Kirjoita uusi päivän väri (esim. 🔴 Punainen):")

# Получение нового цвета
@dp.message(AdminStates.waiting_for_color)
async def process_new_color(message: Message, state: FSMContext):
    global current_color
    current_color = message.text
    await state.clear()
    await message.answer(f"Päivän väri päivitetty!\nUusi väri: {current_color}")

# Нажатие "Vaihda video" (Смена видео)
@dp.message(F.text == "⚙️ Vaihda video")
async def change_video_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_video)
    await message.answer("Lähetä uusi videotiedosto:")

# Получение нового видеофайла
@dp.message(AdminStates.waiting_for_video, F.video)
async def process_new_video(message: Message, state: FSMContext):
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, VIDEO_PATH)
    await state.clear()
    await message.answer("Uusi video tallennettu onnistuneesti!")

async def main():
    print("Botti käynnistetty!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())