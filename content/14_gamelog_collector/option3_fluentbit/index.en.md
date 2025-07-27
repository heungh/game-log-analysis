+++
title = "Option 3: Fluent Bit Installation"
weight = 30
+++

# Fluent Bit Installation Guide

Fluent Bit is a lightweight, high-performance log processor and forwarder that can collect data from various sources and send it to multiple destinations. It's a CNCF project.

## Prerequisites

- Amazon Linux 2023 instance
- curl, wget, tar, gzip packages
- Appropriate IAM permissions (CloudWatch, S3, Kinesis access)

## Automated Installation

You can automatically install Fluent Bit using the following script:

```bash
curl -O https://raw.githubusercontent.com/your-repo/game-log-analytics/main/static/scripts/install-fluent-bit.sh
chmod +x install-fluent-bit.sh
sudo ./install-fluent-bit.sh
```

## Manual Installation Steps

### Step 1: Install Required Packages

```bash
# Update system and install required packages
sudo yum update -y
sudo yum install -y curl wget tar gzip
```

### Step 2: Add Fluent Bit Repository

```bash
# Add Fluent Bit official repository
sudo tee /etc/yum.repos.d/fluent-bit.repo << 'EOF'
[fluent-bit]
name = Fluent Bit
baseurl = https://packages.fluentbit.io/amazonlinux/2023/$basearch/
gpgcheck=1
gpgkey=https://packages.fluentbit.io/fluentbit.key
enabled=1
EOF
```

### Step 3: Install Fluent Bit

```bash
# Install Fluent Bit
sudo yum install -y fluent-bit
```

### Step 4: Create Directories and Set Permissions

```bash
# Create required directories
sudo mkdir -p /etc/fluent-bit
sudo mkdir -p /var/log/fluent-bit
sudo mkdir -p /var/log/game-logs
sudo mkdir -p /var/lib/fluent-bit

# Set permissions
sudo chown -R fluent-bit:fluent-bit /var/log/fluent-bit
sudo chown -R fluent-bit:fluent-bit /var/lib/fluent-bit
sudo chown -R ec2-user:ec2-user /var/log/game-logs
```

### Step 5: Create Fluent Bit Configuration Files

#### Create Main Configuration File

```bash
sudo tee /etc/fluent-bit/fluent-bit.conf << 'EOF'
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off
    Parsers_File  parsers.conf
    HTTP_Server   On
    HTTP_Listen   0.0.0.0
    HTTP_Port     2020
    storage.path  /var/lib/fluent-bit/

[INPUT]
    Name              tail
    Path              /var/log/game-logs/*.log
    Tag               game.logs
    Parser            json
    DB                /var/lib/fluent-bit/game-logs.db
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On
    Refresh_Interval  10

[INPUT]
    Name              systemd
    Tag               system.logs
    Systemd_Filter    _SYSTEMD_UNIT=sshd.service
    Systemd_Filter    _SYSTEMD_UNIT=amazon-ssm-agent.service

[FILTER]
    Name                aws
    Match               *
    imds_version        v2
    az                  true
    ec2_instance_id     true
    ec2_instance_type   true
    private_ip          true
    vpc_id              true
    ami_id              true
    account_id          true
    hostname            true
    region              us-east-1

[FILTER]
    Name          modify
    Match         game.logs
    Add           source game-server
    Add           environment production

[OUTPUT]
    Name                cloudwatch_logs
    Match               game.logs
    region              us-east-1
    log_group_name      /aws/ec2/fluent-bit/game-logs
    log_stream_prefix   game-server-
    auto_create_group   true

[OUTPUT]
    Name                kinesis_streams
    Match               game.logs
    region              us-east-1
    stream              game-log-stream
    partition_key       player_id
    append_newline      false

[OUTPUT]
    Name                s3
    Match               game.logs
    bucket              datapipelinebucket${AWS_ACCOUNT_ID}us-east-1
    region              us-east-1
    total_file_size     50M
    s3_key_format       /game-logs/year=%Y/month=%m/day=%d/hour=%H/fluent-bit-logs-%Y%m%d-%H%M%S
    s3_key_format_tag_delimiters .-
    store_dir           /var/lib/fluent-bit/s3
    upload_timeout      10m

[OUTPUT]
    Name                forward
    Match               system.logs
    Host                127.0.0.1
    Port                24224
    tls                 off
    tls.verify          off
EOF
```

#### Create Parser Configuration File

```bash
sudo tee /etc/fluent-bit/parsers.conf << 'EOF'
[PARSER]
    Name        json
    Format      json
    Time_Key    timestamp
    Time_Format %Y-%m-%dT%H:%M:%S.%L
    Time_Keep   On

[PARSER]
    Name        game_log
    Format      regex
    Regex       ^(?<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z) \[(?<level>\w+)\] (?<message>.*)$
    Time_Key    timestamp
    Time_Format %Y-%m-%dT%H:%M:%S.%L
    Time_Keep   On

[PARSER]
    Name        apache
    Format      regex
    Regex       ^(?<host>[^ ]*) [^ ]* (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*?)(?: +\S*)?)?" (?<code>[^ ]*) (?<size>[^ ]*)(?: "(?<referer>[^\"]*)" "(?<agent>[^\"]*)")?$
    Time_Key    time
    Time_Format %d/%b/%Y:%H:%M:%S %z

[PARSER]
    Name        nginx
    Format      regex
    Regex       ^(?<remote>[^ ]*) (?<host>[^ ]*) (?<user>[^ ]*) \[(?<time>[^\]]*)\] "(?<method>\S+)(?: +(?<path>[^\"]*)(?:\?(?<query>[^ ]*))?(?: +\S*)?)?" (?<code>[^ ]*) (?<size>[^ ]*)(?: "(?<referer>[^\"]*)" "(?<agent>[^\"]*)")?$
    Time_Key    time
    Time_Format %d/%b/%Y:%H:%M:%S %z
EOF
```

