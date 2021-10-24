# ebook-sender-bot
Send E-Book to kindle with Telegram Bot.

[https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)

## Usage
1. copy *.env.example* to *.env*
2. install requirements
```shell
pip install -r requirments.txt
```
3. [install calibre](https://calibre-ebook.com/download)
4. run main.py
```shell
python main.py
```

## env
```dotenv
# Develop mode: printf runtime log to console 
DEV=False

# Database link: 
#
# for example:
#     SQLite[recommend]: sqlite:///database.db
#     Mysql[recommend]: mysql+pool://username:passwordroot@127.0.0.1:3306/ebook_sender_bot?max_connections=20&stale_timeout=300
#     Mysql: connection pool: mysql://username:password@127.0.0.1:3306/ebook_sender_bot
DATABASE=mysql+pool://root:root@127.0.0.1:3306/ebook_sender_bot?max_connections=20&stale_timeout=300

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
