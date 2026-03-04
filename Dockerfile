# 1️⃣ Use official Python image
FROM python:3.10-slim

# 2️⃣ Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# 3️⃣ Prevent Python from buffering stdout
ENV PYTHONUNBUFFERED=1

# 4️⃣ Set working directory
WORKDIR /app

# 5️⃣ Copy requirements file first
COPY requirements.txt /app/

# 6️⃣ Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 7️⃣ Copy the rest of the project
COPY . /app/

# 8️⃣ Expose port
EXPOSE 8000

# 9️⃣ Run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]