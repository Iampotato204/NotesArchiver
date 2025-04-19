import telebot
from telebot import types
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
# from N import *
# from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import importlib
import math
import os
import re
import requests
import time
# Archives
import shutil
import zipfile


import sql_handler as sql_h
# import translation as tr
from keyboards import *
from chat import *
# from tempfile import tempfile
# import tempfile as tempfile


API_TOKEN = '1234567890:abcdefghijklmnopqrstuvwxyzABCDEFGH'
bot = telebot.TeleBot(API_TOKEN)
print(f'INF: Bot info: {bot.get_me()}')
user_lang = "en"

def interactions_flag_get(tgid):
    return sql_h.SqlHandler().get_status(tgid)
def interactions_flag_update(user_id,status):
    return sql_h.SqlHandler().set_status(user_id,status)
def interactions_flag_clear():
    return sql_h.SqlHandler().flush_statuses()

def show_note(tgid, note_type, note_id):
    match note_type:
        case 1: # text
            textnote=db_handler.note_text_getnote(tgid,note_id)
            if textnote is None:
                bot.send_message(tgid, text='Note no longer exists')
                return
            sent_msg_id = bot.send_message(tgid, text=textnote[0]).message_id
        case 2: # file
            filenote=db_handler.note_file_getnote(tgid,note_id)
            print(f'DBG: filenote: {str(filenote)}, note_id={note_id}')
            if filenote is None:
                bot.send_message(tgid, text='Note no longer exists')
                return
            if filenote[3]=='___':
                filename=f'{filenote[2]}'
            else:
                filename=f'{filenote[2]}.{filenote[3]}'
            # file,caption,filename,extention
            # with tempfile.NamedTemporaryFile(delete=False, mode='w+') as written_blob:
                # temp_filename = written_blob.name
                # if received_blob is None:
                    # raise
                # written_blob.write(filenote[0])
                # written_blob.close()
                # with open(temp_filename, 'rb') as file_binary:
                    # db_handler.note_file_upload(tgid,file_binary,full_filename)
                    # db_handler.note_file_upload(tgid,file_binary,orig_filename)

                        
            with tempfile.TemporaryDirectory() as tmpdirname:
                filetosend_w = open(f'{tmpdirname}/{filename}', 'wb')
                filetosend_w.write(filenote[0])
                filetosend_w.close()
                filetosend = open(f'{tmpdirname}/{filename}', 'rb')
                dbcaption=str(filenote[1])
                if dbcaption=='_':
                    bot.send_document(chat_id=tgid, document=filetosend, visible_file_name=f'{filename}')
                else:
                    bot.send_document(chat_id=tgid, document=filetosend, caption=dbcaption, visible_file_name=f'{filename}')
                filetosend.close()
                # sent_msg_id = bot.send_document(user_id, text='temp',reply_markup=start_markup(0)).message_id
    
def get_chat_info(message):
    return {
        'timestamp': int(time.time()),
        'tg_user_id': message.from_user.id,
        'tg_user_username': message.from_user.username,
        'mirror': bot.get_me().username,
        'chat_id': 0     
    }

#sends only text if failed to load photo
def bot_safe_send_photo(tgid, text, photo_url, bottom_keyboard=None):
    try:
        bot.send_photo(tgid, caption=text, photo=photo_url, reply_markup=bottom_keyboard, parse_mode='html')
    except:
        bot.send_message(tgid, text=text, reply_markup=bottom_keyboard, parse_mode='html')

#########################################################################

@bot.message_handler(commands=['help', 'start']) # /start
def send_welcome(message):
    db_handler = sql_h.SqlHandler()
    tgid = message.from_user.id
    bot.reply_to(message, "Welcome, this is a notes bot", reply_markup=start_markup(0), parse_mode='html')
    interactions_flag_update(tgid,0)

