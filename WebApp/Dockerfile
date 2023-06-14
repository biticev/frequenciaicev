FROM python:3.11
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install --requirement ./requirements.txt
COPY . .
ENV TZ=America/Fortaleza
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezon
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]