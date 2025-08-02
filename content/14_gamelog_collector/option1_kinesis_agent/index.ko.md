---
title: "Option 1: Kinesis Agent 설치"
weight: 10
---

# Ubuntu 20.04에서 Kinesis Agent 설치 가이드

Amazon Kinesis Agent는 로그 파일을 모니터링하고 Amazon Kinesis Data Streams 또는 Amazon Data Firehose로 데이터를 전송하는 독립 실행형 Java 애플리케이션입니다.

## 사전 요구사항

- Ubuntu 20.04 LTS EC2 인스턴스
- Java 8 이상 설치
- Kinesis 서비스에 대한 적절한 IAM 권한
- 패키지 다운로드를 위한 인터넷 연결

## 시스템 정보 확인

먼저 시스템 정보를 확인합니다:

```bash
# Ubuntu 버전 확인
lsb_release -a

# 시스템 아키텍처 확인
uname -a

# 사용 가능한 디스크 공간 확인
df -h
```

## 설치 방법

### 방법 1: 직접 DEB 패키지 설치 (권장)

```bash
# 시스템 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 의존성 설치
sudo apt install -y wget curl openjdk-8-jdk

# JAVA_HOME 환경변수 설정
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc

# Kinesis Agent DEB 패키지 다운로드
cd /tmp
wget https://s3.amazonaws.com/kinesis-agent-install-packages/aws-kinesis-agent-latest.deb

# 패키지 설치
sudo dpkg -i aws-kinesis-agent-latest.deb

# 의존성 문제 해결
sudo apt-get install -f -y
```

### 방법 2: 수동 설치 (방법 1이 실패할 경우)

```bash
# Java 8 설치
sudo apt install -y openjdk-8-jdk

# 필요한 디렉토리 생성
sudo mkdir -p /usr/share/aws-kinesis-agent
sudo mkdir -p /etc/aws-kinesis
sudo mkdir -p /var/log/aws-kinesis-agent

# Kinesis Agent JAR 파일 다운로드
cd /usr/share/aws-kinesis-agent
sudo wget https://github.com/awslabs/amazon-kinesis-agent/releases/download/2.0.8/aws-kinesis-agent-2.0.8.jar

# 기본 설정 파일 생성
sudo tee /etc/aws-kinesis/agent.json << 'EOF'
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": []
}
EOF

# 실행 스크립트 생성
sudo tee /usr/bin/aws-kinesis-agent << 'EOF'
#!/bin/bash
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export JAVA_HOME
cd /usr/share/aws-kinesis-agent
$JAVA_HOME/bin/java -cp aws-kinesis-agent-2.0.8.jar com.amazon.kinesis.streaming.agent.Agent
EOF

sudo chmod +x /usr/bin/aws-kinesis-agent

# systemd 서비스 파일 생성
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

# systemd 데몬 리로드
sudo systemctl daemon-reload
```

## 서비스 설정 및 시작

```bash
# 서비스 활성화 및 시작
sudo systemctl enable aws-kinesis-agent
sudo systemctl start aws-kinesis-agent

# 서비스 상태 확인
sudo systemctl status aws-kinesis-agent

# 서비스 로그 확인
sudo journalctl -u aws-kinesis-agent -f
```

## 설정

### 기본 설정 예제

설정 파일을 편집합니다:

```bash
sudo nano /etc/aws-kinesis/agent.json
```

설정 예제:

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

### 설정 옵션

- `cloudwatch.emitMetrics`: CloudWatch 메트릭 활성화
- `kinesis.endpoint`: Kinesis 엔드포인트 (기본값은 빈 문자열)
- `firehose.endpoint`: Firehose 엔드포인트 (기본값은 빈 문자열)
- `flows`: 로그 파일 처리 규칙 배열

### Flow 설정

- `filePattern`: 모니터링할 로그 파일 패턴
- `kinesisStream`: 대상 Kinesis 스트림 이름
- `partitionKeyOption`: 파티션 키 옵션 (RANDOM, DETERMINISTIC)

## 테스트

### 테스트 로그 디렉토리 생성

```bash
# 게임 로그 디렉토리 생성
sudo mkdir -p /var/log/game
sudo chown ubuntu:ubuntu /var/log/game
```

