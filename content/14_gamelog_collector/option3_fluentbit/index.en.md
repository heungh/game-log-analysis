---
title: "Option 3: Fluent Bit Installation"
weight: 30
---

# Fluent Bit Installation Guide for Ubuntu 20.04

Fluent Bit is a lightweight, high-performance log processor and forwarder that is part of the CNCF project. It can collect data from various sources and send it to multiple destinations with low memory usage and high throughput.

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

# Check memory
free -h
```

## Installation Process

### Step 1: System Update and Essential Package Installation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential dependencies
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates lsb-release
```

### Step 2: Add Fluent Bit Official Repository

```bash
# Add Fluent Bit GPG key
wget -qO - https://packages.fluentbit.io/fluentbit.key | sudo apt-key add -

# Add repository for Ubuntu 20.04 (focal)
echo "deb https://packages.fluentbit.io/ubuntu/focal focal main" | sudo tee /etc/apt/sources.list.d/fluent-bit.list

# Update package list
sudo apt update
```

### Step 3: Install Fluent Bit

```bash
# Install Fluent Bit
sudo apt install -y fluent-bit

# Check installation path
ls -la /opt/fluent-bit/bin/fluent-bit

# Check version
/opt/fluent-bit/bin/fluent-bit --version
```

### Step 4: Setup Execution Path

```bash
# Create symbolic link for convenience
sudo ln -sf /opt/fluent-bit/bin/fluent-bit /usr/local/bin/fluent-bit

# Refresh PATH
hash -r
```

### Step 5: Directory and Permission Setup

```bash
# Create necessary directories
sudo mkdir -p /var/log/game
sudo mkdir -p /var/log/fluent-bit

# Set permissions
sudo chown ubuntu:ubuntu /var/log/game
sudo chmod 755 /var/log/game
sudo chmod 755 /var/log/fluent-bit

# Verify directories
ls -la /var/log/ | grep -E "(game|fluent)"
```

## Configuration

### Create Basic Configuration File

Create a configuration file with memory optimization:

```bash
# Backup existing configuration file (if exists)
sudo cp /etc/fluent-bit/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf.backup 2>/dev/null || echo "No existing configuration file"

# Create new configuration file
sudo tee /etc/fluent-bit/fluent-bit.conf << 'EOF'
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off
    Parsers_File  parsers.conf
    HTTP_Server   On
    HTTP_Listen   0.0.0.0
    HTTP_Port     2020
    storage.path  /var/log/fluent-bit/
    storage.sync  normal
    storage.checksum off
    storage.backlog.mem_limit 5M

[INPUT]
    Name              tail
    Path              /var/log/game/*.log
    Tag               game.logs
    Refresh_Interval  5
    Read_from_Head    true
    Buffer_Chunk_Size 32k
    Buffer_Max_Size   256k
    Mem_Buf_Limit     1M

[OUTPUT]
    Name  stdout
    Match *
EOF
```

### Configuration Options Explanation

**SERVICE Section:**
- `Flush`: Output flush interval (seconds)
- `Log_Level`: Log level (error, warn, info, debug, trace)
- `HTTP_Server`: Enable HTTP API server
- `HTTP_Port`: HTTP API port
- `storage.backlog.mem_limit`: Memory backlog limit

**INPUT Section:**
- `Name`: Input plugin name (tail)
- `Path`: Log file path to monitor
- `Tag`: Tag to assign to logs
- `Read_from_Head`: Read from beginning of file
- `Mem_Buf_Limit`: Memory buffer limit

**OUTPUT Section:**
- `Name`: Output plugin name (stdout)
- `Match`: Tag pattern to match

## Service Management

### Start and Enable Service

```bash
# Validate configuration file
sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run

# Start service
sudo systemctl start fluent-bit

# Check service status
sudo systemctl status fluent-bit

# Enable service (auto-start on boot)
sudo systemctl enable fluent-bit
```

### Installation Verification

```bash
# Check if service is active
sudo systemctl is-active fluent-bit

# Check process
ps aux | grep fluent-bit

# Check HTTP API
curl http://localhost:2020/

# Check metrics
curl http://localhost:2020/api/v1/metrics
```

## Testing

### Generate Test Logs

```bash
# Generate simple test logs
echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_001","action":"login","level":1}' >> /var/log/game/test.log
echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_002","action":"logout","level":5}' >> /var/log/game/test.log

# Check generated logs
cat /var/log/game/test.log
```

### Continuous Test Log Generation

```bash
# Create test log generation script
cat > ~/generate_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/game.log"
counter=1

echo "Starting Fluent Bit test log generation..."

while true; do
    timestamp=$(date -Iseconds)
    user_id="user_$((RANDOM%100))"
    actions=("login" "logout" "level_up" "purchase" "battle")
    action=${actions[$RANDOM % ${#actions[@]}]}
    level=$((RANDOM%100))
    
    echo "{\"timestamp\":\"$timestamp\",\"user_id\":\"$user_id\",\"action\":\"$action\",\"level\":$level,\"counter\":$counter}" >> $LOG_FILE
    echo "Log entry $counter created: $action by $user_id"
    
    counter=$((counter + 1))
    sleep 2
done
EOF

chmod +x ~/generate_test_logs.sh

# Run in background
nohup ~/generate_test_logs.sh > ~/test_log_generator.out 2>&1 &
```

