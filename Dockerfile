# Use official Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy project files to container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout=100 -r requirements.txt

# Expose the application port (assuming FastAPI runs on 8000)
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
