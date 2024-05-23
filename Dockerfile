FROM python:3.12.2-slim

WORKDIR /server
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

RUN alembic init source/database/migrations | echo "Alembic initialized, skipping"
COPY alembic.ini .
WORKDIR /server/source/database
COPY source/database/migrations .

WORKDIR /server
RUN mkdir -p logs
COPY . .

WORKDIR /server/source
#CMD while true; do echo "hello"; sleep 2; done
CMD alembic -c ../alembic.ini upgrade head && python main.py > ../logs/main.log