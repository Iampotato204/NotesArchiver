from keyboards import *
from datetime import datetime
import tempfile as tempfile
# unnecessary to store in db - load would be too high
# storing text flags in db also is stupid
# db calls will later be replaced with dictionary userID:status

# storing (number)status in db rather than in dictionary is better for dev stage,
# as dict is not persistent (surprise surprise), and bot is often reset
chat_flags={
    'clear':0,
    # 'standby':16,
    'newtextnote_entername':1000,
    'newtextnote_entertext':1001,
    'newfilenote_entername':2000,
    'newfilenote_enterfile':2001
}
rev_chat_flags = dict(reversed(item) for item in chat_flags.items())

def autoname():
    return datetime.today().strftime('%d%b_%H:%M') # len 11 for normal display of name
    # >>> datetime.today().strftime('%H:%M_%d%b')
    # '08:32_16Apr' #11
    # >>> datetime.today().strftime('%d%b_%H:%M')
    # '16Apr_08:38'
    # >>> datetime.today().strftime('%a%H:%M%b%d')
    # 'Wed08:29Apr16' #13
    # >>> datetime.today().strftime('%a%d%b_%H:%M')
    # 'Wed16Apr_08:33' #14
    # >>> datetime.today().strftime('%H:%M_%a%d%b%y')
    # '08:30_Wed16Apr25' #16

def interactions_flag_get(tgid):
    return sql_h.SqlHandler().get_status(tgid)
def interactions_flag_update(tgid,status_name):
    return sql_h.SqlHandler().set_status(tgid,chat_flags[status_name])
def interactions_flag_clear(tgid):
    return sql_h.SqlHandler().flush_statuses()
# drop-in replacement: # UPD: already NOT drop-in, but i may need data field in this dict later
# it stores text labels directly, without additional conversion to numbers
# interactions_flags = {}
# def interactions_flag_update(tgid, status_flag, _data):
    # interactions_flags.update({int(tgid) : {
            # 'status': status_flag,
            # 'data': _data
        # }})
# def interactions_flag_clear(tgid):
    # print("DEBUG: flag flushed for ",tgid)
    # interactions_flag_update('empty',tgid,'')
def new_note_name(db_handler,message,bot,_type='text'):
    tgid = message.from_user.id
    try:
        if(message.text=='q'):
            bot.send_message(tgid, text="(Cancelled)")
            interactions_flag_update(tgid,'clear')
            db_handler.note_delete(tgid,db_handler.note_last(tgid,_type),_type)
            return
        db_handler.note_setname(db_handler.note_last(tgid,_type), message.text, _type)
        interactions_flag_update(tgid,f'new{_type}note_enter{_type}')
        bot.send_message(tgid, text=f'Send {_type}:')
    except Exception as e:
        print('ERR',str(e))
        db_handler.note_delete(tgid,db_handler.note_last(tgid,_type),_type)
        bot.send_message(tgid, text="Wrong input(name)! (Or other error occured)")

def note_add_file(db_handler,message,bot,_file, orig_filename):
    tgid = message.from_user.id
    try:
        # text is also set, text itself is received from caption
        full_filename = _file.file_path.split('/')[-1]
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as written_blob:
            temp_filename = written_blob.name
            # Downloads file, bytes
            received_blob = bot.download_file(_file.file_path)
            # print('Downloaded:', type(received_blob), received_blob)
            if received_blob is None:
                raise
            written_blob.write(received_blob)
            written_blob.close()
            with open(temp_filename, 'rb') as file_binary:
                # db_handler.note_file_upload(tgid,file_binary,full_filename)
                db_handler.note_file_upload(tgid,db_handler.note_last(tgid,'file'),file_binary,orig_filename)
        # db_handler.note_settext(db_handler.note_last(tgid,'file'), message.text, 'file')
        interactions_flag_update(tgid,'clear')
        bot.send_message(tgid, text="Note created!")
    except Exception as e:
        print('ERR',str(e))
        db_handler.note_delete(tgid,db_handler.note_last(tgid,'file'),'file')
        bot.send_message(tgid, text="Failed to create file note")
        
