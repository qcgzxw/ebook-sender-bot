[English](README.md) | 简体中文

## 【重要】：kindle将于2023年6月30日在中国停止Kindle电子书店的运营。
考虑到届时可能无法购买新电子书、使用send to kindle功能，在这里强烈建议大家将账号迁移至海外区。

- kindle已购书籍、个人文档批量下载：https://github.com/yihong0618/Kindle_download_helper
- kindle海外账号注册指南：https://bookfere.com/post/492.html

# ebook-sender-bot
一个能将电子书发送给你Kinlde的telegram机器人

免费使用：[https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)

> 我们希望通知您，从 2022 年 8 月开始，您将无法再将 MOBI（.mobi、.azw）文件发送至您的 Kindle 图书馆。Kindle 图书馆中已有的 MOBI 文件将不会受此变更的影响。MOBI 是一种较旧的文件格式，不支持最新的 Kindle 文档功能。如果想使用我们最新的文档功能阅读现有 MOBI 文件，您需要以兼容格式重新发送这些文件。

> 目前兼容的格式包括 EPUB（.epub），您可以使用“发送至 Kindle”的电子邮件地址将这些格式的文件发送至您的图书馆。我们还将在适用于 iOS 和安卓设备的免费 Kindle 阅读软件以及适用于 PC 和 Mac 的“发送至 Kindle”桌面应用中添加对 EPUB 的支持。     

## 用法

1. 打开机器人链接:[https://t.me/e_book_send_bot](https://t.me/e_book_send_bot)
2. 发送 */email email@kindle.com* 来设置你的kindle邮箱。kindle邮箱可以在 [个人文档设置](https://www.amazon.com/gp/digital/fiona/manage#/home/settings/payment) 页面找到
3. 添加机器人邮箱到 [已认可的发件人电子邮箱列表](https://www.amazon.com/gp/digital/fiona/manage#/home/settings/payment)
4. 发送支持类型的文档到机器人，然后在kindle首页刷新检查即可。

## 受支持的文档类型
### 直接发送
- doc 
- docx 
- rtf 
- html 
- htm 
- pdf
- epub

### 转换成mobi格式发送
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

## 安装
### 【推荐】docker-compose
[docker-compose.yml](docker-compose.yml)
```shell
docker-compose up -d
```

### 【推荐】docker
```shell
docker run -d \
    --restart unless-stopped \
    --name ebook-sender-bot \
    -e TZ=Asia/Shanghai \
    -e APP_MODE=prod \
    -e MAX_SEND_LIMIT=10 \
    -e FORMAT=epub \
    -e EMAIL_PROVIDER=config \
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

### 源代码安装(便于开发调试)
1. 复制 *config.ini.example* 到 *config.ini* 并修改你的配置
2. pip安装环境
```shell
pip3 install -r requirments.txt
```
3. [安装calibre](https://calibre-ebook.com/download)
4. 运行
```shell
python3 main.py
```

### config.ini
```ini
[default]
# 模式: [dev] dev开发模式下日志直接控制台输出 
mode = dev
# 设置每个用户每天最多使用的次数
email_send_limit = 10
# database: sqlite,mysql,postgresql
database=sqlite
# email_provider: config,mailcow,mailcow_alias
email_provider=config

# 当database为sqlite时
[sqlite]
name=ebook-sender-bot

# 当database为mysql时
[mysql]
name=ebook-sender-bot
host=192.168.1.1
port=3306
user=root
password=root

# 当database为postgresql时
[postgresql]
name=ebook-sender-bot
host=192.168.1.1
port=5432
user=root
password=root

[smtp]
host=smtp.qq.com
port=465
username=your_email_address
password=your_email_account_password

# 当email_provider为mailcow或mailcow_alias时
[provider]
mailcow_url=your_mailcow_url
mailcow_api_key=mailcow_admin_api_key
mailcow_mailbox_domain=mailcow_mailbox_domain


[telegram]
# telegram tg_bot token
bot_token=your_telegram_bot_token
# your telegram chat id
developer_chat_id=your_telegram_chat_id
```

## 预览
![telegram-bot](https://cdn.jsdelivr.net/gh/image-backup/qcgzxw-images@master/image/16344769229431634476922938.png)
![kindle](https://cdn.jsdelivr.net/gh/image-backup/qcgzxw-images@master/image/16344842508421634484250830.png)

## 捐赠
https://afdian.com/a/ebook-sender-bot

## Todo
- [x] Docker直装
- [x] 发送文档到kindle邮箱
- [x] mysql支持
- [x] 书籍文件信息
- [x] 书籍文件转换
- [x] use configParse instead of os.getenv()
- [x] 多语言
- [x] 封装 messageReply 类
- [X] 管理员命令
- [X] 单用户单邮箱
- [ ] 发件邮箱抽离出来，配置保存数据库
- [ ] 更换ORM
- [ ] 测试实例
- [ ] 队列
