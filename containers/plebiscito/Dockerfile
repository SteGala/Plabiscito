FROM python:3.12.3

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src src
COPY deploy deploy

COPY main_container.py main.py

ENTRYPOINT ["python", "-u", "main.py"]
