# Use Ubuntu base image
FROM ubuntu:22.04

# Set environment variables for non-interactive apt
ENV DEBIAN_FRONTEND=noninteractive

# Install python3.10, pip and other dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
RUN mkdir /app
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the app files
COPY . /app

# Expose port
EXPOSE 8000

# Run the app with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]