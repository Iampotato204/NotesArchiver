import telebot
from telebot import types
from random import randint
import random

import sql_handler as sql_h
# import money_handler as money

def start_markup(user_rank=0, *kwargs): 
    print(f'USERRANK: {user_rank}')
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

def main_categories_kb(pagenum, mes_id):  #  generate_inline_kb_categories
    if pagenum < 0:
        return 35505
    quantity_row = 7
    kb_categories_list = types.InlineKeyboardMarkup(row_width=1)
    list_with_categories = db_handler.get_categories_within()
    pages_total = math.ceil(len(list_with_categories) / quantity_row)
    for i in list_with_categories[pagenum: pagenum + quantity_row]:
        #print(f'ITERATION_CATEGORIES={i}___type={type(i)}')
        button = types.InlineKeyboardButton(text=f'{i[5]}', callback_data=f'categories,{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{mes_id}')
        kb_categories_list.row(button)
    
    return kb_categories_list

def categories_kb(pagenum, mes_id, list_with_categories, custom_tag='empty'):
    kb_list = types.InlineKeyboardMarkup(row_width=1)
    for i in list_with_categories:
        button = types.InlineKeyboardButton(text=f'{i[5]}', callback_data=f'categories,{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},,{custom_tag}')
        kb_list.row(button)

    return kb_list

def categories_sub1_kb(pagenum, mes_id, list_with_categories, custom_tag='empty', clickable_categories=False):
    kb_list = types.InlineKeyboardMarkup(row_width=1)
    
    if clickable_categories:
        for i in list_with_categories:
            main = db_handler.get_category(i[1], 0, 0)
            button1 = types.InlineKeyboardButton(text=f'{main[5]}', callback_data="empty")
            button2 = types.InlineKeyboardButton(text=f'<{category_type_index_to_label[i[11]]}> {i[5]}', callback_data=f'categories,{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},,{custom_tag}')
            kb_list.row(button1, button2)
    else:
        for i in list_with_categories:
            main = db_handler.get_category(i[1], 0, 0)
            button1 = types.InlineKeyboardButton(text=f'{main[5]}', callback_data="empty")
            button2 = types.InlineKeyboardButton(text=f'<{category_type_index_to_label[i[11]]}> {i[5]}', callback_data='empty')
            kb_list.row(button1, button2)

    return kb_list

def categories_table_kb(pagenum, mes_id, list_with_categories, custom_tag='empty'):
    kb_list = types.InlineKeyboardMarkup(row_width=1)
    buttons_list = []
    items_per_page = 10
    start =  pagenum * items_per_page
    end = start + items_per_page

    if list_with_categories == []:
        return None
    
    for i in list_with_categories:
        temp_shop = db_handler.get_shop(i[0])
        if temp_shop is None:
            print("Tried to access category that is not a shop")
            continue
        rating_as_shop = money.rating(temp_shop.rating_asShop_sum, temp_shop.rating_asShop_count)
        button1 = types.InlineKeyboardButton(text=f"{rating_as_shop} {db_handler.get_shop_name(i[0])[0]}", callback_data='empty')
        button2 = types.InlineKeyboardButton(text=f'<{category_type_index_to_label[i[11]]}> {i[5]}', callback_data=f'categories,{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},,{custom_tag}')

        buttons_list.append([button1, button2])

    print("---- Button List ----", buttons_list)
    for btn1, btn2 in buttons_list[start:end]:
        kb_list.row(btn1, btn2)

    if pagenum > 0:
        kb_list.row(types.InlineKeyboardButton(text=f'Back', callback_data=f'back,{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{pagenum-1},{custom_tag}'))

    if end < len(buttons_list):
        kb_list.row(types.InlineKeyboardButton(text=f'Forward', callback_data=f'forward,{i[0]},{i[1]},{i[2]},{i[3]},{i[4]},{pagenum+1},{custom_tag}'))

    return kb_list 

