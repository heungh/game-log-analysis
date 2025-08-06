---
title: "Option 2: Vector Installation"
weight: 20
---

# Vector Installation Guide on Ubuntu 20.04

Vector is a high-performance observability data pipeline that can collect, transform, and route logs, metrics, and traces. It's a modern tool that provides efficient data processing with low resource usage.

## Prerequisites

- Ubuntu 20.04 LTS EC2 instance
- Internet connection for package downloads
- Appropriate IAM permissions for AWS services

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

## Vector Installation

### Direct Binary Installation Method

Update system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

Install essential dependencies:
```bash
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates
```

Download Vector binary:
```bash
#cd /tmp
wget https://github.com/vectordotdev/vector/releases/download/v0.34.1/vector-0.34.1-x86_64-unknown-linux-musl.tar.gz
```

Extract, install, and create Vector user:
```bash
tar -xzf vector-0.34.1-x86_64-unknown-linux-musl.tar.gz
sudo cp vector-x86_64-unknown-linux-musl/bin/vector /usr/local/bin/
sudo chmod +x /usr/local/bin/vector
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

### Create Basic Configuration File

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

### Advanced Configuration with JSON Parsing (Optional)

```bash
# Advanced configuration with JSON parsing
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

## systemd Service Configuration

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

# Additional test log
echo "$(date -Iseconds) - Game server started" | sudo tee -a /var/log/game/test.log
```

### Check Vector Output

```bash
# Check Vector service logs in real-time
sudo journalctl -u vector -f

# Check processed log file
sudo tail -f /var/log/vector/processed_logs.log

# Check console output (in separate terminal)
sudo journalctl -u vector -n 20
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
   
   # Direct execution to identify issues
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
   
   # Modify permissions if needed
   sudo chmod 644 /var/log/game/*.log
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

Once Vector installation and configuration is complete, proceed with the following tasks:

1. **Create Amazon Data Firehose**
   - Create Amazon Data Firehose in AWS Console

2. **Configure IAM Permissions**
   - Grant Kinesis access permissions to EC2 instance
   - Create necessary IAM roles and policies

3. **Update Vector Configuration**
   - Update configuration file with Amazon Data Firehose information
   - Optimize batch and retry settings

## References

- [Vector Official Documentation](https://vector.dev/docs/)
- [Vector GitHub Repository](https://github.com/vectordotdev/vector)
- [Vector Configuration Examples](https://vector.dev/docs/reference/configuration/)
- [AWS Kinesis Integration Guide](https://vector.dev/docs/reference/configuration/sinks/aws_kinesis_streams/)
- [VRL (Vector Remap Language) Documentation](https://vrl.dev/)
- [Vector Performance Tuning Guide](https://vector.dev/docs/administration/tuning/)
