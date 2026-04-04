FROM python:3.12-alpine

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY shim.py .

EXPOSE 3001

CMD ["python", "shim.py"]
