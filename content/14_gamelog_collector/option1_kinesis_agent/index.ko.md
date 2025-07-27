---
title: "Option 1: Kinesis Agent 설치"
weight: 10
---

# Kinesis Agent 설치 가이드

Amazon Kinesis Agent는 로그 파일을 모니터링하고 Amazon Kinesis Data Streams 또는 Amazon Data Firehose로 데이터를 전송하는 독립 실행형 Java 애플리케이션입니다.

## 사전 요구사항

- Amazon Linux 2023 인스턴스
- Java 8 또는 11
- 적절한 IAM 권한 (Kinesis 스트림에 대한 쓰기 권한)

## 자동 설치

다음 스크립트를 사용하여 Kinesis Agent를 자동으로 설치할 수 있습니다:

```bash
curl -O https://raw.githubusercontent.com/your-repo/game-log-analytics/main/static/scripts/install-kinesis-agent.sh
chmod +x install-kinesis-agent.sh
sudo ./install-kinesis-agent.sh
```

## 수동 설치 단계

### 1단계: Java 설치

```bash
# Java 설치 확인
java -version

# Java가 설치되어 있지 않은 경우
sudo yum install -y java-11-amazon-corretto-headless
```

### 2단계: Kinesis Agent 다운로드 및 설치

```bash
# 임시 디렉토리로 이동
cd /tmp

# Kinesis Agent RPM 다운로드
wget https://s3.amazonaws.com/streaming-data-agent/aws-kinesis-agent-latest.amzn2.noarch.rpm

# RPM 설치
sudo yum localinstall -y aws-kinesis-agent-latest.amzn2.noarch.rpm
```

### 3단계: 디렉토리 생성

```bash
# 설정 및 로그 디렉토리 생성
sudo mkdir -p /etc/aws-kinesis
sudo mkdir -p /var/log/aws-kinesis-agent
sudo mkdir -p /opt/aws/kinesis-agent/logs
sudo mkdir -p /var/log/game-logs

# 권한 설정
sudo chown ec2-user:ec2-user /var/log/game-logs
```

### 4단계: 설정 파일 생성

기본 설정 파일을 생성합니다:

```bash
sudo tee /etc/aws-kinesis/agent.json << 'EOF'
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
```

### 5단계: 서비스 시작

```bash
# 서비스 활성화 및 시작
sudo systemctl enable aws-kinesis-agent
sudo systemctl start aws-kinesis-agent

# 상태 확인
sudo systemctl status aws-kinesis-agent
```

## 설정 파일 상세 설명

### 주요 설정 옵션

- `cloudwatch.emitMetrics`: CloudWatch 메트릭 전송 여부
- `kinesis.endpoint`: Kinesis 엔드포인트 (기본값 사용시 빈 문자열)
- `firehose.endpoint`: Firehose 엔드포인트 (기본값 사용시 빈 문자열)
- `flows`: 로그 파일 처리 규칙 배열

### Flow 설정 옵션

- `filePattern`: 모니터링할 로그 파일 패턴
- `kinesisStream`: 대상 Kinesis 스트림 이름
- `partitionKeyOption`: 파티션 키 옵션 (RANDOM, DETERMINISTIC)

## 관리 명령어

설치 후 다음 관리 스크립트를 사용할 수 있습니다:

```bash
# 관리 스크립트 사용법
./manage-kinesis-agent.sh {start|stop|restart|status|logs|config|test}
```

### 주요 명령어

```bash
# 서비스 상태 확인
./manage-kinesis-agent.sh status

# 로그 실시간 확인
./manage-kinesis-agent.sh logs

# 설정 파일 편집
./manage-kinesis-agent.sh config

# 테스트 로그 생성
./manage-kinesis-agent.sh test

# 서비스 재시작
./manage-kinesis-agent.sh restart
```

## 테스트

설치가 완료되면 테스트 로그를 생성하여 정상 작동을 확인할 수 있습니다:

```bash
# 테스트 로그 생성
echo "$(date): Test game log entry from Kinesis Agent" >> /var/log/game-logs/game.log

# 로그 확인
sudo tail -f /var/log/aws-kinesis-agent/aws-kinesis-agent.log
```

## 문제 해결

### 일반적인 문제

1. **서비스 시작 실패**
   ```bash
   sudo journalctl -u aws-kinesis-agent -n 50
   ```

2. **권한 문제**
   ```bash
   sudo chown -R aws-kinesis-agent:aws-kinesis-agent /var/log/aws-kinesis-agent
   ```

3. **Java 버전 문제**
   ```bash
   java -version
   sudo alternatives --config java
   ```

### 로그 파일 위치

- 에이전트 로그: `/var/log/aws-kinesis-agent/aws-kinesis-agent.log`
- 설치 로그: `/var/log/kinesis-agent-install.log`
- 게임 로그: `/var/log/game-logs/`

## 다음 단계

Kinesis Agent 설치가 완료되면 Amazon Data Firehose를 생성하고 데이터 스트림을 Firehose로 보내는 방법을 진행하게 됩니다.