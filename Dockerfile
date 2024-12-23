FROM python:3.11.11-slim

RUN apt-get update -y && apt-get install ffmpeg -y

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip3 install --break-system-packages --ignore-installed --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash", "run.sh"]