FROM python:3.12

COPY requirements.txt /code/
WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

CMD ["sh", "-c", "python manage.py migrate && gunicorn app.wsgi:application --bind 0.0.0.0:8000"]
