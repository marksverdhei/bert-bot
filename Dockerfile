FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["python3", "bot.py"]
