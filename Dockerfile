## Base 이미지 선택. 파이썬 애플리케이션임으로 파이썬3 이미지 선택.
FROM python:3

WORKDIR /usr/src/app

## Install packages
COPY requirements.txt ./
RUN pip install -r requirements.txt

## Copy src files needed to run the api
COPY app.py .
COPY config.py .
COPY test_endpoints.py .
COPY setup.py .

## Run the application on the port 5000
EXPOSE 5000

## Config settings
CMD ["python", "./setup.py", "runserver", "--host=0.0.0.0"]
