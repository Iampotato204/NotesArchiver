# NotesArchiver
Telegram bot for managing notes in Python : https://t.me/NotesArchiver_bot<br>
Will not be available all the time, message me or build it yourself, if you want to see it in action

Demonstrational video:
<video src="https://github.com/user-attachments/assets/9c954338-6348-4754-86ec-0c9486ae584d"></video>

Build:
- Create user in database and give him necessary permissions (insert,update,delete,select on all tables).
- Change API_TOKEN in bot.py and database user credentials in sql_handler.py
- Run sql/create_db.sql in your database
- Install pyTelegramBotAPI (I installed in venv using pip)
- Run '/path_to_venv/bin/python3 /path_to_project/bot.py'
- Send '/start' to your bot