def communicate_text(db_handler, message, bot):
    tgid = message.from_user.id

    #sent_msg_id = bot.send_message(tgid, text='temp',reply_markup=start_markup(user_rank)).message_id
    #print('deleted? ',bot.delete_message(tgid, sent_msg_id))

    # print('TEXT:', tgid, f'@{message.from_user.username}', message.text)
    match rev_chat_flags[interactions_flag_get(tgid)]:
        case 'newtextnote_entername': # 1000: # new note: enter name
            new_note_name(db_handler,message,bot,'text')
        case 'newfilenote_entername':
            new_note_name(db_handler,message,bot,'file')
        case 'newtextnote_entertext': # 1001: # new note: enter text
            try:
                db_handler.note_settext(db_handler.note_last(tgid,'text'), message.text,'text')
                interactions_flag_update(tgid,'clear')
                bot.send_message(tgid, text="Note created!")
            except Exception as e:
                print('ERR',str(e))
                bot.send_message(tgid, text="Wrong input(text)! (Or other error occured)")
        case _: # includes 'clear' tag
            match message.text:
                case 'My notes🗄':
                    # markup = types.InlineKeyboardMarkup()
                    # markup.add(types.InlineKeyboardButton("Show All Categories of notes", switch_inline_query_current_chat=""))
                    markup=mynotes_kb(tgid)
                    # print(str(markup))
                    # if(markup['keyboard']==0): # object is not subscriptable, although printed just as a dictionary, so can be parsed
                    if('Inline' in str(markup)):
                        bot.send_photo(chat_id=message.chat.id, photo=open('pics/note.png', 'rb'),reply_markup=markup)
                    else:
                        bot.send_message(tgid, text="You don`t have any notes!")
                case 'New note (text)⭐️':
                    bot.send_message(tgid, text="Name: ('q' to cancel)")
                    db_handler.note_new(tgid,'_','text')
                    interactions_flag_update(tgid, 'newtextnote_entername') #100000)
                case 'New note (file)⭐️':
                    bot.send_message(tgid, text="Name: ('q' to cancel)")
                    db_handler.note_new(tgid,'_','file')
                    interactions_flag_update(tgid, 'newfilenote_entername') #100000)
                case _: # or i could have just exited the function
                    # functionality of 'newtextnote_entername' tag and 'New note (text)⭐️' keyboard interaction
                    # upd: name no longer asked for, but generated
                    try:
                        notename = autoname()
                        db_handler.note_new(tgid, message.text,'text')
                        db_handler.note_setname(db_handler.note_last(tgid,'text'), notename,'text')
                        interactions_flag_update(tgid,'clear')
                        bot.send_message(tgid, text="New note:"+notename)
                    except Exception as e:
                        print('ERR',str(e))
                        bot.send_message(tgid, text="Failed to create a note")
####################################################################################

def communicate_file(db_handler, message, bot, doctype):
    tgid = message.from_user.id
    caption=''
    _file = None
    match doctype:
        case 'document':
            orig_filename = message.document.file_name
            _file = bot.get_file(message.document.file_id)
            caption = message.caption
        case 'video':
            orig_filename = message.video.file_name
            _file = bot.get_file(message.video.file_id)
            caption = message.caption
        case 'photo': # original filename can not be retrieved
            _file = bot.get_file(message.photo[-1].file_id)
            orig_filename = _file.file_path.split('/')[-1]
            caption = message.caption
        case _:
            print('ERR: doctype not implemented: ',doctype)
            return
    print('DOC:',doctype,':', tgid, interactions_flag_get(tgid),_file)
    match rev_chat_flags[interactions_flag_get(tgid)]:
        case 'newfilenote_enterfile':
            note_add_file(db_handler,message,bot,_file, orig_filename)
        case _:
            db_handler.note_new(tgid,'_','file')
            db_handler.note_setname(db_handler.note_last(tgid,'file'), autoname(), 'file')
            note_add_file(db_handler,message,bot,_file, orig_filename)
