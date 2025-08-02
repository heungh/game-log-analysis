---
title: "Option 1: Kinesis Agent Installation"
weight: 10
---

# Kinesis Agent Installation Guide for Ubuntu 20.04

Amazon Kinesis Agent is a standalone Java application that monitors log files and sends data to Amazon Kinesis Data Streams or Amazon Data Firehose.

## Prerequisites

- Ubuntu 20.04 LTS EC2 instance
- Java 11 or later installed
- Appropriate IAM permissions for Kinesis services
- Internet connectivity for downloading packages
- Git and Maven for building from source

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

## Installation Method: Build from GitHub Source

Since pre-built packages are not reliably available, building from source is the recommended approach.

```bash
# Install required dependencies
sudo apt update
sudo apt install -y git maven openjdk-11-jdk

# Verify Java and Maven installation
java -version
mvn -version

# Create necessary directories
sudo mkdir -p /usr/share/aws-kinesis-agent
sudo mkdir -p /etc/aws-kinesis
sudo mkdir -p /var/log/aws-kinesis-agent

# Clone the source code from GitHub
git clone https://github.com/awslabs/amazon-kinesis-agent.git
cd amazon-kinesis-agent

# Check available versions (optional)
git tag --sort=-version:refname | head -5

# Build the project (skip tests for faster build)
mvn clean package -DskipTests

# Verify build results
ls -la target/

# Copy dependencies to lib directory
mvn dependency:copy-dependencies -DoutputDirectory=/tmp/kinesis-deps
sudo mkdir -p /usr/share/aws-kinesis-agent/lib
sudo cp /tmp/kinesis-deps/*.jar /usr/share/aws-kinesis-agent/lib/

# Copy main JAR file to system location (note: filename is amazon-kinesis-agent)
sudo cp target/amazon-kinesis-agent-*.jar /usr/share/aws-kinesis-agent/

# Verify the exact JAR filename
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

# Create execution script with exact JAR filename (replace 2.0.13 with your version)
# First, get the exact version number
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

# Installation verification
ls -la /usr/share/aws-kinesis-agent/
echo "Number of dependency JARs:"
ls /usr/share/aws-kinesis-agent/lib/ | wc -l
aws-kinesis-agent --help
```

**Important Notes:**
- The JAR filename is `amazon-kinesis-agent-*.jar`, not `aws-kinesis-agent-*.jar`
- Using wildcards (`*`) in the execution script may cause classpath issues
- Always use the exact JAR filename in the execution script
- Ensure all dependency JARs are copied to the lib directory

## Troubleshooting Classpath Issues

If you encounter `ClassNotFoundException` errors:

### 1. Check the execution script

```bash
# Verify the script uses exact JAR filename
cat /usr/bin/aws-kinesis-agent

# The CLASSPATH should use exact filename, not wildcards:
# CORRECT: /usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar
# INCORRECT: /usr/share/aws-kinesis-agent/amazon-kinesis-agent-*.jar
```

### 2. Fix classpath with exact filename

```bash
# Get the exact JAR filename
JAR_FILE=$(ls /usr/share/aws-kinesis-agent/amazon-kinesis-agent-*.jar)
echo "JAR file: $JAR_FILE"

# Extract just the filename
JAR_NAME=$(basename "$JAR_FILE")
echo "JAR name: $JAR_NAME"

# Recreate the script with exact filename
sudo tee /usr/bin/aws-kinesis-agent << EOF
#!/bin/bash
CLASSPATH="/usr/share/aws-kinesis-agent/${JAR_NAME}:/usr/share/aws-kinesis-agent/lib/*"
java -cp "\$CLASSPATH" \\
     -Daws.kinesis.agent.config.file=/etc/aws-kinesis/agent.json \\
     -Dlog4j.configuration=file:///etc/aws-kinesis/log4j.properties \\
     com.amazon.kinesis.streaming.agent.Agent "\$@"
EOF

sudo chmod +x /usr/bin/aws-kinesis-agent
```

### 3. Test directly with Java

```bash
# Test with direct Java command
java -cp "/usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar:/usr/share/aws-kinesis-agent/lib/*" com.amazon.kinesis.streaming.agent.Agent --help
```

### 4. Alternative: Explicit JAR listing

If wildcards don't work in your environment:

```bash
sudo tee /usr/bin/aws-kinesis-agent << 'EOF'
#!/bin/bash
MAIN_JAR="/usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar"
LIB_DIR="/usr/share/aws-kinesis-agent/lib"
CLASSPATH="$MAIN_JAR"

# Add all JAR files from lib directory to classpath
for jar in $LIB_DIR/*.jar; do
    CLASSPATH="$CLASSPATH:$jar"
done

java -cp "$CLASSPATH" \
     -Daws.kinesis.agent.config.file=/etc/aws-kinesis/agent.json \
     -Dlog4j.configuration=file:///etc/aws-kinesis/log4j.properties \
     com.amazon.kinesis.streaming.agent.Agent "$@"
EOF

sudo chmod +x /usr/bin/aws-kinesis-agent
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

# Test help command
aws-kinesis-agent --help
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

5. **Classpath issues (most common)**
   ```bash
   # Check JAR files
   ls -la /usr/share/aws-kinesis-agent/
   ls -la /usr/share/aws-kinesis-agent/lib/ | wc -l
   
   # Verify execution script uses exact JAR filename
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
