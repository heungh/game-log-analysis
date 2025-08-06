---
title: "Option 1: Kinesis Agent Installation"
weight: 10
---

# Kinesis Agent Installation Guide on Ubuntu 20.04

Amazon Kinesis Agent is a standalone Java application that monitors log files and sends data to Amazon Kinesis Data Streams or Amazon Data Firehose.

## Prerequisites

- Ubuntu 20.04 LTS EC2 instance
- Java 11 or higher installed
- Appropriate IAM permissions for AWS services
- Internet connection for package downloads
- Git and Maven for source build

## System Information Check

First, check the system information:

```bash
# Check Ubuntu version
lsb_release -a

# Check system architecture
uname -a

# Check available disk space
df -h
```

## Installation Method: Build from GitHub Source

Since Kinesis Agent currently doesn't provide binary files, you can build and use the latest version from the GitHub source.

```bash
# Install necessary tools (Java, Maven installation)
sudo apt update
sudo apt install -y git maven openjdk-11-jdk

# Check Java and Maven versions
java -version
mvn -version
```

If Java and Maven versions are confirmed to be installed properly, build the Kinesis Agent as follows:

```bash
# Create necessary directories
sudo mkdir -p /usr/share/aws-kinesis-agent
sudo mkdir -p /etc/aws-kinesis
sudo mkdir -p /var/log/aws-kinesis-agent

# Clone source code from GitHub
git clone https://github.com/awslabs/amazon-kinesis-agent.git
cd amazon-kinesis-agent

# Check latest tag (optional)
git tag --sort=-version:refname | head -5

# Build (skip tests for faster build)
mvn clean package -DskipTests

# Check build results
ls -la target/
```

Build the Kinesis Agent and proceed with environment configuration tasks such as moving the created JAR file:

```bash
# Copy dependencies to lib directory
mvn dependency:copy-dependencies -DoutputDirectory=/tmp/kinesis-deps
sudo mkdir -p /usr/share/aws-kinesis-agent/lib
sudo cp /tmp/kinesis-deps/*.jar /usr/share/aws-kinesis-agent/lib/

# Copy main JAR file to system location (note that the filename is amazon-kinesis-agent)
sudo cp target/amazon-kinesis-agent-*.jar /usr/share/aws-kinesis-agent/

# Check exact JAR filename
ls -la /usr/share/aws-kinesis-agent/amazon-kinesis-agent-*.jar

# Create basic configuration file
sudo tee /etc/aws-kinesis/agent.json << 'EOF'
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": []
}
EOF
```

The Kinesis Agent configuration file section is left blank as above and will be configured again in the following exercises.
Next is the task of creating execution scripts and running services based on the configured environment.

```bash
# Create execution script with exact JAR filename (replace 2.0.13 with actual version)
# First check exact version number
VERSION=$(ls /usr/share/aws-kinesis-agent/amazon-kinesis-agent-*.jar | sed 's/.*amazon-kinesis-agent-\(.*\)\.jar/\1/')
echo "Detected version: $VERSION"

# Create execution script with exact filename
sudo tee /usr/bin/aws-kinesis-agent << EOF
#!/bin/bash
CLASSPATH="/usr/share/aws-kinesis-agent/amazon-kinesis-agent-${VERSION}.jar:/usr/share/aws-kinesis-agent/lib/*"
java -cp "\$CLASSPATH" \\
     -Daws.kinesis.agent.config.file=/etc/aws-kinesis/agent.json \\
     -Dlog4j.configuration=file:///etc/aws-kinesis/log4j.properties \\
     com.amazon.kinesis.streaming.agent.Agent "\$@"
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

# Verify installation
ls -la /usr/share/aws-kinesis-agent/
echo "Number of dependency JAR files:"
ls /usr/share/aws-kinesis-agent/lib/ | wc -l
aws-kinesis-agent --help
```

## Service Configuration and Start

```bash
# Enable and start service
sudo systemctl enable aws-kinesis-agent
sudo systemctl start aws-kinesis-agent

# Check service status
sudo systemctl status aws-kinesis-agent

# Check service logs
sudo journalctl -u aws-kinesis-agent -f
```

## Configuration

### Basic Configuration Example

Edit the configuration file:

```bash
sudo vi /etc/aws-kinesis/agent.json
```

Configuration example:

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
- `kinesis.endpoint`: Kinesis endpoint (default is empty string)
- `firehose.endpoint`: Firehose endpoint (default is empty string)
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
LOG_FILE="/var/log/game/test.log"
while true; do
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"user_id\":\"user_$((RANDOM%1000))\",\"action\":\"login\",\"level\":$((RANDOM%100))}" >> $LOG_FILE
    sleep 1
done
EOF

chmod +x ~/generate_test_logs.sh

