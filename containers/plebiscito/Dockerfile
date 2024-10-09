from python:3.12.3

COPY src src
COPY deploy deploy
COPY requirements.txt requirements.txt
COPY main_container.py main.py

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
