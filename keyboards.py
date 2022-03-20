from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


refugee = "🇺🇦 I'm refugee"
helper = "⛑ I'm helper"
donor = "Donor (soon)"
donate = "donate (soon)"


def main_keyboard() -> ReplyKeyboardMarkup:
    # Main keyboard for the bot

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    refugee_btn = KeyboardButton(refugee)
    helper_btn = KeyboardButton(helper)
    donor_btn = KeyboardButton(donor)
    donate_btn = KeyboardButton(donate)

    keyboard.row(refugee_btn, helper_btn)
    keyboard.row(donor_btn, donate_btn)

    return keyboard


authorities = "👥 Assistance with authorities"
accommodation = "🏘 Accommodation search (soon)"
transportation = "🚌 Transportation (soon)"


def second_keyboard() -> ReplyKeyboardMarkup:
    # Main keyboard for the bot

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.row(KeyboardButton(authorities))
    keyboard.row(KeyboardButton(accommodation))
    keyboard.row(KeyboardButton(transportation))

    return keyboard


def remove_keyboard() -> object:
    # Remove shown keyboard

    return ReplyKeyboardRemove


def inline_keyboard() -> InlineKeyboardMarkup:
    # Return keyboard of given users text and links

    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text="🗑 Remove query", callback_data='remove'))

    return keyboard
