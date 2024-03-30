import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

BOT_TOKEN = '6635050347:AAGewi0JzM3pX6TpaDJFUJsUYkzNqPN_RvYisHo'


bot = Bot(BOT_TOKEN)
dp = Dispatcher()

ATTEMPTS = 7

user = {}


def get_random_num() -> int:
    return random.randint(1, 100)


@dp.message(CommandStart())
async def process_start_command(message: Message):
    """Этот хэндлер будет срабатывать на команду '/start'"""
    await message.answer('Здравствуй!\nГотов сыгратьв игру "Угадай число"?\n\n'
                         'Чтобы узнать правила и список команд, которые доступны '
                         '- отправь команду /help')

    if message.from_user.id not in user:
        user[message.from_user.id] = {
            'in_game': False,
            'secret_num': None,
            'attempts': None,
            'total_games': 0,
            'wins': 0
        }


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    """Этот хэндлер будет срабатывать на команду '/help'"""
    await message.answer(f'Ну что ж...\nПравила игры:\n\nЯ загадываю число от 1 до 100, '
                         f'а тебе нужно его отгадать. Все просто я загадываю, ты отгадываешь\n'
                         f'У тебя есть {ATTEMPTS} попыток\n\nДоступные команды:\n/help - правила игры '
                         f'и список команд\n/cancel - выйти из игры\n/stat - посмотреть статистику\n\n'
                         f'Готов проверить свою интуицию?')


@dp.message(Command(commands='stat'))
async def process_stat_command(message: Message):
    """Этот хэндлер будет срабатывать на команду '/stat'"""
    await message.answer(f'Всего игр сыграно: {user[message.from_user.id]["total_games"]}\n'
                         f'Игр выиграно: {user[message.from_user.id]["wins"]}')


@dp.message(Command(commands='cancel'))
async def process_cancel_command(message: Message):
    """Этот хэндлер будет срабатывать на команду '/cancel'"""
    if user[message.from_user.id]['in_game']:
        user[message.from_user.id]['in_game'] = False
        await message.answer('Ты вышел из игры. Если захочешь сразиться еще раз '
                             '- напиши мне')
    else:
        await message.answer('Что-то ты не то жмешь. '
                             'Может сыграем разок?)')


@dp.message(F.text.lower().in_(['да', 'давай', 'игра']))
async def process_positive_answer(message: Message):
    """Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру"""
    if not user[message.from_user.id]['in_game']:
        user[message.from_user.id]['in_game'] = True
        user[message.from_user.id]['secret_num'] = get_random_num()
        user[message.from_user.id]['attempts'] = ATTEMPTS
        await message.answer('Итак... Я загадал число от 1 до 100, '
                             'попробуй-ка угадать!')
    else:
        await message.answer('Пока мы играем, я буду реагировать только на числа '
                             'от 1 до 100 и комынды /cancel и /stat')


@dp.message(F.text.lower().in_(['нет', 'не надо', 'не хочу']))
async def process_negative_answer(message: Message):
    """Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру"""
    if not user[message.from_user.id]['in_game']:
        await message.answer('Очень жаль,трусишка...\n\n Захочешь сыграть - пиши')
    else:
        await message.answer('Мы же сейчас играем. Шли числа...')


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_num_answer(message: Message):
    """Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100"""
    if user[message.from_user.id]['in_game']:
        if int(message.text) == user[message.from_user.id]['secret_num']:
            user[message.from_user.id]['in_game'] = False
            user[message.from_user.id]['total_games'] += 1
            user[message.from_user.id]['wins'] += 1
            await message.answer('Вот это да! Ты угадал!\n\nЕще разок?')
        elif int(message.text) > user[message.from_user.id]['secret_num']:
            user[message.from_user.id]['attempts'] -= 1
            await message.answer('Число меньше')
        elif int(message.text) < user[message.from_user.id]['secret_num']:
            user[message.from_user.id]['attempts'] -= 1
            await message.answer('Число больше')

        if user[message.from_user.id]['attempts'] == 0:
            user[message.from_user.id]['in_game'] = False
            user[message.from_user.id]['total_games'] += 1
            await message.answer(f'У тебя больше не осталось попыток. '
                                 f'Ты проиграл. Мое число было {user[message.from_user.id]["secret_num"]}\n\n'
                                 f'Возьмешь реванш?')
    else:
        await message.answer('Мы еще не играем. Хочешь сыграть?')


@dp.message()
async def process_other_answer(message: Message):
    """Этот хэндлер будет срабатывать на остальные сообщения"""
    if user[message.from_user.id]['in_game']:
        await message.answer('Мы же играем. Шли числа')
    else:
        await message.answer('Я такого не понимаю. Может лучше сыграем?')


if __name__ == '__main__':
    dp.run_polling(bot)
