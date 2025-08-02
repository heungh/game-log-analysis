---
title: "Option 2: Vector Installation"
weight: 20
---

# Vector Installation Guide for Ubuntu 20.04

Vector is a high-performance observability data pipeline that can collect, transform, and route logs, metrics, and traces. It's designed for efficient data processing with low resource usage.

## Prerequisites

- Ubuntu 20.04 LTS EC2 instance
- Internet connectivity for downloading packages
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

## Installation Methods

### Method 1: Direct DEB Package Installation (Recommended)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates

# Download Vector DEB package
cd /tmp
wget https://github.com/vectordotdev/vector/releases/download/v0.34.1/vector_0.34.1-1_amd64.deb

# Install the package
sudo dpkg -i vector_0.34.1-1_amd64.deb

# Fix any dependency issues
sudo apt-get install -f -y
```

### Method 2: Binary Installation (Alternative)

```bash
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

## Directory Setup

```bash
# Create necessary directories
sudo mkdir -p /etc/vector
sudo mkdir -p /var/log/vector
sudo mkdir -p /var/lib/vector
sudo mkdir -p /var/log/game

# Set proper ownership
sudo chown -R vector:vector /etc/vector
sudo chown -R vector:vector /var/log/vector
sudo chown -R vector:vector /var/lib/vector
sudo chown ubuntu:ubuntu /var/log/game
```

## Configuration

### Basic Configuration File

Create the main configuration file:

```bash
# Create Vector configuration file
sudo tee /etc/vector/vector.toml << 'EOF'
data_dir = "/var/lib/vector"

[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"

[sinks.stdout]
type = "console"
inputs = ["game_logs"]
encoding.codec = "text"
EOF
```

### Advanced Configuration with Transforms

```bash
# Create advanced configuration file
sudo tee /etc/vector/vector.toml << 'EOF'
data_dir = "/var/lib/vector"

# Source: Monitor game log files
[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"
ignore_older_secs = 86400

# Transform: Parse JSON logs and enrich data
[transforms.parse_logs]
type = "remap"
inputs = ["game_logs"]
source = '''
. = parse_json!(.message) ?? .
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"
'''

# Sink: Console output for testing
[sinks.console]
type = "console"
inputs = ["parse_logs"]
encoding.codec = "json"

# Sink: File output
[sinks.file_output]
type = "file"
inputs = ["parse_logs"]
path = "/var/log/vector/processed_logs.log"
encoding.codec = "json"
EOF
```

### AWS Kinesis Configuration

```bash
# Configuration for AWS Kinesis Streams
sudo tee /etc/vector/vector-kinesis.toml << 'EOF'
data_dir = "/var/lib/vector"

[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"

[transforms.parse_and_enrich]
type = "remap"
inputs = ["game_logs"]
source = '''
. = parse_json!(.message) ?? .
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"
'''

[sinks.kinesis_stream]
type = "aws_kinesis_streams"
inputs = ["parse_and_enrich"]
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

## Service Configuration

### Set File Permissions

```bash
# Set proper permissions
sudo chown vector:vector /etc/vector/vector.toml
sudo chmod 644 /etc/vector/vector.toml
```

### Create systemd Service (if needed)

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
ExecStartPre=/usr/bin/vector validate --no-environment /etc/vector/vector.toml
ExecStart=/usr/bin/vector --config /etc/vector/vector.toml
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
sudo systemctl daemon-reload
```

## Service Management

### Start and Enable Vector

```bash
# Validate configuration
sudo vector validate /etc/vector/vector.toml

# Enable and start service
sudo systemctl enable vector
sudo systemctl start vector

# Check service status
sudo systemctl status vector
```

### Verification

```bash
# Check Vector version
vector --version

# Verify service is active
sudo systemctl is-active vector

# Check process
ps aux | grep vector

# View service logs
sudo journalctl -u vector -n 20
```

## Testing

### Create Test Logs

```bash
# Create test log generation script
cat > ~/generate_vector_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/vector_test.log"
echo "Starting Vector test log generation..."

for i in {1..5}; do
    echo "$(date -Iseconds) - Test log entry $i from Vector" >> $LOG_FILE
    echo "Generated log entry $i"
    sleep 2
done

echo "Test log generation completed!"
EOF

chmod +x ~/generate_vector_test_logs.sh

# Run test log generation
~/generate_vector_test_logs.sh
```

