# ebook-sender-bot
Send E-Book to kindle with Telegram Bot.

[https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)

## Usage
1. copy *.env.example* to *.env*
2. install requirements
```shell
pip install -r requirments.txt
```
3. run main.py
```shell
python main.py
```

## env
```dotenv
# Develop mode: printf runtime log to console 
DEV=True

# Database link: 
# SQLite: sqlite:///database.db
# Mysql: mysql://root:root@192.168.50.121:3306/tg_bot_kindle
# more databast support:
#    https://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url
DATABASE=mysql://root:root@192.168.50.121:3306/tg_bot_kindle

# SMTP account
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USERNAME=
SMTP_PASSWORD=

# telegram bot token
TELEGRAM_TOKEN=

# your telegram chat id
TELEGRAM_DEVELOP_CHAT_ID=

# Set a daily limit of e-mailing per user
EMAIL_SEND_LIMIT=10

# first, install calibre
# secend, open 'cmd' in windows or 'terminal' in linux,
# type 'ebook-meta.exe' in windows or 'ebook-meta' in linux and check this command if exists
# FYI:
#    Windows:ebook-meta.exe
#    Linux:ebook-meta
SHELL_CALIBRE_EBOOK_META=ebook-meta.exe

# FYI:
#    Windows:ebook-convert.exe
#    Linux:ebook-convert
SHELL_CALIBRE_EBOOK_CONVERT=ebook-convert.exe
```

## Preview
![telegram-bot](https://cdn.jsdelivr.net/gh/image-backup/qcgzxw-images@master/image/16344769229431634476922938.png)
![kindle](https://cdn.jsdelivr.net/gh/image-backup/qcgzxw-images@master/image/16344842508421634484250830.png)

## Todo
- [x] Send document to kindle email
- [x] mysql
- [x] document information
- [x] covert books with calibre
- [ ] i18n
- [ ] use config.get() instead of os.getenv()
- [ ] telegram MessageReply class
- [ ] test case
- [ ] queue
