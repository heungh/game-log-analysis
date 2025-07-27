#!/bin/bash

# Vector 설치 스크립트
# Amazon Linux 2023용

set -e

echo "=================================================="
echo " Vector 설치 시작"
echo "=================================================="

# 로그 파일 설정
LOG_FILE="/var/log/vector-install.log"
exec > >(tee -a $LOG_FILE) 2>&1

echo " 1단계: 필수 패키지 설치"
# 필수 패키지 설치
yum update -y
yum install -y curl wget tar gzip

echo " 2단계: Vector 다운로드 및 설치"
# Vector 최신 버전 다운로드
VECTOR_VERSION="0.34.1"
VECTOR_ARCH="x86_64"
VECTOR_URL="https://packages.timber.io/vector/${VECTOR_VERSION}/vector-${VECTOR_VERSION}-${VECTOR_ARCH}-unknown-linux-musl.tar.gz"

cd /tmp
echo "Vector 다운로드 중... ($VECTOR_URL)"
wget -O vector.tar.gz "$VECTOR_URL"

# 압축 해제 및 설치
tar -xzf vector.tar.gz
cd vector-*

# Vector 바이너리를 시스템 경로에 복사
cp bin/vector /usr/local/bin/
chmod +x /usr/local/bin/vector

echo " 3단계: Vector 사용자 및 디렉토리 생성"
# Vector 사용자 생성
useradd --system --shell /bin/false --home-dir /var/lib/vector vector || true

# 필요한 디렉토리 생성
mkdir -p /etc/vector
mkdir -p /var/lib/vector
mkdir -p /var/log/vector
mkdir -p /var/log/game-logs

# 권한 설정
chown -R vector:vector /var/lib/vector
chown -R vector:vector /var/log/vector
chown -R ec2-user:ec2-user /var/log/game-logs

echo " 4단계: Vector 설정 파일 생성"
# Vector 설정 파일 생성
cat > /etc/vector/vector.toml << 'EOF'
# Vector Configuration for Game Log Processing

# Data directory
data_dir = "/var/lib/vector"

# Sources - 게임 로그 파일 모니터링
[sources.game_logs]
type = "file"
include = ["/var/log/game-logs/*.log"]
read_from = "beginning"

# Sources - 시스템 로그 모니터링 (선택사항)
[sources.system_logs]
type = "journald"
current_boot_only = true

# Transforms - 로그 파싱 및 변환
[transforms.parse_game_logs]
type = "remap"
inputs = ["game_logs"]
source = '''
  . = parse_json!(.message)
  .timestamp = now()
  .source = "game-server"
'''

# Transforms - 로그 필터링
[transforms.filter_errors]
type = "filter"
inputs = ["parse_game_logs"]
condition = '.level == "ERROR" || .level == "WARN"'

# Sinks - CloudWatch Logs로 전송
[sinks.cloudwatch_logs]
type = "aws_cloudwatch_logs"
inputs = ["parse_game_logs"]
group_name = "/aws/ec2/vector/game-logs"
stream_name = "{{ hostname }}"
region = "us-east-1"
encoding.codec = "json"

# Sinks - S3로 전송 (아카이브용)
[sinks.s3_archive]
type = "aws_s3"
inputs = ["parse_game_logs"]
bucket = "datapipelinebucket{{ env_var!("AWS_ACCOUNT_ID") }}us-east-1"
key_prefix = "game-logs/year=%Y/month=%m/day=%d/"
region = "us-east-1"
encoding.codec = "json"
compression = "gzip"

# Sinks - Kinesis Data Streams로 전송
[sinks.kinesis_stream]
type = "aws_kinesis_streams"
inputs = ["parse_game_logs"]
stream_name = "game-log-stream"
region = "us-east-1"
encoding.codec = "json"

# Sinks - 콘솔 출력 (디버깅용)
[sinks.console]
type = "console"
inputs = ["parse_game_logs"]
encoding.codec = "json"

# API 설정
[api]
enabled = true
address = "0.0.0.0:8686"
EOF

echo " 5단계: systemd 서비스 파일 생성"
# systemd 서비스 파일 생성
cat > /etc/systemd/system/vector.service << 'EOF'
[Unit]
Description=Vector log collector
Documentation=https://vector.dev
After=network-online.target
Requires=network-online.target

