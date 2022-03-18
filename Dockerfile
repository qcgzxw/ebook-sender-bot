FROM ubuntu:latest

LABEL MAINTAINER="qcgzxw<qcgzxw.com@gmail.com>"
ARG DEBIAN_FRONTEND=noninteractive

# Set Environment Variables
## App Mode
ENV APP_MODE dev
ENV MAX_SEND_LIMIT 10
## Database Infomation
ENV DB sqlite
ENV DB_NAME ebook_sender_bot
ENV DB_HOST localhost
ENV DB_PORT 3306
ENV DB_USER root
ENV DB_PASSWORD root
## Smtp Infomation
ENV SMTP_HOST ''
ENV SMTP_PORT ''
ENV SMTP_USERNAME ''
ENV SMTP_PASSWORD ''
## Telegram infomation
ENV BOT_TOKEN ''
ENV DEVELOPER_CHAT_ID ''

# Install Calibere And Python
RUN \
  apt-get update && \
  apt-get install -y curl pkg-config tzdata wget iputils-ping git libfontconfig libgl1-mesa-glx python3 python3-pip python3-pyqt5.qtmultimedia libnss3 && \
  pip3 install PyQtWebEngine && \
  wget --no-check-certificate -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sh /dev/stdin

# Setup App
WORKDIR /app
VOLUME /app
COPY . .
RUN \
  chmod +x docker/setup.sh && \
  python3 -m pip install --upgrade pip && \
  pip3 install -r requirements.txt && \
  touch default.log

# Run App
CMD ["/bin/bash", "/app/docker/setup.sh"]
