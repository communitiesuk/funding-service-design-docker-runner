#!/bin/bash

# Create the bucket using awslocal
if awslocal s3 ls | grep -q $AWS_BUCKET_NAME; then
  echo "Bucket already exists!"
else
  awslocal s3api \
  create-bucket --bucket $AWS_BUCKET_NAME --region $AWS_REGION
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

# Create the bucket using awslocal for notification service
if awslocal s3 ls | grep -q $AWS_MSG_BUCKET_NAME; then
  echo "Bucket already exists!"
else
  awslocal s3api \
  create-bucket --bucket $AWS_MSG_BUCKET_NAME --region $AWS_REGION
  echo "Created Bucket $AWS_BUCKET_NAME!"
  awslocal s3api \
  put-bucket-cors --bucket $AWS_MSG_BUCKET_NAME \
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


# Create the Fifo SQS Queue & DLQ using awslocal
if awslocal sqs list-queues | grep -q $AWS_DLQ_IMPORT_APP_QUEUE_NAME; then
  echo "$AWS_DLQ_IMPORT_APP_QUEUE_NAME already exists!"
else
  DLQ_QUEUE_URL=$(awslocal sqs create-queue --queue-name $AWS_DLQ_IMPORT_APP_QUEUE_NAME --region $AWS_REGION --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  echo "Created DLQ: $DLQ_QUEUE_URL!"
fi

if awslocal sqs list-queues | grep -q $AWS_SQS_IMPORT_APP_QUEUE_NAME; then
  echo "$AWS_SQS_IMPORT_APP_QUEUE_NAME already exists!"
else
  SQS_QUEUE_URL=$(awslocal sqs create-queue --queue-name $AWS_SQS_IMPORT_APP_QUEUE_NAME --region $AWS_REGION --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  DLQ_QUEUE_ARN="arn:aws:sqs:$AWS_REGION:000000000000:$AWS_DLQ_IMPORT_APP_QUEUE_NAME"

  # configure DLQ for current queue
  awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_QUEUE_ARN\\\",\\\"maxReceiveCount\\\":\\\"$AWS_DLQ_MAX_RECIEVE_COUNT\\\"}\"}"

  # set DeduplicationScope='queue', ensures strict message uniqueness across the entire queue
  awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL --attributes DeduplicationScope=queue

  echo "Created SQS Queue: $SQS_QUEUE_URL!"
fi

# Create the Fifo SQS Queue & DLQ using awslocal for notification service
if awslocal sqs list-queues | grep -q $AWS_DLQ_NOTIFICATION_APP_QUEUE_NAME; then
  echo "$AWS_DLQ_NOTIFICATION_APP_QUEUE_NAME already exists!"
else
  DLQ_NOTIFICATION_QUEUE_URL=$(awslocal sqs create-queue --queue-name $AWS_DLQ_NOTIFICATION_APP_QUEUE_NAME --region $AWS_REGION --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  echo "Created DLQ: $DLQ_NOTIFICATION_QUEUE_URL!"
fi

if awslocal sqs list-queues | grep -q $AWS_SQS_NOTIFICATION_APP_QUEUE_NAME; then
  echo "$AWS_SQS_NOTIFICATION_APP_QUEUE_NAME already exists!"
else
  SQS_NOTIFICATION_QUEUE_URL=$(awslocal sqs create-queue --queue-name $AWS_SQS_NOTIFICATION_APP_QUEUE_NAME --region $AWS_REGION --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
  DLQ_NOTIFICATION_QUEUE_ARN="arn:aws:sqs:$AWS_REGION:000000000000:$AWS_DLQ_NOTIFICATION_APP_QUEUE_NAME"

  # configure DLQ for current queue
  awslocal sqs set-queue-attributes --queue-url $SQS_NOTIFICATION_QUEUE_URL \
  --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_NOTIFICATION_QUEUE_ARN\\\",\\\"maxReceiveCount\\\":\\\"$AWS_DLQ_NOTIFICATION_MAX_RECIEVE_COUNT\\\"}\"}"

  # set DeduplicationScope='queue', ensures strict message uniqueness across the entire queue
  awslocal sqs set-queue-attributes --queue-url $SQS_NOTIFICATION_QUEUE_URL --attributes DeduplicationScope=queue

  echo "Created SQS Queue: $SQS_NOTIFICATION_QUEUE_URL!"
fi
