FROM python:3.12.9-slim

RUN apt-get update && apt-get install -y netcat-openbsd \
    libpq-dev


COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app/
WORKDIR /app

ENV PYTHONPATH=/steamate 

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
