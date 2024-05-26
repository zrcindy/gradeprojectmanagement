FROM python:3.9-alpine

RUN adduser --system app --home /app
USER app
WORKDIR /app
COPY ./ /app

RUN pip3 install -r requirements.txt

CMD python3 app/app.py

EXPOSE 5000