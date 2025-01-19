import asyncio
from handlers import router
from config import TOKEN
from aiogram import Bot,Dispatcher
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)




async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())