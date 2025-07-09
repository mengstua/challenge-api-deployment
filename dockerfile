FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app

COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Create a non-root user
RUN useradd -m repl
USER repl

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