def new_note_kb():
    newnote_kb = types.InlineKeyboardMarkup(row_width=1)
    _button = types.InlineKeyboardButton(text='Buy', callback_data=f'{",".join(data)}') # if data arr contains ints, this will fail
    # cancel_button = types.InlineKeyboardButton(text='Cancel', callback_data='empty')

    kb_list.row(buy_button)

    return kb_list

def choose_category_type(list_with_categories):
    choose_kb = types.InlineKeyboardMarkup(row_width=1)

    print("Choose cat type kb: ", list_with_categories)

    # btn_product = types.InlineKeyboardButton(text="Products", callback_data=f'add_shops_category,products,{list_with_categories}')
    # btn_service = types.InlineKeyboardButton(text="Services", callback_data=f'add_shops_category,services,{list_with_categories}')
    btn_product_text = types.InlineKeyboardButton(text="Lines as Products", callback_data=f'categories,,{list_with_categories[2]},{list_with_categories[3]},{list_with_categories[4]},,,add_shops_category,p_t')
    btn_product_files = types.InlineKeyboardButton(text="Files as Products", callback_data=f'categories,,{list_with_categories[2]},{list_with_categories[3]},{list_with_categories[4]},,,add_shops_category,p_f')
    btn_service = types.InlineKeyboardButton(text="Services", callback_data=f'categories,,{list_with_categories[2]},{list_with_categories[3]},{list_with_categories[4]},,,add_shops_category,_s_')

    choose_kb.row(btn_product_text)
    choose_kb.row(btn_product_files)
    choose_kb.row(btn_service)

    return choose_kb

def edit_category_kb(temp_category, custom_tag="empty"):
    edit_kb = types.InlineKeyboardMarkup(row_width=1)
    print(temp_category)
    # callback_data:
        # 0 Type
        # 1 Command
        # 2 Shop ID
        # 3 Main_cat
        # 4 Cat1
        # 5 cat2=0
    btn_title       = types.InlineKeyboardButton(text=f'Title: {temp_category[5]}',             callback_data=f'edit_category,change_title,         {temp_category[0]},{temp_category[1]},{temp_category[2]},{temp_category[3]}'),
    btn_description = types.InlineKeyboardButton(text=f'Description: {temp_category[6]}',       callback_data=f'edit_category,change_description,   {temp_category[0]},{temp_category[1]},{temp_category[2]},{temp_category[3]}'),
    btn_price       = types.InlineKeyboardButton(text=f'Price per Unit: {money.cents_to_usdstr(temp_category[9])}', callback_data=f'edit_category,change_price,         {temp_category[0]},{temp_category[1]},{temp_category[2]},{temp_category[3]}'),
    btn_url         = types.InlineKeyboardButton(text=f'URL: {temp_category[8]}',               callback_data=f'edit_category,change_url,           {temp_category[0]},{temp_category[1]},{temp_category[2]},{temp_category[3]}'),
    btn_format      = types.InlineKeyboardButton(text=f'Format: {temp_category[7]}',            callback_data=f'edit_category,change_format,        {temp_category[0]},{temp_category[1]},{temp_category[2]},{temp_category[3]}'),

    btn_list = [
        btn_title,
        btn_description,
        btn_price,
        btn_url,
        btn_format
    ]
    # edit_kb.row(button)
    for idx, btn in enumerate(btn_list):
        edit_kb.row(btn[0])

    return edit_kb

def sellers_shop_list(all_shop_names):
    shop_list = types.InlineKeyboardMarkup(row_width=1)

    for shop in all_shop_names:
        btn_name = types.InlineKeyboardButton(text=f"{shop['shop_name']}", callback_data=f'empty')
        btn_action = types.InlineKeyboardButton(text=f"View", callback_data=f"view_shop_categories,{shop['shop_id']}")

        shop_list.row(btn_name, btn_action)
        print(shop)

    return shop_list
