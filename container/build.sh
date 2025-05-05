#!/usr/bin/env bash
source .dockerenv

# Get the latest Docker image ID
latest_id=$(docker images --format "{{.ID}}" --filter=reference="${IMAGE_NAME}:latest" | head -n 1)

# Build the new image
docker build --rm -t "${IMAGE_NAME}" .
success=$?

# Get the new latest Docker image ID
new_id=$(docker images --format "{{.ID}}" --filter=reference="${IMAGE_NAME}:latest" | head -n 1)

# Check if the build was successful
if [ $success -eq 0 ]; then
    # Check if the new ID differs from the previous one
    if [ "$latest_id" != "$new_id" ]; then
        # Remove the previous Docker image
        if [ ! -z "$latest_id" ]; then
            docker rmi "$latest_id"
        else
            echo "Previous image ID not found or no previous image exists."
            echo "$latest_id"
        fi
    else
        echo "New image does not differ from the previous one."
        echo "Latest ID: $latest_id"
        echo "New ID: $new_id"
    fi
else
    echo "Docker build failed."
fi

echo "Build success: $success"
