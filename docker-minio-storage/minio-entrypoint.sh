#!/bin/sh

# # Wait for MinIO server to start
# while ! curl -f http://minio:9000; do
#   sleep 1
# done

# Create the bucket using mc (MinIO Client)
mc config host add myminio http://minio:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
if mc ls myminio | grep -q $AWS_BUCKET_NAME; then
  echo "Bucket already exists!"
else
  mc mb myminio/$AWS_BUCKET_NAME --region $AWS_REGION
fi

exec "$@"
