# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for git tools
RUN apt update && apt install -y git && rm -rf /var/lib/apt/lists/*

# NEW: Copy requirements FIRST
COPY requirements.txt /app/

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY app.py /app/app.py
COPY .streamlit /app/.streamlit
COPY fonts /app/fonts

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]