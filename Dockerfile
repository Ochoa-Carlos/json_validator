FROM python:3.12.2-slim

WORKDIR /usr/src/src

COPY ./requirements.txt .
RUN apt-get update \
    && apt-get clean \
    && apt-get -y install openssh-client libpq-dev curl nano

# DBMATE
# RUN curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64
# RUN chmod +x /usr/local/bin/dbmate

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV TZ="America/Mexico_City"
ENV NAME .env

RUN pwd

COPY . .

CMD ["uvicorn", "src.fast_app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3001"]