### Step 6: Configure systemd Service

```bash
# Create systemd service file (if needed)
sudo tee /etc/systemd/system/fluent-bit.service << 'EOF'
[Unit]
Description=Fluent Bit
Documentation=https://fluentbit.io/documentation/
Requires=network.target
After=network.target

[Service]
Type=simple
ExecStart=/opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=2
User=fluent-bit
Group=fluent-bit

[Install]
WantedBy=multi-user.target
EOF
```

### Step 7: Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable fluent-bit
sudo systemctl start fluent-bit

# Check status
sudo systemctl status fluent-bit
```

## Configuration File Details

### SERVICE Section

- `Flush`: Output flush interval (seconds)
- `Log_Level`: Log level (error, warn, info, debug, trace)
- `HTTP_Server`: Enable HTTP server
- `HTTP_Port`: HTTP API port

### INPUT Section

- `tail`: File monitoring
- `systemd`: systemd journal log collection

### FILTER Section

- `aws`: Add AWS metadata
- `modify`: Add/modify fields

### OUTPUT Section

- `cloudwatch_logs`: Send to CloudWatch Logs
- `kinesis_streams`: Send to Kinesis Data Streams
- `s3`: Archive to S3 bucket

## Management Commands

After installation, you can use the following management script:

```bash
# Management script usage
./manage-fluent-bit.sh {start|stop|restart|status|logs|config|validate|test|api|metrics|uptime|health}
```

### Key Commands

```bash
# Check service status
./manage-fluent-bit.sh status

# View logs in real-time
./manage-fluent-bit.sh logs

# Validate configuration file
./manage-fluent-bit.sh validate

# Generate test log
./manage-fluent-bit.sh test

# Check HTTP API status
./manage-fluent-bit.sh api

# Health check
./manage-fluent-bit.sh health
```

## HTTP API

Fluent Bit provides an HTTP API (port 2020):

```bash
# Health check
curl http://localhost:2020/api/v1/health

# View metrics
curl http://localhost:2020/api/v1/metrics

# Check uptime
curl http://localhost:2020/api/v1/uptime

# Configuration info
curl http://localhost:2020/
```

## Testing

After installation is complete, you can generate test logs to verify proper operation:

```bash
# Generate test log
echo '{"timestamp":"'$(date -Iseconds)'","level":"INFO","message":"Test game event from Fluent Bit","player_id":"test456","event_type":"logout","score":1500}' >> /var/log/game-logs/game.log

# Check Fluent Bit logs
sudo journalctl -u fluent-bit -f
```

## Troubleshooting

### Common Issues

1. **Service Start Failure**
   ```bash
   sudo journalctl -u fluent-bit -n 50
   ```

2. **Configuration File Errors**
   ```bash
   sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run
   ```

3. **Permission Issues**
   ```bash
   sudo chown -R fluent-bit:fluent-bit /var/log/fluent-bit
   sudo chown -R fluent-bit:fluent-bit /var/lib/fluent-bit
   ```

4. **Memory Usage Issues**
   ```bash
   # Adjust Mem_Buf_Limit in fluent-bit.conf
   Mem_Buf_Limit     10MB
   ```

### Log File Locations

- Fluent Bit logs: `sudo journalctl -u fluent-bit`
- Installation logs: `/var/log/fluent-bit-install.log`
- Game logs: `/var/log/game-logs/`
- Fluent Bit data: `/var/lib/fluent-bit/`

## Performance Optimization

### Memory Usage Optimization

```ini
[INPUT]
    Name              tail
    Path              /var/log/game-logs/*.log
    Mem_Buf_Limit     10MB
    Skip_Long_Lines   On
    Buffer_Chunk_Size 32k
    Buffer_Max_Size   256k
```

### Batch Processing Optimization

```ini
[OUTPUT]
    Name                cloudwatch_logs
    Match               game.logs
    workers             2
```

## Monitoring

### Metrics Collection

```bash
# Check in Prometheus metrics format
curl http://localhost:2020/api/v1/metrics/prometheus
```

### Log Statistics

```bash
# Check input/output statistics
curl http://localhost:2020/api/v1/metrics | jq '.input'
curl http://localhost:2020/api/v1/metrics | jq '.output'
```

## Next Steps

After Fluent Bit installation is complete:

1. Fine-tune log parsing rules
2. Set up metrics and alarms
3. Configure dashboards
4. Set up performance monitoring
5. Configure log retention policies

For more details, refer to the [Fluent Bit Official Documentation](https://docs.fluentbit.io/).
