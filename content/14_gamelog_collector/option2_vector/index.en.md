---
title: "Option 2: Vector Installation"
weight: 20
---

# Vector Installation Guide for Ubuntu 20.04

Vector is a high-performance observability data pipeline that can collect, transform, and route logs, metrics, and traces. It provides efficient data processing with low resource usage.

## Prerequisites

- Ubuntu 20.04 LTS EC2 instance
- Internet connection for package downloads
- Appropriate IAM permissions for AWS services
- Basic system administration knowledge

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

## Vector Installation

### Direct Binary Installation Method

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential dependencies
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates

# Download Vector binary
cd /tmp
wget https://github.com/vectordotdev/vector/releases/download/v0.34.1/vector-0.34.1-x86_64-unknown-linux-musl.tar.gz

# Extract and install
tar -xzf vector-0.34.1-x86_64-unknown-linux-musl.tar.gz
sudo cp vector-x86_64-unknown-linux-musl/bin/vector /usr/local/bin/
sudo chmod +x /usr/local/bin/vector

# Create Vector user
sudo useradd --system --shell /bin/false --home-dir /var/lib/vector vector
```

## Directory and Permission Setup

```bash
# Create necessary directories
sudo mkdir -p /etc/vector
sudo mkdir -p /var/log/vector
sudo mkdir -p /var/lib/vector
sudo mkdir -p /var/log/game

# Set appropriate ownership
sudo chown -R vector:vector /etc/vector
sudo chown -R vector:vector /var/log/vector
sudo chown -R vector:vector /var/lib/vector
sudo chown ubuntu:ubuntu /var/log/game

# Set permissions
sudo chmod -R 755 /var/lib/vector
sudo chmod -R 755 /var/log/vector
sudo chmod 755 /var/log/game
```

## Vector Configuration

### Basic Configuration File

```bash
# Create Vector basic configuration file
sudo tee /etc/vector/vector.toml << 'EOF'
data_dir = "/var/lib/vector"

