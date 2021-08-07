# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /app
WORKDIR /flask_website

# Copy the current directory contents into the container at /app
COPY . /flask_website

RUN python -m pip install --upgrade pip
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 4000 available to the world outside this container
EXPOSE 4000

# Define environment variable
ENV FLASK_APP flask_website
ENV FLASK_ENV development

# Run app.py when the container launches
CMD ["flask", "run", "--host", "0.0.0.0", "-p", "4000"]

