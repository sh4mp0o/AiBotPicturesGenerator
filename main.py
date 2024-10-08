from aiogram import Bot, types, Dispatcher, Router, F
from aiogram.filters import Command
import asyncio
import uuid
import json
import websockets

token = '' # Ваш токен бота взятый из @BotFather
runware_api = 'z1ilk4CqKMMMPSm3gynSdrsuoKsECcxK' # Тот самый ключик разработчиков для работы нейросети

bot = Bot(token=token)
dp = Dispatcher()
router = Router()

async def create_image(prompt): # Генерируем картинку
    async with websockets.connect('wss://ws-api.runware.ai/v1') as websocket:
        auth_request = [{"taskType": "authentication","apiKey": runware_api}]
        await websocket.send(json.dumps(auth_request)) # Логинимся и получаем успешный ответ от сервера
        auth_response = await websocket.recv()
        n = 1
        image_request = [{"positivePrompt": prompt,"model": "runware:100@1",'steps':4,'width':512,'height':512,'numberResults':n,'outputType':['URL'],'taskType':'imageInference','taskUUID':uuid.uuid4().hex}]
        await websocket.send(json.dumps(image_request)) # Отправляем запрос на генерацию и получаем картинку
        img = await websocket.recv()
        data = json.loads(img)['data'][0]
        return data

@router.message(Command('start')) # Добавляем ответ на команду /start
async def start(message: types.Message):
    await message.answer('Hi!\nI am a bot that instantly generates images based on your requests.\nType the text in English.')

@router.message() # Ловим промпты
async def gen(message: types.Message):
    if not message.text:
        return await message.answer('Only text :(')
    msg = await message.answer(f'Generating:\n\n{message.text}')
    print(message.text)
    image = await create_image(message.text)
    await message.answer_photo(image['imageURL'], caption=f'Generation according to your request:\n\n{message.text}')
    await bot.delete_messages(message.chat.id, [msg.message_id, message.message_id])

async def main():
    router.message.filter(F.chat.type == 'private')
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Бот для генерации картинок успешно запущен')
    asyncio.run(main())