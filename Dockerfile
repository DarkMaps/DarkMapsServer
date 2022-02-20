FROM python:3.7-alpine

ADD requirements.txt /app/requirements.txt

RUN apk add --update alpine-sdk && apk add libffi-dev openssl-dev

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN set -ex \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install psycopg2-binary \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt

ADD . /app
WORKDIR /app

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "--worker-tmp-dir", "/dev/shm", "dark_maps.wsgi:application"]
