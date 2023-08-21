#!/bin/bash

# Create the bucket using awslocal
if awslocal s3 ls | grep -q $AWS_BUCKET_NAME; then
  echo "Bucket already exists!"
else
  # awslocal s3 mb s3://$AWS_BUCKET_NAME --region $AWS_REGION
  awslocal s3api \
  create-bucket --bucket $AWS_BUCKET_NAME \
  --create-bucket-configuration LocationConstraint=$AWS_REGION \
  --region $AWS_REGION
  echo "Created Bucket $AWS_BUCKET_NAME!"
  awslocal s3api \
  put-bucket-cors --bucket $AWS_BUCKET_NAME \
  --cors-configuration '{
    "CORSRules": [
      {
        "AllowedOrigins": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
        "AllowedHeaders": ["*"]
      }
    ]
  }'
  echo "Created CORS rule!"
fi


# Create the SQS Queue using awslocal
if awslocal sqs list-queues | grep -q $AWS_SQS_QUEUE_NAME; then
  echo "$AWS_SQS_QUEUE_NAME already exists!"
else
  awslocal sqs create-queue --queue-name $AWS_SQS_QUEUE_NAME --region $AWS_REGION
  echo "Created SQS Queue: $AWS_SQS_QUEUE_NAME!"
fi