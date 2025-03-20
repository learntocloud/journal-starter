
# Use a smaller base image
FROM python:3.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache for dependencies
COPY api/requirements.txt /app/

# Install dependencies, using --no-cache-dir to save space
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose the FastAPI port (default is 8000)
EXPOSE 8000

# Command to run the application with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


