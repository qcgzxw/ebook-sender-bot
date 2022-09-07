#!/usr/bin/env bash
set -e
cp /app/docker/config.ini /app/config.ini
for name in APP_MODE MAX_SEND_LIMIT DB FORMAT DB_NAME DB_HOST DB_PORT DB_USER DB_PASSWORD SMTP_HOST SMTP_PORT SMTP_USERNAME SMTP_PASSWORD BOT_TOKEN DEVELOPER_CHAT_ID
do
    eval value=\$$name
    sed -i "s|\${${name}}|${value}|g" /app/config.ini
done

python3 /app/main.py