# Run test log generation in background
nohup ~/generate_test_logs.sh &

# Monitor log file
tail -f /var/log/game/test.log
```

## Installation Verification

### Check Installation Status

```bash
# Check if service is running
sudo systemctl is-active aws-kinesis-agent

# Check process
ps aux | grep kinesis

# Check recent logs
sudo journalctl -u aws-kinesis-agent --no-pager -n 20

# Test help command
aws-kinesis-agent --help
```

### Performance Monitoring

```bash
# Check resource usage
top -p $(pgrep -f kinesis)

# Check network connections
sudo ss -tulpn | grep java
```

## Troubleshooting

### Common Issues

1. **Service Start Failure**
   ```bash
   sudo journalctl -u aws-kinesis-agent -n 50
   sudo systemctl restart aws-kinesis-agent
   ```

2. **Java Not Found**
   ```bash
   java -version
   sudo update-alternatives --config java
   ```

3. **Permission Issues**
   ```bash
   sudo chown -R root:root /usr/share/aws-kinesis-agent
   sudo chmod 755 /usr/bin/aws-kinesis-agent
   ```

4. **Configuration Errors**
   ```bash
   # Validate JSON configuration
   python3 -m json.tool /etc/aws-kinesis/agent.json
   ```

5. **Classpath Issues (Most Common)**
   ```bash
   # Check JAR files
   ls -la /usr/share/aws-kinesis-agent/
   ls -la /usr/share/aws-kinesis-agent/lib/ | wc -l
   
   # Check if execution script uses correct JAR filename
   cat /usr/bin/aws-kinesis-agent
   
   # Test direct Java execution
   java -cp "/usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar:/usr/share/aws-kinesis-agent/lib/*" com.amazon.kinesis.streaming.agent.Agent --help
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

# Check logs
sudo journalctl -u aws-kinesis-agent -f

# Reload configuration
sudo systemctl reload aws-kinesis-agent
```

## Advanced Configuration

### Multi-Stream Configuration

```json
{
  "cloudwatch.emitMetrics": true,
  "flows": [
    {
      "filePattern": "/var/log/game/login*.log",
      "kinesisStream": "game-login-stream",
      "partitionKeyOption": "RANDOM"
    },
    {
      "filePattern": "/var/log/game/gameplay*.log",
      "kinesisStream": "game-play-stream",
      "partitionKeyOption": "DETERMINISTIC",
      "partitionKey": "{user_id}"
    }
  ]
}
```

### Data Transformation Configuration

```json
{
  "flows": [
    {
      "filePattern": "/var/log/game/*.log",
      "kinesisStream": "game-log-stream",
      "dataProcessingOptions": [
        {
          "optionName": "LOGTOJSON",
          "logFormat": "COMMONAPACHELOG"
        }
      ]
    }
  ]
}
```

## Performance Tuning

### JVM Options Configuration

You can modify the execution script to add JVM options:

```bash
sudo vi /usr/bin/aws-kinesis-agent
```

```bash
#!/bin/bash
CLASSPATH="/usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar:/usr/share/aws-kinesis-agent/lib/*"
java -Xmx512m -Xms256m -cp "$CLASSPATH" \
     -Daws.kinesis.agent.config.file=/etc/aws-kinesis/agent.json \
     -Dlog4j.configuration=file:///etc/aws-kinesis/log4j.properties \
     com.amazon.kinesis.streaming.agent.Agent "$@"
```

### Monitoring Configuration

You can enable CloudWatch metrics to monitor performance:

```json
{
  "cloudwatch.emitMetrics": true,
  "cloudwatch.endpoint": "",
  "flows": [
    {
      "filePattern": "/var/log/game/*.log",
      "kinesisStream": "game-log-stream",
      "partitionKeyOption": "RANDOM"
    }
  ]
}
```

## Next Steps

Once Kinesis Agent installation and configuration is complete, proceed with the following tasks:

1. **Create Amazon Data Firehose**
   - Create Amazon Data Firehose in AWS Console

2. **Configure IAM Permissions**
   - Grant Kinesis access permissions to EC2 instance
   - Create necessary IAM roles and policies

3. **Update Kinesis Agent Configuration**
   - Update configuration file with Amazon Data Firehose information
   - Optimize batch and retry settings

For detailed information, refer to the [Amazon Kinesis Agent Official Documentation](https://docs.aws.amazon.com/kinesis/latest/dev/writing-with-agents.html).

## References

- [Amazon Kinesis Agent GitHub](https://github.com/awslabs/amazon-kinesis-agent)
- [Kinesis Data Streams Developer Guide](https://docs.aws.amazon.com/kinesis/latest/dev/)
- [Amazon Data Firehose Developer Guide](https://docs.aws.amazon.com/firehose/latest/dev/)
