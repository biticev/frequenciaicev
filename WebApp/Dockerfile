FROM python:3.11
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install --requirement ./requirements.txt
COPY . .
CMD ["python", "app.py"]