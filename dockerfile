# 1. Specify the base image (e.g., node, python, alpine)
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy dependency files first to leverage build cache
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .


# 8. Define the command to run your app
CMD ["python", "main.py"]
  