FROM python:3.12.2-slim AS builder

WORKDIR /usr/src/src

COPY ./requirements.txt .
RUN apt-get update \
    && apt-get -y install openssh-client libpq-dev curl nano \
    && apt-get -y --no-install-recommends install build-essential \
    && apt-get clean 

# DBMATE
# RUN curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64
# RUN chmod +x /usr/local/bin/dbmate

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


FROM python:3.12.2-slim AS runner
WORKDIR /usr/src/src

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV TZ="America/Mexico_City"

COPY . .

CMD ["uvicorn", "src.fast_app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3001"]
