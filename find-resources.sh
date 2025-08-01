#!/bin/bash

# Helper script to find AWS resources needed for deployment

REGION="us-east-1"

echo "=== Finding AWS Resources for Game Log Analytics Stack ==="
echo ""

echo "1. Available Key Pairs:"
aws ec2 describe-key-pairs --region $REGION --query 'KeyPairs[*].KeyName' --output table

echo ""
echo "2. Available VPCs:"
aws ec2 describe-vpcs --region $REGION --query 'Vpcs[*].[VpcId,CidrBlock,State,Tags[?Key==`Name`].Value|[0]]' --output table

echo ""
echo "3. Available Subnets (showing first 10):"
aws ec2 describe-subnets --region $REGION --query 'Subnets[0:9].[SubnetId,VpcId,CidrBlock,AvailabilityZone,Tags[?Key==`Name`].Value|[0]]' --output table

echo ""
echo "=== Usage Instructions ==="
echo "Once you have the information above, deploy the stack with:"
echo "./deploy-stack.sh <KeyPairName> <VpcId> [SubnetId] [AllowedCidr]"
echo ""
echo "Example:"
echo "./deploy-stack.sh my-key-pair vpc-12345678 subnet-87654321 10.0.0.0/16"
