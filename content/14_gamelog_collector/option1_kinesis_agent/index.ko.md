---
title: "Option 1: Kinesis Agent 설치"
weight: 10
---

# Ubuntu 20.04에서 Kinesis Agent 설치 가이드

Amazon Kinesis Agent는 로그 파일을 모니터링하고 Amazon Kinesis Data Streams 또는 Amazon Data Firehose로 데이터를 전송하는 독립 실행형 Java 애플리케이션입니다.

## 사전 요구사항

- Ubuntu 20.04 LTS EC2 인스턴스
- Java 11 이상 설치
- AWS 서비스에 대한 적절한 IAM 권한
- 패키지 다운로드를 위한 인터넷 연결
- 소스 빌드를 위한 Git 및 Maven

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

## 설치 방법: GitHub 소스에서 빌드

키네시스 에이전트는 현재 binary 파일이 제공되지 않아 Github 소스에서 최신버전을 빌드해서 사용할수 있습니다. 

```bash
# 필요한 도구 설치 (Java, Maven 설치)
sudo apt update
sudo apt install -y git maven openjdk-11-jdk


# Java 및 Maven 버전 확인
java -version
mvn -version
```

자바와 메이븐 버전을 확인하여 설치가 정상적으로 되었다면, 아래와 같이 키네시스 에이전트를 빌드합니다. 

```bash
# 필요한 디렉토리 생성
sudo mkdir -p /usr/share/aws-kinesis-agent
sudo mkdir -p /etc/aws-kinesis
sudo mkdir -p /var/log/aws-kinesis-agent

# GitHub에서 소스 코드 클론
git clone https://github.com/awslabs/amazon-kinesis-agent.git
cd amazon-kinesis-agent

# 최신 태그 확인 (선택사항)
git tag --sort=-version:refname | head -5

# 빌드 (테스트 스킵으로 빠르게)
mvn clean package -DskipTests

# 빌드 결과 확인
ls -la target/
```

키네시스 에이전트를 빌드하고 만들어진 Jar파일을 옮기는 등의 환경설정 작업을 진행합니다. 
```bash
# 의존성을 lib 디렉토리로 복사
mvn dependency:copy-dependencies -DoutputDirectory=/tmp/kinesis-deps
sudo mkdir -p /usr/share/aws-kinesis-agent/lib
sudo cp /tmp/kinesis-deps/*.jar /usr/share/aws-kinesis-agent/lib/

# 메인 JAR 파일을 시스템 위치로 복사 (파일명이 amazon-kinesis-agent임에 주의)
sudo cp target/amazon-kinesis-agent-*.jar /usr/share/aws-kinesis-agent/

# 정확한 JAR 파일명 확인
ls -la /usr/share/aws-kinesis-agent/amazon-kinesis-agent-*.jar

# 기본 설정 파일 생성
sudo tee /etc/aws-kinesis/agent.json << 'EOF'
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": []
}
EOF
```
키네시스 에이전트의 환경설정 파일부분은 위와 같이 공백으로 남겨두고 이어지는 실습에서 다시 설정하도록 하겠습니다.
다음은 설정된 환경을 바탕으로 실행스크립트를 만들고 서비스를 구동시키는 작업입니다. 

```bash
# 정확한 JAR 파일명으로 실행 스크립트 생성 (2.0.13을 실제 버전으로 교체)
# 먼저 정확한 버전 번호 확인
VERSION=$(ls /usr/share/aws-kinesis-agent/amazon-kinesis-agent-*.jar | sed 's/.*amazon-kinesis-agent-\(.*\)\.jar/\1/')
echo "감지된 버전: $VERSION"

# 정확한 파일명으로 실행 스크립트 생성
sudo tee /usr/bin/aws-kinesis-agent << EOF
#!/bin/bash
CLASSPATH="/usr/share/aws-kinesis-agent/amazon-kinesis-agent-${VERSION}.jar:/usr/share/aws-kinesis-agent/lib/*"
java -cp "\$CLASSPATH" \\
     -Daws.kinesis.agent.config.file=/etc/aws-kinesis/agent.json \\
     -Dlog4j.configuration=file:///etc/aws-kinesis/log4j.properties \\
     com.amazon.kinesis.streaming.agent.Agent "\$@"
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

# 설치 확인
ls -la /usr/share/aws-kinesis-agent/
echo "의존성 JAR 파일 개수:"
ls /usr/share/aws-kinesis-agent/lib/ | wc -l
aws-kinesis-agent --help
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
sudo vi /etc/aws-kinesis/agent.json
```

