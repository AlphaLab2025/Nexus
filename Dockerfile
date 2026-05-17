# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your app runs on (e.g., 8000 for FastAPI/Django, 5000 for Flask)
EXPOSE 8000

# Specify the command to run on container start
CMD ["python", "src/main.py"]
