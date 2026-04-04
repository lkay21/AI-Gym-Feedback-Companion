FROM python:3.11
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app.main:create_app()"]