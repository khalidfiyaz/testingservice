#image
FROM python:3.9-slim

# Setting the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install packages in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Making port 5000 available to the world outside this container
EXPOSE 5000

#environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "backend.py"]
