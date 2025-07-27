---
title: "Option 2: Vector Installation"
weight: 20
---

# Vector Installation Guide

Vector is a high-performance observability data pipeline that can collect, transform, and route logs, metrics, and traces. It's a modern tool designed for efficient data processing.

## Prerequisites

- Linux-based system (Amazon Linux 2, Ubuntu, etc.)
- Appropriate IAM permissions for AWS services
- Network connectivity to AWS services

## Installation Steps

### 1. Download and Install Vector

For Amazon Linux 2:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.vector.dev | bash
```

### 2. Create Configuration File

Create a Vector configuration file:

```bash
sudo mkdir -p /etc/vector
sudo vi /etc/vector/vector.toml
```

### 3. Configure Vector Service

```bash
sudo systemctl enable vector
sudo systemctl start vector
```

## Configuration

Vector uses TOML configuration format with three main components:
- **Sources**: Where data comes from (log files, metrics, etc.)
- **Transforms**: How to process and modify the data
- **Sinks**: Where to send the processed data (AWS services, databases, etc.)

## Key Features

- High performance and low resource usage
- Rich data transformation capabilities
- Built-in observability and monitoring
- Support for multiple data formats and protocols

## Next Steps

Configure Vector to monitor your game logs and send them to AWS services like Kinesis, S3, or OpenSearch for analysis and visualization.
