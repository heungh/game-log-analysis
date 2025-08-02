---
title: "Option 1: Kinesis Agent Installation"
weight: 10
---

# Kinesis Agent Installation Guide for Ubuntu 20.04

Amazon Kinesis Agent is a standalone Java application that monitors log files and sends data to Amazon Kinesis Data Streams or Amazon Data Firehose.

## Prerequisites

- Ubuntu 20.04 LTS EC2 instance
- Java 8 or later installed
- Appropriate IAM permissions for Kinesis services
- Internet connectivity for downloading packages

## System Information Check

First, verify your system information:

```bash
# Check Ubuntu version
lsb_release -a

# Check system architecture
uname -a

# Check available disk space
df -h
```

## Installation Methods

### Method 1: Direct DEB Package Installation (Recommended)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y wget curl openjdk-8-jdk

# Set JAVA_HOME environment
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc

# Download Kinesis Agent DEB package
cd /tmp
wget https://s3.amazonaws.com/kinesis-agent-install-packages/aws-kinesis-agent-latest.deb

# Install the package
sudo dpkg -i aws-kinesis-agent-latest.deb

# Fix any dependency issues
sudo apt-get install -f -y
```

### Method 2: Manual Installation (If Method 1 fails)

```bash
# Install Java 8
sudo apt install -y openjdk-8-jdk

# Create necessary directories
sudo mkdir -p /usr/share/aws-kinesis-agent
sudo mkdir -p /etc/aws-kinesis
sudo mkdir -p /var/log/aws-kinesis-agent

# Download Kinesis Agent JAR file
cd /usr/share/aws-kinesis-agent
sudo wget https://github.com/awslabs/amazon-kinesis-agent/releases/download/2.0.8/aws-kinesis-agent-2.0.8.jar

# Create basic configuration file
sudo tee /etc/aws-kinesis/agent.json << 'EOF'
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": []
}
EOF

# Create execution script
sudo tee /usr/bin/aws-kinesis-agent << 'EOF'
#!/bin/bash
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export JAVA_HOME
cd /usr/share/aws-kinesis-agent
$JAVA_HOME/bin/java -cp aws-kinesis-agent-2.0.8.jar com.amazon.kinesis.streaming.agent.Agent
EOF

sudo chmod +x /usr/bin/aws-kinesis-agent

# Create systemd service file
sudo tee /etc/systemd/system/aws-kinesis-agent.service << 'EOF'
[Unit]
Description=AWS Kinesis Agent
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/aws-kinesis-agent
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
sudo systemctl daemon-reload
```

## Service Configuration and Startup

```bash
# Enable and start the service
sudo systemctl enable aws-kinesis-agent
sudo systemctl start aws-kinesis-agent

# Check service status
sudo systemctl status aws-kinesis-agent

# View service logs
sudo journalctl -u aws-kinesis-agent -f
```

## Configuration

### Basic Configuration Example

Edit the configuration file:

```bash
sudo nano /etc/aws-kinesis/agent.json
```

Example configuration:

```json
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": [
    {
      "filePattern": "/var/log/game/*.log",
      "kinesisStream": "game-log-stream",
      "partitionKeyOption": "RANDOM"
    }
  ]
}
```

### Configuration Options

- `cloudwatch.emitMetrics`: Enable CloudWatch metrics
- `kinesis.endpoint`: Kinesis endpoint (empty for default)
- `firehose.endpoint`: Firehose endpoint (empty for default)
- `flows`: Array of log file processing rules

### Flow Configuration

- `filePattern`: Log file pattern to monitor
- `kinesisStream`: Target Kinesis stream name
- `partitionKeyOption`: Partition key option (RANDOM, DETERMINISTIC)

## Testing

### Create Test Log Directory

```bash
# Create game log directory
sudo mkdir -p /var/log/game
sudo chown ubuntu:ubuntu /var/log/game
```

### Generate Test Logs

```bash
# Create test log generation script
cat > ~/generate_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/game.log"
while true; do
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"user_id\":\"user_$((RANDOM%1000))\",\"action\":\"login\",\"level\":$((RANDOM%100))}" >> $LOG_FILE
    sleep 1
done
EOF

chmod +x ~/generate_test_logs.sh

# Run test log generation in background
nohup ~/generate_test_logs.sh &

# Monitor the log file
tail -f /var/log/game/game.log
```

## Verification

### Check Installation Status

```bash
# Verify service is running
sudo systemctl is-active aws-kinesis-agent

# Check process
ps aux | grep kinesis

# View recent logs
sudo journalctl -u aws-kinesis-agent --no-pager -n 20
```

### Monitor Performance

```bash
# Check resource usage
top -p $(pgrep -f kinesis)

# Check network connections
sudo ss -tulpn | grep java
```

## Troubleshooting

### Common Issues

1. **Service fails to start**
   ```bash
   sudo journalctl -u aws-kinesis-agent -n 50
   sudo systemctl restart aws-kinesis-agent
   ```

2. **Java not found**
   ```bash
   java -version
   sudo update-alternatives --config java
   ```

3. **Permission issues**
   ```bash
   sudo chown -R root:root /usr/share/aws-kinesis-agent
   sudo chmod 755 /usr/bin/aws-kinesis-agent
   ```

4. **Configuration errors**
   ```bash
   # Validate JSON configuration
   python3 -m json.tool /etc/aws-kinesis/agent.json
   ```

### Log File Locations

- Agent logs: `/var/log/aws-kinesis-agent/aws-kinesis-agent.log`
- System logs: `sudo journalctl -u aws-kinesis-agent`
- Game logs: `/var/log/game/`

## Management Commands

```bash
# Start service
sudo systemctl start aws-kinesis-agent

# Stop service
sudo systemctl stop aws-kinesis-agent

# Restart service
sudo systemctl restart aws-kinesis-agent

# Check status
sudo systemctl status aws-kinesis-agent

# View logs
sudo journalctl -u aws-kinesis-agent -f

# Reload configuration
sudo systemctl reload aws-kinesis-agent
```

## Next Steps

Once Kinesis Agent is installed and configured:

1. Create Amazon Kinesis Data Stream or Data Firehose
2. Configure IAM permissions for the EC2 instance
3. Update the agent configuration with your stream details
4. Monitor data flow in AWS Console

For more detailed information, refer to the [Amazon Kinesis Agent Documentation](https://docs.aws.amazon.com/kinesis/latest/dev/writing-with-agents.html).
