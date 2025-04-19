import telebot
from telebot import types
from random import randint
import random

import sql_handler as sql_h

def start_markup(user_rank=0, *kwargs):
    start_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    start_markup.row('My notes🗄')
    start_markup.row('New note (text)⭐️')
    start_markup.row('New note (file)⭐️')
    # start_markup.row('Search')
    return start_markup

def mynotes_kb(tgid):
    kb_list = types.InlineKeyboardMarkup(row_width=1)
    for item in sql_h.SqlHandler().get_notes_all(tgid):
        # item: id, type, name
        name = types.InlineKeyboardButton(text=f'{item[2]}', callback_data=f'echonote,{item[1]},{item[0]}')
        rm = types.InlineKeyboardButton(text='❌', callback_data=f'rmnote,{item[1]},{item[0]}')
        kb_list.row(name,rm)
    return kb_list
