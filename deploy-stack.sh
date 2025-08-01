#!/bin/bash

# Game Log Analytics Stack Deployment Script
# This script deploys the CloudFormation stack with proper parameters

STACK_NAME="game-log-stack"  # Shorter name to avoid S3 bucket name length issues
TEMPLATE_FILE="integrated-data-pipeline-stack-us-east-1.yaml"
REGION="us-east-1"

# Check if required parameters are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <KeyPairName> <VpcId> [SubnetId] [AllowedCidr]"
    echo ""
    echo "To find your VPC ID and Subnet ID, run:"
    echo "  aws ec2 describe-vpcs --region us-east-1"
    echo "  aws ec2 describe-subnets --region us-east-1"
    echo ""
    echo "To list your key pairs:"
    echo "  aws ec2 describe-key-pairs --region us-east-1"
    exit 1
fi

KEY_PAIR_NAME=$1
VPC_ID=$2
SUBNET_ID=${3:-""}  # Optional, will prompt if not provided
ALLOWED_CIDR=${4:-"0.0.0.0/0"}  # Default to open access

# If subnet not provided, try to get the first available subnet in the VPC
if [ -z "$SUBNET_ID" ]; then
    echo "Getting available subnets for VPC $VPC_ID..."
    SUBNET_ID=$(aws ec2 describe-subnets \
        --region $REGION \
        --filters "Name=vpc-id,Values=$VPC_ID" \
        --query 'Subnets[0].SubnetId' \
        --output text)
    
    if [ "$SUBNET_ID" = "None" ] || [ -z "$SUBNET_ID" ]; then
        echo "Error: No subnets found in VPC $VPC_ID"
        exit 1
    fi
    echo "Using subnet: $SUBNET_ID"
fi

echo "Deploying CloudFormation stack..."
echo "Stack Name: $STACK_NAME"
echo "Template: $TEMPLATE_FILE"
echo "Region: $REGION"
echo "Key Pair: $KEY_PAIR_NAME"
echo "VPC ID: $VPC_ID"
echo "Subnet ID: $SUBNET_ID"
echo "Allowed CIDR: $ALLOWED_CIDR"
echo ""

# Deploy the stack
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --parameters \
        ParameterKey=KeyPairName,ParameterValue=$KEY_PAIR_NAME \
        ParameterKey=VpcId,ParameterValue=$VPC_ID \
        ParameterKey=SubnetId,ParameterValue=$SUBNET_ID \
        ParameterKey=AllowedCidr,ParameterValue=$ALLOWED_CIDR \
        ParameterKey=InstanceType,ParameterValue=t3.medium \
    --capabilities CAPABILITY_IAM \
    --region $REGION

if [ $? -eq 0 ]; then
    echo ""
    echo "Stack creation initiated successfully!"
    echo "Monitor the stack creation progress with:"
    echo "  aws cloudformation describe-stack-events --stack-name $STACK_NAME --region $REGION"
    echo ""
    echo "Or watch the stack status with:"
    echo "  watch 'aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query \"Stacks[0].StackStatus\"'"
else
    echo "Error: Failed to create stack"
    exit 1
fi