설정 예제:

```json
sudo tee /etc/aws-kinesis/agent.json > /dev/null <<EOF
{
  "cloudwatch.emitMetrics": true,
  "kinesis.endpoint": "",
  "firehose.endpoint": "",
  "flows": [
    {
      "filePattern": "/var/log/game/*.log",
      "kinesisStream": "game-log-stream",
      "deliveryStream": "game-log-df",
      "partitionKeyOption": "RANDOM"
    }
  ]
}
EOF

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
LOG_FILE="/var/log/game/test.log"
while true; do
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"user_id\":\"user_$((RANDOM%1000))\",\"action\":\"login\",\"level\":$((RANDOM%100))}" >> $LOG_FILE
    sleep 1
done
EOF

chmod +x ~/generate_test_logs.sh

# 백그라운드에서 테스트 로그 생성 실행
nohup ~/generate_test_logs.sh &

# 로그 파일 모니터링
tail -f /var/log/game/test.log
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

# 도움말 명령 테스트
aws-kinesis-agent --help
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

5. **클래스패스 문제 (가장 일반적)**
   ```bash
   # JAR 파일 확인
   ls -la /usr/share/aws-kinesis-agent/
   ls -la /usr/share/aws-kinesis-agent/lib/ | wc -l
   
   # 실행 스크립트가 정확한 JAR 파일명을 사용하는지 확인
   cat /usr/bin/aws-kinesis-agent
   
   # Java 직접 실행 테스트
   java -cp "/usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar:/usr/share/aws-kinesis-agent/lib/*" com.amazon.kinesis.streaming.agent.Agent --help
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
sudo vi /usr/bin/aws-kinesis-agent
```

```bash
#!/bin/bash
CLASSPATH="/usr/share/aws-kinesis-agent/amazon-kinesis-agent-2.0.13.jar:/usr/share/aws-kinesis-agent/lib/*"
java -Xmx512m -Xms256m -cp "$CLASSPATH" \
     -Daws.kinesis.agent.config.file=/etc/aws-kinesis/agent.json \
     -Dlog4j.configuration=file:///etc/aws-kinesis/log4j.properties \
     com.amazon.kinesis.streaming.agent.Agent "$@"
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

Kinesis Agent 설치 및 설정이 완료되면 다음과 같은 작업을 진행합니다. 

1. **Amazon Data Firehose 생성**
   - AWS 콘솔에서 Amazon Data Firehose 생성

2. **IAM 권한 설정**
   - EC2 인스턴스에 Kinesis 접근 권한 부여
   - 필요한 IAM 역할 및 정책 생성

3. **Kinesis Agent 설정 업데이트**
   - Amazon Data Firehose 정보로 설정 파일 업데이트
   - 배치 및 재시도 설정 최적화

자세한 정보는 [Amazon Kinesis Agent 공식 문서](https://docs.aws.amazon.com/ko_kr/kinesis/latest/dev/writing-with-agents.html)를 참조하세요.

## 참고 자료

- [Amazon Kinesis Agent GitHub](https://github.com/awslabs/amazon-kinesis-agent)
- [Kinesis Data Streams 개발자 가이드](https://docs.aws.amazon.com/ko_kr/kinesis/latest/dev/)
- [Amazon Data Firehose 개발자 가이드](https://docs.aws.amazon.com/ko_kr/firehose/latest/dev/)
