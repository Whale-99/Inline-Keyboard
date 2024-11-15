from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Токен бота
api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Машина состояний для данных пользователя
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Обычная клавиатура для команды '/start'
kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_info = KeyboardButton(text='Информация')
button_start = KeyboardButton(text='Рассчитать')
kb.add(button_info)
kb.add(button_start)

# Inline-клавиатура для опций 'Рассчитать норму калорий' и 'Формулы расчёта'
inline_kb = InlineKeyboardMarkup()
button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton(text='Формула расчёта', callback_data='formulas')
inline_kb.add(button_calories)
inline_kb.add(button_formulas)

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Нажми "Рассчитать" для расчета калорий.')

# Функция, отправляющая Inline-клавиатуру при нажатии на 'Рассчитать'
@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

# Обработчик кнопки 'Формулы расчёта' — отправляет формулу расчета калорий
@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("Формула Миффлина-Сан Жеора для расчета калорийности:\n"
                              "Калории = 10 * вес + 6.25 * рост - 5 * возраст + 5")
    await call.answer()
# Обработчик кнопки 'Рассчитать норму калорий' — начинает машину состояний
@dp.callback_query_handler(text='calories')
async def set_age(call):
    await UserState.age.set()  # Устанавливаем состояние для ввода возраста
    await call.message.answer("Введите свой возраст:")
    await call.answer()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)  # Сохраняем возраст
        await UserState.next()  # Переходим к следующему состоянию
        await message.answer("Введите свой рост:")
        await call.answer()
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение для возраста.")
        await call.answer()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        growth = int(message.text)
        await state.update_data(growth=growth)  # Сохраняем рост
        await UserState.next()  # Переходим к следующему состоянию
        await message.answer("Введите свой вес:")
        await call.answer()
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение для роста.")
        await call.answer()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        await state.update_data(weight=weight)  # Сохраняем вес

        # Получаем все данные
        data = await state.get_data()
        age = data['age']
        growth = data['growth']
        weight = data['weight']

        # Формула Миффлина-Сан Жеора для расчета калорийности
        calories = 10 * weight + 6.25 * growth - 5 * age + 5

        # Отправляем результат пользователю
        await message.answer(f"Ваша дневная норма калорий: {calories:.2f} ккал.")

        # Завершаем машину состояний
        await state.finish()
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение для веса.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
