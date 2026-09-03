#!/bin/bash

NAMESPACE="OpsPilot"
METRIC_NAME="DemoApiHealth"
REGION="${AWS_REGION:-us-east-1}"

if systemctl is-active --quiet demo-api; then
    VALUE=1
else
    VALUE=0
fi

aws cloudwatch put-metric-data \
  --namespace "$NAMESPACE" \
  --metric-data "MetricName=$METRIC_NAME,Value=$VALUE,Unit=Count" \
  --region "$REGION"

echo "Published $METRIC_NAME=$VALUE"
