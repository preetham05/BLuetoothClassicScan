FROM python:3.7

RUN apt-get update && apt-get install -y \
    bluez \
    dbus


RUN apt-get install -y bluez bluetooth libbluetooth-dev

WORKDIR /app

LABEL maintainer="Preetham Kannan (preetham.kannan@zigpos.com)"
LABEL version="$VERSION"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#

# setup startup script
COPY entrypoint.sh .
RUN ["chmod", "+x", "entrypoint.sh"]
CMD ["python3", "BTScanner.py"]
