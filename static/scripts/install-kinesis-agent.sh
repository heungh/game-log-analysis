#!/bin/bash

# Kinesis Agent 설치 스크립트
# Amazon Linux 2023용

set -e

echo "=================================================="
echo " Kinesis Agent 설치 시작"
echo "=================================================="

# 로그 파일 설정
LOG_FILE="/var/log/kinesis-agent-install.log"
exec > >(tee -a $LOG_FILE) 2>&1

echo " 1단계: Java 설치 확인 및 설치"
# Java 8 또는 11 설치 (Kinesis Agent 요구사항)
if ! java -version 2>&1 | grep -q "openjdk version"; then
    echo "Java가 설치되어 있지 않습니다. OpenJDK 11을 설치합니다..."
    yum install -y java-11-amazon-corretto-headless
else
    echo "Java가 이미 설치되어 있습니다."
fi

echo " 2단계: Kinesis Agent 다운로드 및 설치"
# Kinesis Agent RPM 다운로드 및 설치
cd /tmp
wget https://s3.amazonaws.com/streaming-data-agent/aws-kinesis-agent-latest.amzn2.noarch.rpm

# RPM 설치
yum localinstall -y aws-kinesis-agent-latest.amzn2.noarch.rpm

echo " 3단계: Kinesis Agent 설정 디렉토리 생성"
# 설정 디렉토리 및 로그 디렉토리 생성
mkdir -p /etc/aws-kinesis
mkdir -p /var/log/aws-kinesis-agent
mkdir -p /opt/aws/kinesis-agent/logs

echo " 4단계: 기본 설정 파일 생성"
# 기본 설정 파일 생성
cat > /etc/aws-kinesis/agent.json << 'EOF'
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": [
    {
      "filePattern": "/var/log/game-logs/*.log",
      "kinesisStream": "game-log-stream",
      "partitionKeyOption": "RANDOM"
    }
  ]
}
EOF

echo " 5단계: 로그 디렉토리 생성"
# 게임 로그 디렉토리 생성
mkdir -p /var/log/game-logs
chown ec2-user:ec2-user /var/log/game-logs

echo " 6단계: Kinesis Agent 서비스 설정"
# 서비스 활성화 및 시작
systemctl enable aws-kinesis-agent
systemctl start aws-kinesis-agent

echo " 7단계: 관리 스크립트 생성"
# Kinesis Agent 관리 스크립트 생성
cat > /home/ec2-user/manage-kinesis-agent.sh << 'EOF'
#!/bin/bash

echo "=================================================="
echo "🔧 Kinesis Agent 관리 스크립트"
echo "=================================================="

case "$1" in
    start)
        echo "Kinesis Agent 시작 중..."
        sudo systemctl start aws-kinesis-agent
        echo " Kinesis Agent가 시작되었습니다."
        ;;
    stop)
        echo "Kinesis Agent 중지 중..."
        sudo systemctl stop aws-kinesis-agent
        echo " Kinesis Agent가 중지되었습니다."
        ;;
    restart)
        echo "Kinesis Agent 재시작 중..."
        sudo systemctl restart aws-kinesis-agent
        echo " Kinesis Agent가 재시작되었습니다."
        ;;
    status)
        echo "Kinesis Agent 상태 확인 중..."
        sudo systemctl status aws-kinesis-agent
        ;;
    logs)
        echo "Kinesis Agent 로그 확인 중..."
        sudo tail -f /var/log/aws-kinesis-agent/aws-kinesis-agent.log
        ;;
    config)
        echo "Kinesis Agent 설정 파일 편집..."
        sudo nano /etc/aws-kinesis/agent.json
        ;;
    test)
        echo "테스트 로그 생성 중..."
        echo "$(date): Test game log entry from Kinesis Agent" >> /var/log/game-logs/game.log
        echo " 테스트 로그가 생성되었습니다."
        ;;
    *)
        echo "사용법: $0 {start|stop|restart|status|logs|config|test}"
        echo ""
        echo "명령어 설명:"
        echo "  start   - Kinesis Agent 시작"
        echo "  stop    - Kinesis Agent 중지"
        echo "  restart - Kinesis Agent 재시작"
        echo "  status  - Kinesis Agent 상태 확인"
        echo "  logs    - Kinesis Agent 로그 실시간 확인"
        echo "  config  - 설정 파일 편집"
        echo "  test    - 테스트 로그 생성"
        exit 1
        ;;
esac
EOF

chmod +x /home/ec2-user/manage-kinesis-agent.sh
chown ec2-user:ec2-user /home/ec2-user/manage-kinesis-agent.sh

echo " 8단계: 설치 완료 확인"
# 설치 확인
if systemctl is-active --quiet aws-kinesis-agent; then
    echo "🎉 Kinesis Agent 설치 및 시작 완료!"
    echo ""
    echo "📋 설치 정보:"
    echo "- 설정 파일: /etc/aws-kinesis/agent.json"
    echo "- 로그 파일: /var/log/aws-kinesis-agent/aws-kinesis-agent.log"
    echo "- 게임 로그 디렉토리: /var/log/game-logs/"
    echo "- 관리 스크립트: /home/ec2-user/manage-kinesis-agent.sh"
    echo ""
    echo "🔧 사용법:"
    echo "- 상태 확인: ./manage-kinesis-agent.sh status"
    echo "- 로그 확인: ./manage-kinesis-agent.sh logs"
    echo "- 테스트: ./manage-kinesis-agent.sh test"
else
    echo " Kinesis Agent 시작에 실패했습니다."
    echo "로그를 확인하세요: sudo journalctl -u aws-kinesis-agent -n 50"
    exit 1
fi

echo "=================================================="
echo " Kinesis Agent 설치 완료!"
echo "=================================================="
