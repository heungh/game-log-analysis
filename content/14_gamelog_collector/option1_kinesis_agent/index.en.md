---
title: "Option 1: Kinesis Agent Installation"
weight: 10
---

# Kinesis Agent Installation Guide

Amazon Kinesis Agent is a standalone Java application that monitors log files and sends data to Amazon Kinesis Data Streams or Amazon Data Firehose.

## Prerequisites

- EC2 instance running Amazon Linux or Red Hat Enterprise Linux
- Appropriate IAM permissions for Kinesis services
- Java 8 or later installed

## Installation Steps

### 1. Install Kinesis Agent

```bash
sudo yum install –y aws-kinesis-agent
```

### 2. Configure the Agent

Edit the configuration file:

```bash
sudo vi /etc/aws-kinesis/agent.json
```

### 3. Start the Service

```bash
sudo service aws-kinesis-agent start
```

## Configuration

The agent configuration includes:
- Log file paths to monitor
- Destination Kinesis stream or Firehose delivery stream
- Data transformation rules
- Monitoring and error handling settings

## Next Steps

Once configured, the Kinesis Agent will automatically monitor your game log files and stream them to your specified AWS destination for real-time processing and analysis.
