# Use Ubuntu as the base image
FROM ubuntu:20.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list, install Python 3, pip, and necessary GObject libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgirepository1.0-dev \
    libcairo2-dev \
    gir1.2-gtk-3.0

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the port your application uses
EXPOSE 1234

# Define the command to run your application
CMD ["python3", "app.py"]
