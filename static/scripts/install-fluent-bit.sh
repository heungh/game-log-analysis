#!/bin/bash

# Fluent Bit 설치 스크립트
# Amazon Linux 2023용

set -e

echo "=================================================="
echo " Fluent Bit 설치 시작"
echo "=================================================="

# 로그 파일 설정
LOG_FILE="/var/log/fluent-bit-install.log"
exec > >(tee -a $LOG_FILE) 2>&1

echo " 1단계: 필수 패키지 설치"
# 필수 패키지 설치
yum update -y
yum install -y curl wget tar gzip

echo " 2단계: Fluent Bit 리포지토리 추가"
# Fluent Bit 공식 리포지토리 추가
cat > /etc/yum.repos.d/fluent-bit.repo << 'EOF'
[fluent-bit]
name = Fluent Bit
baseurl = https://packages.fluentbit.io/amazonlinux/2023/$basearch/
gpgcheck=1
gpgkey=https://packages.fluentbit.io/fluentbit.key
enabled=1
EOF

echo " 3단계: Fluent Bit 설치"
# Fluent Bit 설치
yum install -y fluent-bit

echo " 4단계: 디렉토리 생성 및 권한 설정"
# 필요한 디렉토리 생성
mkdir -p /etc/fluent-bit
mkdir -p /var/log/fluent-bit
mkdir -p /var/log/game-logs
mkdir -p /var/lib/fluent-bit

# 권한 설정
chown -R fluent-bit:fluent-bit /var/log/fluent-bit
chown -R fluent-bit:fluent-bit /var/lib/fluent-bit
chown -R ec2-user:ec2-user /var/log/game-logs

echo " 5단계: Fluent Bit 설정 파일 생성"
# 메인 설정 파일 생성
cat > /etc/fluent-bit/fluent-bit.conf << 'EOF'
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

# 파서 설정 파일 생성
cat > /etc/fluent-bit/parsers.conf << 'EOF'
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

echo " 6단계: systemd 서비스 설정"
# systemd 서비스 파일 수정 (필요시)
if [ ! -f /etc/systemd/system/fluent-bit.service ]; then
    cat > /etc/systemd/system/fluent-bit.service << 'EOF'
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
fi

echo " 7단계: Fluent Bit 서비스 시작"
# systemd 데몬 리로드 및 서비스 시작
systemctl daemon-reload
systemctl enable fluent-bit
systemctl start fluent-bit

echo " 8단계: 관리 스크립트 생성"
# Fluent Bit 관리 스크립트 생성
cat > /home/ec2-user/manage-fluent-bit.sh << 'EOF'
#!/bin/bash

echo "=================================================="
echo "🔧 Fluent Bit 관리 스크립트"
echo "=================================================="

case "$1" in
    start)
        echo "Fluent Bit 시작 중..."
        sudo systemctl start fluent-bit
        echo " Fluent Bit이 시작되었습니다."
        ;;
    stop)
        echo "Fluent Bit 중지 중..."
        sudo systemctl stop fluent-bit
        echo " Fluent Bit이 중지되었습니다."
        ;;
    restart)
        echo "Fluent Bit 재시작 중..."
        sudo systemctl restart fluent-bit
        echo " Fluent Bit이 재시작되었습니다."
        ;;
    status)
        echo "Fluent Bit 상태 확인 중..."
        sudo systemctl status fluent-bit
        ;;
    logs)
        echo "Fluent Bit 로그 확인 중..."
        sudo journalctl -u fluent-bit -f
        ;;
    config)
        echo "Fluent Bit 설정 파일 편집..."
        sudo nano /etc/fluent-bit/fluent-bit.conf
        ;;
    validate)
        echo "Fluent Bit 설정 파일 검증 중..."
        sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run
        ;;
    test)
        echo "테스트 로그 생성 중..."
        echo '{"timestamp":"'$(date -Iseconds)'","level":"INFO","message":"Test game event from Fluent Bit","player_id":"test456","event_type":"logout","score":1500}' >> /var/log/game-logs/game.log
        echo " 테스트 로그가 생성되었습니다."
        ;;
    api)
        echo "Fluent Bit HTTP API 상태 확인 중..."
        curl -s http://localhost:2020/ | jq . || echo "API 응답 없음 또는 jq 미설치"
        ;;
    metrics)
        echo "Fluent Bit 메트릭 확인 중..."
        curl -s http://localhost:2020/api/v1/metrics
        ;;
    uptime)
        echo "Fluent Bit 업타임 확인 중..."
        curl -s http://localhost:2020/api/v1/uptime
        ;;
    health)
        echo "Fluent Bit 헬스 체크 중..."
        curl -s http://localhost:2020/api/v1/health
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs|config|validate|test|api|metrics|uptime|health}"
        echo ""
        echo "명령어 설명:"
        echo "  start    - Fluent Bit 시작"
        echo "  stop     - Fluent Bit 중지"
        echo "  restart  - Fluent Bit 재시작"
        echo "  status   - Fluent Bit 상태 확인"
        echo "  logs     - Fluent Bit 로그 실시간 확인"
        echo "  config   - 설정 파일 편집"
        echo "  validate - 설정 파일 검증"
        echo "  test     - 테스트 로그 생성"
        echo "  api      - HTTP API 상태 확인"
        echo "  metrics  - 메트릭 확인"
        echo "  uptime   - 업타임 확인"
        echo "  health   - 헬스 체크"
        exit 1
        ;;
esac
EOF

chmod +x /home/ec2-user/manage-fluent-bit.sh
chown ec2-user:ec2-user /home/ec2-user/manage-fluent-bit.sh

echo " 9단계: 설치 완료 확인"
# 설치 확인
sleep 3
if systemctl is-active --quiet fluent-bit; then
    echo "🎉 Fluent Bit 설치 및 시작 완료!"
    echo ""
    echo "📋 설치 정보:"
    echo "- 바이너리: /opt/fluent-bit/bin/fluent-bit"
    echo "- 설정 파일: /etc/fluent-bit/fluent-bit.conf"
    echo "- 파서 파일: /etc/fluent-bit/parsers.conf"
    echo "- 데이터 디렉토리: /var/lib/fluent-bit"
    echo "- 로그 디렉토리: /var/log/fluent-bit"
    echo "- 게임 로그 디렉토리: /var/log/game-logs/"
    echo "- 관리 스크립트: /home/ec2-user/manage-fluent-bit.sh"
    echo "- HTTP API: http://localhost:2020"
    echo ""
    echo "🔧 사용법:"
    echo "- 상태 확인: ./manage-fluent-bit.sh status"
    echo "- 로그 확인: ./manage-fluent-bit.sh logs"
    echo "- 설정 검증: ./manage-fluent-bit.sh validate"
    echo "- 테스트: ./manage-fluent-bit.sh test"
    echo "- API 확인: ./manage-fluent-bit.sh api"
    echo "- 헬스 체크: ./manage-fluent-bit.sh health"
else
    echo " Fluent Bit 시작에 실패했습니다."
    echo "로그를 확인하세요: sudo journalctl -u fluent-bit -n 50"
    exit 1
fi

echo "=================================================="
echo " Fluent Bit 설치 완료!"
echo "=================================================="
