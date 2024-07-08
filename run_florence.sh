#!/bin/bash

# Stop script on any error
set -e

# Define variables
DOCKERFILE="Localmodel.Dockerfile"
IMAGE_NAME="florence-fastapi-image"
CONTAINER_NAME="florence-fastapi-container"
PORT=8989

echo "Building Docker image..."
docker build -f $DOCKERFILE -t $IMAGE_NAME .

echo "Docker image built successfully."

# Check if a container with the same name is already running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

echo "Running Docker container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    --gpus all \
    $IMAGE_NAME

echo "Docker container is now running."
echo "You can access the API at http://localhost:$PORT after the model is loaded."