# Source: Monitor game log files
[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"

# Transform: Add basic metadata
[transforms.add_metadata]
type = "remap"
inputs = ["game_logs"]
source = '''
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"
.original_message = .message
'''

# Sink: Console output
[sinks.console]
type = "console"
inputs = ["add_metadata"]
encoding.codec = "json"

# Sink: File output
[sinks.file_output]
type = "file"
inputs = ["add_metadata"]
path = "/var/log/vector/processed_logs.log"
encoding.codec = "json"
EOF
```

### Advanced Configuration with JSON Parsing

```bash
# Advanced configuration with JSON parsing (optional)
sudo tee /etc/vector/vector-advanced.toml << 'EOF'
data_dir = "/var/lib/vector"

[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"
ignore_older_secs = 86400

[transforms.parse_logs]
type = "remap"
inputs = ["game_logs"]
source = '''
# Add basic metadata
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"

# Attempt JSON parsing (safe method)
if is_string(.message) {
  parsed_json, parse_err = parse_json(.message)
  if parse_err == null {
    .parsed_data = parsed_json
    .is_json = true
  } else {
    .is_json = false
    .parse_error = to_string(parse_err)
  }
} else {
  .is_json = false
}
'''

[sinks.console]
type = "console"
inputs = ["parse_logs"]
encoding.codec = "json"

[sinks.file_output]
type = "file"
inputs = ["parse_logs"]
path = "/var/log/vector/processed_logs.log"
encoding.codec = "json"
EOF
```

## systemd Service Setup

### Create Service File

```bash
# Create systemd service file
sudo tee /etc/systemd/system/vector.service << 'EOF'
[Unit]
Description=Vector
Documentation=https://vector.dev
After=network-online.target
Requires=network-online.target

[Service]
User=vector
Group=vector
ExecStartPre=/usr/local/bin/vector validate --no-environment /etc/vector/vector.toml
ExecStart=/usr/local/bin/vector --config /etc/vector/vector.toml
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF
```

### Start and Enable Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Validate configuration
sudo /usr/local/bin/vector validate /etc/vector/vector.toml

# Enable and start service
sudo systemctl enable vector
sudo systemctl start vector

# Check service status
sudo systemctl status vector
```

## Installation Verification and Testing

### Verify Vector Installation

```bash
# Check Vector version
/usr/local/bin/vector --version

# Check service status
sudo systemctl is-active vector

# Check process
ps aux | grep vector
```

### Generate Test Logs

```bash
# Generate basic test log
echo "Test message from game" | sudo tee /var/log/game/test.log

# Generate JSON format test log
echo '{"user_id": "user123", "action": "login", "level": 25}' | sudo tee -a /var/log/game/test.log

# Generate additional test logs
echo "$(date -Iseconds) - Game server started" | sudo tee -a /var/log/game/test.log
```

### Check Vector Output

```bash
# Monitor Vector service logs in real-time
sudo journalctl -u vector -f

# Check processed log file
sudo tail -f /var/log/vector/processed_logs.log

# Check console output (in separate terminal)
sudo journalctl -u vector -n 20
```

## AWS Kinesis Integration Setup

### Kinesis Streams Configuration

```bash
# Configuration file for AWS Kinesis Streams
sudo tee /etc/vector/vector-kinesis.toml << 'EOF'
data_dir = "/var/lib/vector"

[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"

[transforms.add_metadata]
type = "remap"
inputs = ["game_logs"]
source = '''
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"
.original_message = .message
'''

[sinks.kinesis_stream]
type = "aws_kinesis_streams"
inputs = ["add_metadata"]
stream_name = "game-log-stream"
region = "ap-northeast-1"
encoding.codec = "json"

# Batch settings
batch.max_events = 100
batch.timeout_secs = 5

# Retry settings
request.retry_attempts = 3
request.timeout_secs = 30
EOF
```

### Apply Kinesis Configuration

```bash
# Switch to Kinesis configuration (when needed)
sudo cp /etc/vector/vector-kinesis.toml /etc/vector/vector.toml

# Validate configuration
sudo /usr/local/bin/vector validate /etc/vector/vector.toml

# Restart service
sudo systemctl restart vector
```

## Monitoring and Troubleshooting

### Log Monitoring

```bash
# Check Vector service logs
sudo journalctl -u vector -n 50

# Real-time log monitoring
sudo journalctl -u vector -f

# Check processed logs
sudo tail -f /var/log/vector/processed_logs.log
```

### Performance Monitoring

```bash
# Vector process resource usage
top -p $(pgrep vector)

# Check memory usage
ps aux | grep vector | grep -v grep

# Check disk usage
du -sh /var/lib/vector /var/log/vector
```

### Common Troubleshooting

1. **Service Start Failure**
   ```bash
   # Check detailed logs
   sudo journalctl -u vector -n 50
   
   # Validate configuration
   sudo /usr/local/bin/vector validate /etc/vector/vector.toml
   
   # Run directly to identify issues
   sudo /usr/local/bin/vector --config /etc/vector/vector.toml
   ```

2. **Permission Issues**
   ```bash
   # Reset permissions
   sudo chown -R vector:vector /var/lib/vector
   sudo chown -R vector:vector /var/log/vector
   sudo chmod 755 /var/log/game
   ```

3. **Log File Access Issues**
   ```bash
   # Check log file permissions
   ls -la /var/log/game/
   
   # Fix permissions if needed
   sudo chmod 644 /var/log/game/*.log
   ```

## Continuous Test Log Generation

### Automated Log Generation Script

```bash
# Create continuous test log generation script
cat > ~/continuous_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/continuous.log"
counter=1

echo "Starting continuous test log generation..."

while true; do
    # Generate various types of logs
    case $((counter % 4)) in
        0)
            echo "$(date -Iseconds) - User login: user_$((RANDOM%100))" >> $LOG_FILE
            ;;
        1)
            echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_'$((RANDOM%100))'","action":"gameplay","level":'$((RANDOM%50))'}' >> $LOG_FILE
            ;;
        2)
            echo "$(date -Iseconds) - Server event: maintenance_check" >> $LOG_FILE
            ;;
        3)
            echo '{"timestamp":"'$(date -Iseconds)'","event":"purchase","item_id":"item_'$((RANDOM%20))'","price":'$((RANDOM%1000))'}' >> $LOG_FILE
            ;;
    esac
    
    echo "Log entry $counter generated"
    counter=$((counter + 1))
    sleep 3
done
EOF

chmod +x ~/continuous_test_logs.sh
```

### Background Execution

```bash
# Run continuous log generation in background
nohup ~/continuous_test_logs.sh > ~/log_generator.out 2>&1 &

# Check process
ps aux | grep continuous_test_logs

# Stop log generation (when needed)
pkill -f continuous_test_logs.sh
```

## Service Management Commands

```bash
# Start service
sudo systemctl start vector

# Stop service
sudo systemctl stop vector

# Restart service
sudo systemctl restart vector

# Check service status
sudo systemctl status vector

# Enable service (auto-start on boot)
sudo systemctl enable vector

# Disable service
sudo systemctl disable vector

# Reload configuration
sudo systemctl reload vector
```

## Next Steps

After Vector installation and configuration is complete:

1. **Create AWS Kinesis Data Stream**
   - Create Kinesis Data Stream in AWS Console
   - Configure appropriate shard count

2. **Setup IAM Permissions**
   - Grant Kinesis access permissions to EC2 instance
   - Create necessary IAM roles and policies

3. **Update Vector Configuration**
   - Update configuration file with Kinesis stream details
   - Optimize batch and retry settings

4. **Setup Monitoring**
   - Create CloudWatch dashboards
   - Configure alarms and notifications

5. **Performance Tuning**
   - Adjust batch sizes based on log volume
   - Monitor and optimize resource usage

## Reference Materials

- [Vector Official Documentation](https://vector.dev/docs/)
- [Vector GitHub Repository](https://github.com/vectordotdev/vector)
- [Vector Configuration Examples](https://vector.dev/docs/reference/configuration/)
- [AWS Kinesis Integration Guide](https://vector.dev/docs/reference/configuration/sinks/aws_kinesis_streams/)
- [VRL (Vector Remap Language) Documentation](https://vrl.dev/)
- [Vector Performance Tuning Guide](https://vector.dev/docs/administration/tuning/)
