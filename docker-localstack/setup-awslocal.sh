#!/bin/bash

# AWS_REGION is being overwritten by localstack on startup, the other environement vars passed in are respected
# This should be addressed in a future release https://github.com/localstack/localstack/issues/11387
AWS_REGION=eu-west-2
AWS_DEFAULT_REGION=eu-west-2

function create_aws_bucket {
  if awslocal s3 ls | grep -q "$1"; then
    echo "Bucket already exists!"
  else
    awslocal s3api \
    create-bucket --bucket "$1" \
    --create-bucket-configuration LocationConstraint=$AWS_REGION \
    --region $AWS_REGION
    echo "Created Bucket $1!"
    awslocal s3api \
    put-bucket-cors --bucket "$1" \
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
}

function create_sqs_queue {
  QUEUE_NAME="$1"
  DLQ_QUEUE_NAME="$2"
  MAX_RECEIVE_COUNT="$3"

  if awslocal sqs list-queues | grep -q $DLQ_QUEUE_NAME; then
    echo "$DLQ_QUEUE_NAME already exists!"
  else
    DLQ_QUEUE_URL=$(awslocal sqs create-queue --queue-name $DLQ_QUEUE_NAME --region $AWS_REGION --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
    echo "Created DLQ: $DLQ_QUEUE_URL!"
  fi

  if awslocal sqs list-queues | grep -q $QUEUE_NAME; then
    echo "$QUEUE_NAME already exists!"
  else
    SQS_QUEUE_URL=$(awslocal sqs create-queue --queue-name $QUEUE_NAME --region $AWS_REGION --attributes FifoQueue=true --output json | grep -o '"QueueUrl": "[^"]*' | awk -F'"' '{print $4}')
    DLQ_QUEUE_ARN="arn:aws:sqs:$AWS_REGION:000000000000:$DLQ_QUEUE_NAME"

    # configure DLQ for current queue
    awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL \
    --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_QUEUE_ARN\\\",\\\"maxReceiveCount\\\":\\\"$MAX_RECEIVE_COUNT\\\"}\"}"

    # set DeduplicationScope='queue', ensures strict message uniqueness across the entire queue
    awslocal sqs set-queue-attributes --queue-url $SQS_QUEUE_URL --attributes DeduplicationScope=queue

    echo "Created SQS Queue: $SQS_QUEUE_URL!"
  fi
}

# <- Pre-award environment ->

# Create buckets using awslocal
for bucket in "$AWS_BUCKET_NAME" "$AWS_MSG_BUCKET_NAME"; do
  create_aws_bucket "$bucket"
done

create_sqs_queue "$AWS_SQS_NOTIFICATION_APP_QUEUE_NAME" "$AWS_DLQ_NOTIFICATION_APP_QUEUE_NAME"  "$AWS_DLQ_MAX_RECEIVE_COUNT"
# <- Pre-award environment ->


# <- Post-award environment ->
for bucket in ${AWS_S3_BUCKET_FAILED_FILES} ${AWS_S3_BUCKET_SUCCESSFUL_FILES} ${AWS_S3_BUCKET_FIND_DOWNLOAD_FILES}; do
  create_aws_bucket "$bucket"
done
# <- Post-award environment ->
