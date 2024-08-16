# Download k6 binary
FROM alpine as k6-downloader

RUN wget https://github.com/grafana/k6/releases/download/v0.43.1/k6-v0.43.1-linux-amd64.tar.gz && \
    tar -xvzf k6-v0.43.1-linux-amd64.tar.gz

# Build the Python application
FROM python:3.8-slim

# Install git to clone the repository
RUN apt-get update && apt-get install -y git

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Clone the booking microservice repository if the directory doesn't exist
RUN [ ! -d /app/booking-microservices ] && git clone https://github.com/meysamhadeli/booking-microservices || echo "Directory already exists"

# Copy k6 binary from the previous stage
COPY --from=k6-downloader /k6-v0.43.1-linux-amd64/k6 /usr/local/bin/k6

# Copy requirements.txt from your local directory to the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Command to run the application
CMD ["python", "/app/backend.py"]