### Generate JSON Test Logs

```bash
# Generate JSON formatted test logs
echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_123","action":"login","level":25}' >> /var/log/game/game.log

# Generate continuous test logs
cat > ~/continuous_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/continuous.log"
counter=1

while true; do
    echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_'$((RANDOM%100))'","action":"test_action","level":'$((RANDOM%50))',"counter":'$counter'}' >> $LOG_FILE
    echo "Generated log entry $counter"
    counter=$((counter + 1))
    sleep 3
done
EOF

chmod +x ~/continuous_test_logs.sh

# Run in background
nohup ~/continuous_test_logs.sh &
```

## Monitoring and Troubleshooting

### Monitor Vector Activity

```bash
# Real-time service logs
sudo journalctl -u vector -f

# Check processed logs (if file sink is configured)
sudo tail -f /var/log/vector/processed_logs.log

# Monitor resource usage
top -p $(pgrep vector)

# Check network connections
sudo ss -tulpn | grep vector
```

### Common Issues

1. **Service fails to start**
   ```bash
   sudo journalctl -u vector -n 50
   sudo systemctl restart vector
   ```

2. **Configuration errors**
   ```bash
   sudo vector validate /etc/vector/vector.toml
   ```

3. **Permission issues**
   ```bash
   sudo chown -R vector:vector /var/lib/vector
   sudo chown -R vector:vector /var/log/vector
   ```

4. **File access issues**
   ```bash
   sudo chmod 644 /var/log/game/*.log
   sudo chown ubuntu:ubuntu /var/log/game
   ```

### Log File Locations

- Vector service logs: `sudo journalctl -u vector`
- Vector output logs: `/var/log/vector/`
- Configuration file: `/etc/vector/vector.toml`
- Data directory: `/var/lib/vector/`
- Game logs: `/var/log/game/`

## Advanced Configuration

### Multiple Sources and Sinks

```toml
data_dir = "/var/lib/vector"

# Source 1: Login logs
[sources.login_logs]
type = "file"
include = ["/var/log/game/login*.log"]

# Source 2: Gameplay logs
[sources.gameplay_logs]
type = "file"
include = ["/var/log/game/gameplay*.log"]

# Transform: Process login logs
[transforms.process_login]
type = "remap"
inputs = ["login_logs"]
source = '''
. = parse_json!(.message) ?? .
.log_type = "login"
.processed_at = now()
'''

# Transform: Process gameplay logs
[transforms.process_gameplay]
type = "remap"
inputs = ["gameplay_logs"]
source = '''
. = parse_json!(.message) ?? .
.log_type = "gameplay"
.processed_at = now()
'''

# Sink: Send to different Kinesis streams
[sinks.login_kinesis]
type = "aws_kinesis_streams"
inputs = ["process_login"]
stream_name = "game-login-stream"
region = "ap-northeast-1"

[sinks.gameplay_kinesis]
type = "aws_kinesis_streams"
inputs = ["process_gameplay"]
stream_name = "game-play-stream"
region = "ap-northeast-1"
```

## Performance Tuning

### Memory Optimization

```toml
# Add to vector.toml
[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
max_line_bytes = 102400
max_read_bytes = 2048
```

### Batch Processing

```toml
[sinks.kinesis_stream]
type = "aws_kinesis_streams"
inputs = ["parse_logs"]
stream_name = "game-log-stream"
region = "ap-northeast-1"
batch.max_events = 1000
batch.timeout_secs = 1
```

## Management Commands

```bash
# Start service
sudo systemctl start vector

# Stop service
sudo systemctl stop vector

# Restart service
sudo systemctl restart vector

# Check status
sudo systemctl status vector

# View logs
sudo journalctl -u vector -f

# Validate configuration
sudo vector validate /etc/vector/vector.toml

# Test configuration
sudo vector test /etc/vector/vector.toml
```

## Next Steps

Once Vector is installed and configured:

1. Create Amazon Kinesis Data Stream or Data Firehose
2. Configure IAM permissions for the EC2 instance
3. Update Vector configuration with your stream details
4. Monitor data flow in AWS Console
5. Set up CloudWatch dashboards for monitoring

For more detailed information, refer to the [Vector Documentation](https://vector.dev/docs/).
