FROM python:3


ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /mediators
WORKDIR /mediators
COPY ./mediators /mediators


COPY . /code

RUN python manage.py makemigrations
RUN python manage.py migrate

RUN ["python3", "manage.py", "runserver"]

