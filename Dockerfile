# Start from the latest Debian image
FROM debian:11

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install any needed packages specified in requirements.txt
# COPY and RUN first to cache this layer
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
ADD . /nlim
WORKDIR /nlim

# Put the module in the path
RUN python3 setup.py develop
