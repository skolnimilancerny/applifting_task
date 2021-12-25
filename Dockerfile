FROM alpine:latest

RUN apk add --update --no-cache python3 \
    && ln -sf python3 /usr/bin/python \
    && python3 -m ensurepip \
    && pip3 install --no-cache --upgrade pip setuptools \
    && mkdir "app"

COPY run.py requirements.txt ./

RUN pip3 --no-cache-dir install -r requirements.txt

ENV OFFERS_URL=https://applifting-python-excercise-ms.herokuapp.com/api/v1
ENV ACCESS_TOKEN=e22203f9-ec14-4fd5-a106-0e98b4a96b16

WORKDIR /app

COPY /app/* .

WORKDIR ../

EXPOSE 5000

ENTRYPOINT ["python3"]

CMD ["run.py"]