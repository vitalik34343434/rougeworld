import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from mcrcon import MCRcon

TOKEN = ""
CHANNEL_ID = "@RougeWorlds"  # канал для подписки

RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "пароль"

DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# загрузка базы
try:
    with open(DATA_FILE, "r") as f:
        users = json.load(f)
except:
    users = {}

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

# кнопки
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(KeyboardButton("🎁 Получить донат"))

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "🔥 Привет!\nХочешь получить донат на сервере RougeWorld?\n\nЖми кнопку ниже 👇",
        reply_markup=kb
    )

@dp.message_handler(lambda m: m.text == "🎁 Получить донат")
async def donate(msg: types.Message):
    user_id = str(msg.from_user.id)

    # проверка подписки
    member = await bot.get_chat_member(CHANNEL_ID, msg.from_user.id)
    if member.status == "left":
        await msg.answer("❌ Подпишись на канал, чтобы получить награду!")
        return

    if user_id in users:
        await msg.answer("❌ Ты уже получал награду!")
        return

    await msg.answer("✏️ Введи свой ник Minecraft:")

    users[user_id] = {"step": "waiting_nick"}
    save()

@dp.message_handler()
async def handle(msg: types.Message):
    user_id = str(msg.from_user.id)

    if user_id not in users:
        return

    if users[user_id].get("step") == "waiting_nick":
        nick = msg.text

        # проверка: ник уже использован
        for u in users.values():
            if u.get("nick") == nick:
                await msg.answer("❌ Этот ник уже получил награду!")
                return

        # выдача награды через RCON
        try:
            with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
                mcr.command(f"give {nick} diamond 5")

            users[user_id] = {"nick": nick}
            save()

            await msg.answer("✅ Донат выдан! Заходи на сервер 🔥")

        except Exception as e:
            await msg.answer("⚠️ Ошибка выдачи награды")
            print(e)

if __name__ == "__main__":
    executor.start_polling(dp)