## Monitoring

### Real-time Log Monitoring

```bash
# Monitor game logs in real-time
tail -f /var/log/game/game.log

# Monitor Fluent Bit service logs
sudo journalctl -u fluent-bit -f

# Check recent logs
sudo journalctl -u fluent-bit -n 20
```

### Performance Monitoring

```bash
# Check resource usage
top -p $(pgrep fluent-bit)

# Check memory usage
ps aux | grep fluent-bit | grep -v grep

# Check network connections
sudo ss -tulpn | grep 2020
```

### HTTP API Monitoring

```bash
# Check basic information
curl http://localhost:2020/

# Check metrics
curl http://localhost:2020/api/v1/metrics

# Check configuration
curl http://localhost:2020/api/v1/config

# Health check
curl http://localhost:2020/api/v1/health
```

## Advanced Configuration

### AWS Kinesis Streams Integration

```bash
# Create configuration file for Kinesis Streams
sudo tee /etc/fluent-bit/kinesis.conf << 'EOF'
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off
    HTTP_Server   On
    HTTP_Listen   0.0.0.0
    HTTP_Port     2020

[INPUT]
    Name              tail
    Path              /var/log/game/*.log
    Tag               game.logs
    Read_from_Head    true

[FILTER]
    Name parser
    Match game.logs
    Key_Name message
    Parser json

[OUTPUT]
    Name kinesis_streams
    Match *
    region ap-northeast-2
    stream game-log-stream
    partition_key user_id
EOF
```

### CloudWatch Logs Integration

```bash
# Create configuration file for CloudWatch Logs
sudo tee /etc/fluent-bit/cloudwatch.conf << 'EOF'
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off

[INPUT]
    Name              tail
    Path              /var/log/game/*.log
    Tag               game.logs
    Read_from_Head    true

[OUTPUT]
    Name cloudwatch_logs
    Match *
    region ap-northeast-2
    log_group_name /aws/ec2/game-logs
    log_stream_name ${hostname}
    auto_create_group true
EOF
```

## Troubleshooting

### Common Issues

1. **Service Start Failure**
   ```bash
   sudo journalctl -u fluent-bit -n 50
   sudo systemctl restart fluent-bit
   ```

2. **Configuration File Error**
   ```bash
   sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run
   ```

3. **Permission Issues**
   ```bash
   sudo chown -R fluent-bit:fluent-bit /var/log/fluent-bit
   sudo chmod 644 /var/log/game/*.log
   ```

4. **Memory Issues**
   ```bash
   # Adjust memory limits in configuration file
   Mem_Buf_Limit     512k
   storage.backlog.mem_limit 2M
   ```

### Log File Locations

- Fluent Bit service logs: `sudo journalctl -u fluent-bit`
- Configuration file: `/etc/fluent-bit/fluent-bit.conf`
- Game logs: `/var/log/game/`
- Fluent Bit data: `/var/log/fluent-bit/`

## Management Commands

```bash
# Start service
sudo systemctl start fluent-bit

# Stop service
sudo systemctl stop fluent-bit

# Restart service
sudo systemctl restart fluent-bit

# Check status
sudo systemctl status fluent-bit

# View logs
sudo journalctl -u fluent-bit -f

# Validate configuration
sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run

# Stop test log generator
pkill -f generate_test_logs.sh
```

## Performance Optimization

### Memory-Limited Environment Optimization

```toml
[SERVICE]
    storage.backlog.mem_limit 2M
    
[INPUT]
    Mem_Buf_Limit     512k
    Buffer_Chunk_Size 16k
    Buffer_Max_Size   128k
```

### Batch Processing Optimization

```toml
[OUTPUT]
    Name kinesis_streams
    Match *
    region ap-northeast-2
    stream game-log-stream
    batch_size 100
    batch_timeout 5s
```

## Next Steps

After completing Fluent Bit installation and configuration:

1. Create Amazon Kinesis Data Stream or Data Firehose
2. Set up IAM permissions for EC2 instance
3. Update Fluent Bit configuration with stream details
4. Monitor data flow in AWS Console
5. Set up CloudWatch dashboards

For more information, refer to the [Fluent Bit official documentation](https://docs.fluentbit.io/).

## References

- [Fluent Bit GitHub Repository](https://github.com/fluent/fluent-bit)
- [Fluent Bit Configuration Guide](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit)
- [AWS Output Plugins](https://docs.fluentbit.io/manual/pipeline/outputs/kinesis)
- [Performance Tuning Guide](https://docs.fluentbit.io/manual/administration/memory-management)