[Service]
User=vector
Group=vector
ExecStart=/usr/local/bin/vector --config /etc/vector/vector.toml
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=2
StandardOutput=journal
StandardError=journal
SyslogIdentifier=vector
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
EOF

echo " 6단계: Vector 서비스 시작"
# systemd 데몬 리로드 및 서비스 시작
systemctl daemon-reload
systemctl enable vector
systemctl start vector

echo " 7단계: 관리 스크립트 생성"
# Vector 관리 스크립트 생성
cat > /home/ec2-user/manage-vector.sh << 'EOF'
#!/bin/bash

echo "=================================================="
echo "🔧 Vector 관리 스크립트"
echo "=================================================="

case "$1" in
    start)
        echo "Vector 시작 중..."
        sudo systemctl start vector
        echo " Vector가 시작되었습니다."
        ;;
    stop)
        echo "Vector 중지 중..."
        sudo systemctl stop vector
        echo " Vector가 중지되었습니다."
        ;;
    restart)
        echo "Vector 재시작 중..."
        sudo systemctl restart vector
        echo " Vector가 재시작되었습니다."
        ;;
    status)
        echo "Vector 상태 확인 중..."
        sudo systemctl status vector
        ;;
    logs)
        echo "Vector 로그 확인 중..."
        sudo journalctl -u vector -f
        ;;
    config)
        echo "Vector 설정 파일 편집..."
        sudo nano /etc/vector/vector.toml
        ;;
    validate)
        echo "Vector 설정 파일 검증 중..."
        sudo /usr/local/bin/vector validate /etc/vector/vector.toml
        ;;
    test)
        echo "테스트 로그 생성 중..."
        echo '{"timestamp":"'$(date -Iseconds)'","level":"INFO","message":"Test game event","player_id":"test123","event_type":"login"}' >> /var/log/game-logs/game.log
        echo " 테스트 로그가 생성되었습니다."
        ;;
    api)
        echo "Vector API 상태 확인 중..."
        curl -s http://localhost:8686/health | jq . || echo "API 응답 없음 또는 jq 미설치"
        ;;
    metrics)
        echo "Vector 메트릭 확인 중..."
        curl -s http://localhost:8686/metrics
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs|config|validate|test|api|metrics}"
        echo ""
        echo "명령어 설명:"
        echo "  start    - Vector 시작"
        echo "  stop     - Vector 중지"
        echo "  restart  - Vector 재시작"
        echo "  status   - Vector 상태 확인"
        echo "  logs     - Vector 로그 실시간 확인"
        echo "  config   - 설정 파일 편집"
        echo "  validate - 설정 파일 검증"
        echo "  test     - 테스트 로그 생성"
        echo "  api      - API 상태 확인"
        echo "  metrics  - 메트릭 확인"
        exit 1
        ;;
esac
EOF

chmod +x /home/ec2-user/manage-vector.sh
chown ec2-user:ec2-user /home/ec2-user/manage-vector.sh

echo " 8단계: 설치 완료 확인"
# 설치 확인
sleep 3
if systemctl is-active --quiet vector; then
    echo "🎉 Vector 설치 및 시작 완료!"
    echo ""
    echo "📋 설치 정보:"
    echo "- 바이너리: /usr/local/bin/vector"
    echo "- 설정 파일: /etc/vector/vector.toml"
    echo "- 데이터 디렉토리: /var/lib/vector"
    echo "- 로그 디렉토리: /var/log/vector"
    echo "- 게임 로그 디렉토리: /var/log/game-logs/"
    echo "- 관리 스크립트: /home/ec2-user/manage-vector.sh"
    echo "- API 엔드포인트: http://localhost:8686"
    echo ""
    echo "🔧 사용법:"
    echo "- 상태 확인: ./manage-vector.sh status"
    echo "- 로그 확인: ./manage-vector.sh logs"
    echo "- 설정 검증: ./manage-vector.sh validate"
    echo "- 테스트: ./manage-vector.sh test"
    echo "- API 확인: ./manage-vector.sh api"
else
    echo " Vector 시작에 실패했습니다."
    echo "로그를 확인하세요: sudo journalctl -u vector -n 50"
    exit 1
fi

echo "=================================================="
echo " Vector 설치 완료!"
echo "=================================================="
