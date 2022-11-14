English | [简体中文](README-ZH.md)

# ebook-sender-bot
Send E-Book to kindle with Telegram Bot.

Try it: [https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)

> We wanted to let you know that starting August 2022, you’ll no longer be able to send MOBI (.mobi, .azw) files to your Kindle library. Any MOBI files already in your library will not be affected by this change. MOBI is an older file format and won’t support the newest Kindle features for documents. Any existing MOBI files you want to read with our most up-to-date features for documents will need to be re-sent in a compatible format.

> Compatible formats now include EPUB (.epub), which you can send to your library using your Send to Kindle email address. We’ll also be adding EPUB support to the free Kindle app for iOS and Android devices and the Send to Kindle desktop app for PC and Mac. 

## Usage

1. Open bot link:[https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)
2. Send */email your-kindle-email@kindle.com* to set your kindle email address.
3. Add bot email to your [Approved Personal Document E-mail](https://www.amazon.com/hz/mycd/myx#/home/settings/payment).
4. Send a supported document to this bot and check your Kindle.

## Support document format
### send directly
- doc 
- docx 
- rtf 
- html 
- htm 
- pdf
- epub

### convert to epub and send
- azw 
- azw1 
- azw3 
- azw4 
- fb2 
- lrf 
- kfx 
- pdb 
- lit
- txt 
- mobi

---

## Setup

### [recommended] docker-compose install
[docker-compose.yml](docker-compose.yml)
```shell
docker-compose up -d
```

### [recommended] docker install
```shell
docker run -d \
    --restart unless-stopped \
    --name ebook-sender-bot \
    -e TZ=Asia/Shanghai \
    -e APP_MODE=prod \
    -e MAX_SEND_LIMIT=10 \
    -e FORMAT=epub \
    -e SMTP_HOST={YOUR_SMTP_HOST} \
    -e SMTP_PORT={YOUR_SMTP_PORT} \
    -e SMTP_USERNAME={YOUR_SMTP_USERNAME} \
    -e SMTP_PASSWORD={YOUR_SMTP_PASSWORD} \
    -e BOT_TOKEN={YOUR_BOT_TOKEN} \
    -e DEVELOPER_CHAT_ID={YOUR_TELEGRAM_CHAT_ID} \
    -v `./ebooks/`:`/app/storage/` \
    -v `./default.log`:`/app/default.log` \
    qcgzxw/ebook-sender-bot
```

### source install
1. copy *config.ini.example* to *config.ini*
2. install requirements
```shell
pip3 install -r requirments.txt
```
3. [install calibre](https://calibre-ebook.com/download)
4. run main.py
```shell
python3 main.py
```

### config.ini
```ini
[default]
# mode: [dev] printf runtime log to console 
mode=dev
# Set a daily limit of e-mailing per user
email_send_limit=10
# database: sqlite,mysql,postgresql
database=sqlite

# when database is sqlite
[sqlite]
name=ebook-sender-bot

# when database is mysql
[mysql]
name=ebook-sender-bot
host=192.168.1.1
port=3306
user=root
password=root

# when database is postgresql
[postgresql]
name=ebook-sender-bot
host=192.168.1.1
port=5432
user=root
password=root

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

## Donate
<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
<input type="hidden" name="cmd" value="_s-xclick">
<table>
<tr><td><input type="hidden" name="on0" value="Sponsors">Sponsors</td></tr><tr><td><select name="os0">
	<option value="Buy Me A Beer">Buy Me A Beer $9.99 USD</option>
	<option value="Buy Me A VPS">Buy Me A VPS $19.99 USD</option>
	<option value="Buy Me A Keyboard">Buy Me A Keyboard $99.99 USD</option>
</select> </td></tr>
</table>
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----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-----END PKCS7-----">
<input type="image" src="https://www.paypalobjects.com/en_US/C2/i/btn/btn_buynowCC_LG.gif" border="0" name="submit" alt="PayPal - The safer, easier way to pay online!">
<img alt="" border="0" src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" width="1" height="1">
</form>

## Todo
- [x] docker
- [x] Send document to kindle email
- [x] mysql
- [x] document information
- [x] covert books with calibre
- [x] use configParse instead of os.getenv()
- [x] i18n
- [x] telegram MessageReply class
- [x] admin command
- [ ] unique email
- [ ] queue
- [ ] test case
