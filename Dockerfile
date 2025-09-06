FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install gcc -y && apt-get clean

WORKDIR /app

COPY monitor monitor
COPY pyproject.lock .

RUN pip install -r pyproject.lock

CMD ["python", "-m", "monitor"]
