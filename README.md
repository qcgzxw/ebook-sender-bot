# ebook-sender-bot
Send E-Book to kindle with Telegram Bot.

[https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)

## Usage
1. copy *config.ini.example* to *config.ini*
2. install requirements
```shell
pip install -r requirments.txt
```
3. [install calibre](https://calibre-ebook.com/download)
4. run main.py
```shell
python main.py
```

## config.ini
```ini
[default]
# mode: [dev] printf runtime log to console 
mode = dev
# Set a daily limit of e-mailing per user
email_send_limit = 10
# for example:
#     SQLite[recommended]: sqlite:///database.db
#     Mysql[recommended]: mysql+pool://username:passwordroot@127.0.0.1:3306/ebook_sender_bot?max_connections=20&stale_timeout=300
#     Mysql: connection pool: mysql://username:password@127.0.0.1:3306/ebook_sender_bot
database = mysql+pool://root:root@127.0.0.1:3306/ebook_sender_bot?max_connections=20&stale_timeout=300

[smtp]
host=smtp.gmail.com
port=465
username=your_email_address
password=your_email_account_password

[telegram]
# telegram tg_bot token
bot_token=your_telegram_bot_token
# your telegram chat id
developer_chat_id=your_telegram_chat_id
```

## Preview
![telegram-bot](https://cdn.jsdelivr.net/gh/image-backup/qcgzxw-images@master/image/16344769229431634476922938.png)
![kindle](https://cdn.jsdelivr.net/gh/image-backup/qcgzxw-images@master/image/16344842508421634484250830.png)

## Todo
- [x] Send document to kindle email
- [x] mysql
- [x] document information
- [x] covert books with calibre
- [x] use configParse instead of os.getenv()
- [ ] i18n
- [ ] telegram MessageReply class
- [ ] test case
- [ ] queue
