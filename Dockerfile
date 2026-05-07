FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "-c", "python app/services/init_qdrant.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]