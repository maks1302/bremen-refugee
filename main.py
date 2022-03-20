import logging

from aiogram.types import ChatType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import funcs
import config
import keyboards
from bot_states import *



# Config logging
# log_format = '%(levelname)s: %(asctime)s: %(message)s '
# logging.basicConfig(filename='bot.log', level='INFO', format=log_format)
# logger = logging.getLogger()

# Setting the bot's config
bot = Bot(token=config.BOT_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=MemoryStorage())

CANCEL = "\n\n<code>You can cancel the action by pressing</code> /cancel"


@dp.message_handler(chat_type=[ChatType.CHANNEL, ChatType.SUPERGROUP, ChatType.GROUP])
async def access_func(message: types.Message):
    # Avoid any messages but private
    pass


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='/exit', ignore_case=True), state='*')
async def get_cancelled(message: types.Message, state: FSMContext):
    # Cancel user action, clean up state and memory, send a keyboard

    await state.finish()
    await message.reply('Cancelled ✔️', reply=False, reply_markup=keyboards.main_keyboard())


@dp.message_handler(commands='start')  # If command is "start"
async def start(message: types.Message):
    # Greetings a user

    to_print = 'Welcome message'
    await message.reply(to_print, reply_markup=keyboards.main_keyboard(), reply=False)


@dp.message_handler(regexp=keyboards.helper)
@dp.message_handler(regexp=keyboards.refugee)
async def add_message_step1(message: types.Message, state: FSMContext) -> None:
    """
    """

    await state.update_data(user_id=message.chat.id)
    if message.text == keyboards.refugee:
        await state.update_data(role='refugee')
        to_print = 'Choose a service you need as a refugee' + CANCEL
    else:
        await state.update_data(role='helper')
        to_print = 'Choose a service you can provide a refugee with as a volunteer' + CANCEL
    await message.reply(to_print, reply=False, reply_markup=keyboards.second_keyboard())


@dp.message_handler(regexp=keyboards.authorities)
async def add_message_step1(message: types.Message, state: FSMContext) -> None:
    """
    """
    result = await state.get_data()
    if result['role'] == 'refugee':
        to_print = "You can ask for an assistance from a volunteer with authorities in the districts bellow"
    else:
        to_print = "You can provide an assistance to a refugee as a volunteer with authorities in the districts bellow"
    await message.reply(to_print, reply=False)
    to_print = funcs.get_district_list()
    await message.reply(to_print, reply=False, reply_markup=keyboards.ReplyKeyboardRemove())
    await Add.district.set()
    to_print = 'Enter a number of district for an assistance' + CANCEL
    await message.reply(to_print, reply=False)


@dp.message_handler(state=Add.district)
async def add_message_step3(message: types.Message, state: FSMContext):
    """
    Handling buttons and retrieving text and links if exists,
    forward user to next step of creating a message
    """
    if str(message.text).isdigit() and 0 < int(message.text) <= len(config.districts):
        district = funcs.get_district(int(message.text))
        await state.update_data(district=district)
        to_print = 'Type data in format dd.mm.yyyy, eg: 20.03.2022' + CANCEL
        await Add.date.set()
        await message.reply(to_print, reply=False)
    else:
        to_print = '⚠️ Only correct number of districts allowed' + CANCEL
        return await message.reply(to_print, reply=False)


@dp.message_handler(state=Add.date, regexp='^\s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*$')
async def add_message_step3(message: types.Message, state: FSMContext):
    """
    Handling buttons and retrieving text and links if exists,
    forward user to next step of creating a message
    """

    await state.update_data(date=message.text)
    to_print = 'Input local time in format HH:MM, eg: 14:00' + CANCEL
    await Add.time.set()
    await message.reply(to_print, reply=False)


@dp.message_handler(state=Add.date)
async def add_message_step3_fail(message: types.Message):
    # If buttons do not match the pattern, then return

    to_print = '⚠️ Wrong input use next format dd.mm.yyyy, eg: 20.03.2022' + CANCEL
    return await message.reply(to_print, reply=False)


@dp.message_handler(state=Add.time, regexp='^([0-1][0-9]|[2][0-3]):([0-5][0-9])$')
async def add_message_step3(message: types.Message, state: FSMContext):
    """
    Handling buttons and retrieving text and links if exists,
    forward user to next step of creating a message
    """

    await state.update_data(time=message.text)
    result = await state.get_data()
    await state.finish()
    to_print = 'Your query has been added'
    await message.reply(to_print, reply=False, reply_markup=keyboards.main_keyboard())
    funcs.process_query(result)

    if result['role'] == 'refugee':
        found_helpers = funcs.get_refugee_result(result, role='helper')
        if found_helpers:
            await message.reply(f"Found {len(found_helpers)} volunteers matched your requests", reply=False)
            for helper in found_helpers:
                await message.reply(funcs.helper_layout(helper), reply=False)
        else:
            to_print = 'There is no matches for your query yet. When there is a match to your query, you will be notified\n\n' \
                       'You can also check if there is available helpers for another date or district by typing ' \
                       '<code>/check {district number} {date} </code> \ne.g. /check 7 20.03.2022\n\n' \
                       'If you no longer need an assistance, please press /myQueries and remove your query'
            await message.reply(to_print, reply=False)
    else:
        to_print = 'In case you no longer able to provide an assistance at that time, please press /myQueries and remove your query'
        await message.reply(to_print, reply=False)

        found_refugee = funcs.get_refugee_result(result, role='refugee')
        if found_refugee:
            for refugee in found_refugee:
                to_print = "Found new helper\n\n" + funcs.helper_layout(refugee, user_id=message.chat.id)
                await bot.send_message(refugee[0], to_print)
                to_print = "If you no longer want to receive notification, please press /myQueries and remove your query"
                await bot.send_message(refugee[0], to_print)


@dp.message_handler(state=Add.time)
async def add_message_step3_fail(message: types.Message):
    # If buttons do not match the pattern, then return
    to_print = 'Type time in format HH:MM, eg: 14:00' + CANCEL
    return await message.reply(to_print, reply=False)


@dp.message_handler(commands='check')
async def set_supply_command(message: types.Message):

    arguments = message.get_args()
    if arguments:
        result = funcs.get_check_result(arguments)
        if result:
            await message.reply(f"Found {len(result)} volunteers matched your requests", reply=False)
            for helper in result:
                await message.reply(funcs.helper_layout(helper), reply=False)
        else:
            await message.reply('Nothing found, try another district or date', reply=False)
    else:
        to_print = 'Use the next following format: <code>/check {district number} {date} </code> e.g. /check 7 20.03.2022'
        await message.reply(to_print, reply=False)


@dp.message_handler(commands='myqueries')
async def set_supply_command(message: types.Message):

    result = funcs.user_queries(message.chat.id)
    if result:
        for helper in result:
            await message.reply(funcs.helper_layout(helper, check=True), reply=False, reply_markup=keyboards.inline_keyboard())
    else:
        await message.reply('You have no active queries yet', reply=False)


@dp.callback_query_handler(lambda query: query.data == 'remove')
async def get_change_message_status(query: types.CallbackQuery):
    # Changing active status of a message

    await query.answer('Done ✅')
    funcs.remove_query(query.from_user.id, query.message.text)
    to_print = query.message.text + "\n\nRemoved 🗑"
    await bot.edit_message_text(text=to_print, chat_id=query.message.chat.id, message_id=query.message.message_id)


if __name__ == '__main__':
    print('All rights reserved, created by @demploy')
    print('The bot is working...')
    executor.start_polling(dp, skip_updates=True)
