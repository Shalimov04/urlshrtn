FROM python:3.12

COPY requirements.txt /code/
WORKDIR /code
RUN pip install -r requirements.txt

COPY . /code/

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