### 테스트 로그 생성

```bash
# 테스트 로그 생성 스크립트 생성
cat > ~/generate_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/game.log"
while true; do
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"user_id\":\"user_$((RANDOM%1000))\",\"action\":\"login\",\"level\":$((RANDOM%100))}" >> $LOG_FILE
    sleep 1
done
EOF

chmod +x ~/generate_test_logs.sh

# 백그라운드에서 테스트 로그 생성 실행
nohup ~/generate_test_logs.sh &

# 로그 파일 모니터링
tail -f /var/log/game/game.log
```

## 설치 확인

### 설치 상태 확인

```bash
# 서비스가 실행 중인지 확인
sudo systemctl is-active aws-kinesis-agent

# 프로세스 확인
ps aux | grep kinesis

# 최근 로그 확인
sudo journalctl -u aws-kinesis-agent --no-pager -n 20
```

### 성능 모니터링

```bash
# 리소스 사용량 확인
top -p $(pgrep -f kinesis)

# 네트워크 연결 확인
sudo ss -tulpn | grep java
```

## 문제 해결

### 일반적인 문제

1. **서비스 시작 실패**
   ```bash
   sudo journalctl -u aws-kinesis-agent -n 50
   sudo systemctl restart aws-kinesis-agent
   ```

2. **Java를 찾을 수 없음**
   ```bash
   java -version
   sudo update-alternatives --config java
   ```

3. **권한 문제**
   ```bash
   sudo chown -R root:root /usr/share/aws-kinesis-agent
   sudo chmod 755 /usr/bin/aws-kinesis-agent
   ```

4. **설정 오류**
   ```bash
   # JSON 설정 검증
   python3 -m json.tool /etc/aws-kinesis/agent.json
   ```

### 로그 파일 위치

- 에이전트 로그: `/var/log/aws-kinesis-agent/aws-kinesis-agent.log`
- 시스템 로그: `sudo journalctl -u aws-kinesis-agent`
- 게임 로그: `/var/log/game/`

## 관리 명령어

```bash
# 서비스 시작
sudo systemctl start aws-kinesis-agent

# 서비스 중지
sudo systemctl stop aws-kinesis-agent

# 서비스 재시작
sudo systemctl restart aws-kinesis-agent

# 상태 확인
sudo systemctl status aws-kinesis-agent

# 로그 확인
sudo journalctl -u aws-kinesis-agent -f

# 설정 다시 로드
sudo systemctl reload aws-kinesis-agent
```

## 고급 설정

### 다중 스트림 설정

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

### 데이터 변환 설정

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

## 성능 튜닝

### JVM 옵션 설정

실행 스크립트를 수정하여 JVM 옵션을 추가할 수 있습니다:

```bash
sudo nano /usr/bin/aws-kinesis-agent
```

```bash
#!/bin/bash
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export JAVA_HOME
cd /usr/share/aws-kinesis-agent
$JAVA_HOME/bin/java -Xmx512m -Xms256m -cp aws-kinesis-agent-2.0.8.jar com.amazon.kinesis.streaming.agent.Agent
```

### 모니터링 설정

CloudWatch 메트릭을 활성화하여 성능을 모니터링할 수 있습니다:

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

## 다음 단계

Kinesis Agent 설치 및 설정이 완료되면:

1. Amazon Kinesis Data Stream 또는 Data Firehose 생성
2. EC2 인스턴스에 대한 IAM 권한 설정
3. 스트림 세부 정보로 에이전트 설정 업데이트
4. AWS 콘솔에서 데이터 흐름 모니터링

자세한 정보는 [Amazon Kinesis Agent 공식 문서](https://docs.aws.amazon.com/ko_kr/kinesis/latest/dev/writing-with-agents.html)를 참조하세요.

## 참고 자료

- [Amazon Kinesis Agent GitHub](https://github.com/awslabs/amazon-kinesis-agent)
- [Kinesis Data Streams 개발자 가이드](https://docs.aws.amazon.com/ko_kr/kinesis/latest/dev/)
- [Kinesis Data Firehose 개발자 가이드](https://docs.aws.amazon.com/ko_kr/firehose/latest/dev/)
