FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY src main.py ./
CMD ["python", "main.py"]