@bot.message_handler(content_types=["text"])
def main(message):
    db_handler = sql_h.SqlHandler()
    # next_message_id = message.message_id + 1
    tgid = message.from_user.id
    print('TXT:', tgid, interactions_flag_get(tgid), message.text)
    communicate_text(db_handler, message, bot) # unclutter bot.py

@bot.message_handler(content_types=["document"])
def main(message):
    handle_file('document', message)
@bot.message_handler(content_types=["video"])
def main(message):
    # handle_file('video',message.from_user.id, message, bot.get_file(message.video.file_id))
    handle_file('video', message)
@bot.message_handler(content_types=["photo"])
def main(message):
    # for ph in message.photo: # has 4 images in different sizes: for 128748: 1920,23525,96614,128748
    # print('PHOTO:', tgid, interactions_flag_get(tgid), str(bot.get_file(ph.file_id)))
    # handle_file('photo',message.from_user.id, message, bot.get_file(message.photo[-1].file_id))
    handle_file('photo',message)

def handle_file(tag, message):
    db_handler = sql_h.SqlHandler()
    tgid = message.from_user.id
    # print('DOC:',tag,':', tgid, interactions_flag_get(tgid))
    communicate_file(db_handler, message, bot, tag) # unclutter bot.py
    
    

@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    db_handler = sql_h.SqlHandler()
    tgid = call.from_user.id

    # tag, type, id
    callback_data_list = call.data.split(",")
    callback_type = callback_data_list[0]
    note_type = int(callback_data_list[1])
    note_id = int(callback_data_list[2])
    print('CAL:', tgid, interactions_flag_get(tgid), len(call.data), str(callback_data_list))
    
    match callback_type:
        # only author of note can retrieve it, so there is no sense in getting tgid from callback
        case 'echonote': # tag, type, id
            show_note(tgid,note_type,note_id)
        case 'rmnote': # tag, type, id
            match note_type:
                case 1: # text
                    db_handler.note_delete(tgid,note_id,'text')
                case 2: # file
                    db_handler.note_delete(tgid,note_id,'file')
        case "categories":
            # callback_types_custom_tag_id
            match callback_data_list[7]:
                case "my_category_upload_file":
                    interactions_flag_update('wait_for_file_with_products', tgid, callback_data_list)
                    bot.send_message(tgid, text='Upload the file:')                    

                case "buy_keyboard_all_categories":
                    # shows shop-rating-shop category
                    list_with_categories = db_handler.get_categories_within(callback_data_list[2])
                    select_sub1_to_buy_from(tgid, list_with_categories)

        case "edit_category":
            match callback_data_list[1]:
                case 'rename':
                    bot.send_message(tgid, text='Enter the new title:', parse_mode='html')
                    print("Rename:", callback_data_list)
                    interactions_flag_update("edit_category_rename", tgid, callback_data_list)
                case 'change_description':
                    bot.send_message(tgid, text='Enter the new description:', parse_mode='html')
                    interactions_flag_update("edit_category_change_description", tgid, callback_data_list)

    match call.data:
        case 'seller_want_add_product':
            list_with_categories = db_handler.get_shop_categories_sorted(tgid)
            list_with_categories = filter(lambda el: (el[11] != 2), list_with_categories)
            reply_kb_list = categories_sub1_kb(0, tgid, list_with_categories, "my_category_upload_file", True)
            bot.send_message(tgid, text='Your Categories:', reply_markup=reply_kb_list)


if __name__ == '__main__':
    db_handler = sql_h.SqlHandler()
    print("INF: BOT STARTED")

    # interactions_flag_clear(user_id)
    # when bot is reset, we need to update the reply_markup keyboard. It can be applied only if message was sent
    for user_id in db_handler.get_all_users_ids():
        sent_msg_id = bot.send_message(user_id, text='temp',reply_markup=start_markup(0)).message_id
        #print('deleted? ',bot.delete_message(user_id[0], sent_msg_id))
    bot.infinity_polling(none_stop=True)