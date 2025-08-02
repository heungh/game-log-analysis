---
title: "Option 2: Vector 설치"
weight: 20
---

# Ubuntu 20.04에서 Vector 설치 가이드

Vector는 고성능 관찰 가능성 데이터 파이프라인으로, 로그, 메트릭, 트레이스를 수집, 변환 및 라우팅할 수 있는 현대적인 도구입니다. 낮은 리소스 사용량으로 효율적인 데이터 처리를 제공합니다.

## 사전 요구사항

- Ubuntu 20.04 LTS EC2 인스턴스
- 패키지 다운로드를 위한 인터넷 연결
- AWS 서비스에 대한 적절한 IAM 권한
- 기본적인 시스템 관리 지식

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
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates

# Vector DEB 패키지 다운로드
cd /tmp
wget https://github.com/vectordotdev/vector/releases/download/v0.34.1/vector_0.34.1-1_amd64.deb

# 패키지 설치
sudo dpkg -i vector_0.34.1-1_amd64.deb

# 의존성 문제 해결
sudo apt-get install -f -y
```

### 방법 2: 바이너리 설치 (대안)

```bash
# Vector 바이너리 다운로드
cd /tmp
wget https://github.com/vectordotdev/vector/releases/download/v0.34.1/vector-0.34.1-x86_64-unknown-linux-musl.tar.gz

# 압축 해제 및 설치
tar -xzf vector-0.34.1-x86_64-unknown-linux-musl.tar.gz
sudo cp vector-x86_64-unknown-linux-musl/bin/vector /usr/local/bin/
sudo chmod +x /usr/local/bin/vector

# Vector 사용자 생성
sudo useradd --system --shell /bin/false --home-dir /var/lib/vector vector
```

## 디렉토리 설정

```bash
# 필요한 디렉토리 생성
sudo mkdir -p /etc/vector
sudo mkdir -p /var/log/vector
sudo mkdir -p /var/lib/vector
sudo mkdir -p /var/log/game

# 적절한 소유권 설정
sudo chown -R vector:vector /etc/vector
sudo chown -R vector:vector /var/log/vector
sudo chown -R vector:vector /var/lib/vector
sudo chown ubuntu:ubuntu /var/log/game
```

## 설정

### 기본 설정 파일

메인 설정 파일을 생성합니다:

```bash
# Vector 설정 파일 생성
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

### 변환 기능이 포함된 고급 설정

```bash
# 고급 설정 파일 생성
sudo tee /etc/vector/vector.toml << 'EOF'
data_dir = "/var/lib/vector"

# 소스: 게임 로그 파일 모니터링
[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"
ignore_older_secs = 86400

# 변환: JSON 로그 파싱 및 데이터 보강
[transforms.parse_logs]
type = "remap"
inputs = ["game_logs"]
source = '''
. = parse_json!(.message) ?? .
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"
'''

# 싱크: 콘솔 출력 (테스트용)
[sinks.console]
type = "console"
inputs = ["parse_logs"]
encoding.codec = "json"

# 싱크: 파일 출력
[sinks.file_output]
type = "file"
inputs = ["parse_logs"]
path = "/var/log/vector/processed_logs.log"
encoding.codec = "json"
EOF
```

### AWS Kinesis 설정

```bash
# AWS Kinesis Streams용 설정
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

# 배치 설정
batch.max_events = 100
batch.timeout_secs = 5

# 재시도 설정
request.retry_attempts = 3
request.timeout_secs = 30
EOF
```

## 서비스 설정

### 파일 권한 설정

```bash
# 적절한 권한 설정
sudo chown vector:vector /etc/vector/vector.toml
sudo chmod 644 /etc/vector/vector.toml
```

### systemd 서비스 생성 (필요시)

```bash
# systemd 서비스 파일 생성
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

# systemd 데몬 리로드
sudo systemctl daemon-reload
```

## 서비스 관리

### Vector 시작 및 활성화

```bash
# 설정 검증
sudo vector validate /etc/vector/vector.toml

# 서비스 활성화 및 시작
sudo systemctl enable vector
sudo systemctl start vector

# 서비스 상태 확인
sudo systemctl status vector
```

### 설치 확인

```bash
# Vector 버전 확인
vector --version

# 서비스가 활성화되었는지 확인
sudo systemctl is-active vector

# 프로세스 확인
ps aux | grep vector

# 서비스 로그 확인
sudo journalctl -u vector -n 20
```

## 테스트

### 테스트 로그 생성

```bash
# 테스트 로그 생성 스크립트 생성
cat > ~/generate_vector_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/vector_test.log"
echo "Vector 테스트 로그 생성 시작..."

for i in {1..5}; do
    echo "$(date -Iseconds) - Vector 테스트 로그 항목 $i" >> $LOG_FILE
    echo "로그 항목 $i 생성됨"
    sleep 2
done

echo "테스트 로그 생성 완료!"
EOF

chmod +x ~/generate_vector_test_logs.sh

# 테스트 로그 생성 실행
~/generate_vector_test_logs.sh
```

### JSON 테스트 로그 생성

```bash
# JSON 형식 테스트 로그 생성
echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_123","action":"login","level":25}' >> /var/log/game/game.log

# 연속 테스트 로그 생성
cat > ~/continuous_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/continuous.log"
counter=1

while true; do
    echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_'$((RANDOM%100))'","action":"test_action","level":'$((RANDOM%50))',"counter":'$counter'}' >> $LOG_FILE
    echo "로그 항목 $counter 생성됨"
    counter=$((counter + 1))
    sleep 3
done
EOF

chmod +x ~/continuous_test_logs.sh

# 백그라운드에서 실행
nohup ~/continuous_test_logs.sh &
```

## 모니터링 및 문제 해결

### Vector 활동 모니터링

```bash
# 실시간 서비스 로그
sudo journalctl -u vector -f

# 처리된 로그 확인 (파일 싱크가 설정된 경우)
sudo tail -f /var/log/vector/processed_logs.log

# 리소스 사용량 모니터링
top -p $(pgrep vector)

# 네트워크 연결 확인
sudo ss -tulpn | grep vector
```

### 일반적인 문제

1. **서비스 시작 실패**
   ```bash
   sudo journalctl -u vector -n 50
   sudo systemctl restart vector
   ```

2. **설정 오류**
   ```bash
   sudo vector validate /etc/vector/vector.toml
   ```

3. **권한 문제**
   ```bash
   sudo chown -R vector:vector /var/lib/vector
   sudo chown -R vector:vector /var/log/vector
   ```

4. **파일 접근 문제**
   ```bash
   sudo chmod 644 /var/log/game/*.log
   sudo chown ubuntu:ubuntu /var/log/game
   ```

### 로그 파일 위치

- Vector 서비스 로그: `sudo journalctl -u vector`
- Vector 출력 로그: `/var/log/vector/`
- 설정 파일: `/etc/vector/vector.toml`
- 데이터 디렉토리: `/var/lib/vector/`
- 게임 로그: `/var/log/game/`

## 고급 설정

### 다중 소스 및 싱크

```toml
data_dir = "/var/lib/vector"

# 소스 1: 로그인 로그
[sources.login_logs]
type = "file"
include = ["/var/log/game/login*.log"]

# 소스 2: 게임플레이 로그
[sources.gameplay_logs]
type = "file"
include = ["/var/log/game/gameplay*.log"]

# 변환: 로그인 로그 처리
[transforms.process_login]
type = "remap"
inputs = ["login_logs"]
source = '''
. = parse_json!(.message) ?? .
.log_type = "login"
.processed_at = now()
'''

# 변환: 게임플레이 로그 처리
[transforms.process_gameplay]
type = "remap"
inputs = ["gameplay_logs"]
source = '''
. = parse_json!(.message) ?? .
.log_type = "gameplay"
.processed_at = now()
'''

# 싱크: 다른 Kinesis 스트림으로 전송
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

## 성능 튜닝

### 메모리 최적화

```toml
# vector.toml에 추가
[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
max_line_bytes = 102400
max_read_bytes = 2048
```

### 배치 처리

```toml
[sinks.kinesis_stream]
type = "aws_kinesis_streams"
inputs = ["parse_logs"]
stream_name = "game-log-stream"
region = "ap-northeast-1"
batch.max_events = 1000
batch.timeout_secs = 1
```

## 관리 명령어

```bash
# 서비스 시작
sudo systemctl start vector

# 서비스 중지
sudo systemctl stop vector

# 서비스 재시작
sudo systemctl restart vector

# 상태 확인
sudo systemctl status vector

# 로그 확인
sudo journalctl -u vector -f

# 설정 검증
sudo vector validate /etc/vector/vector.toml

# 설정 테스트
sudo vector test /etc/vector/vector.toml
```

## 고급 기능

### API 엔드포인트 활성화

```toml
# vector.toml에 추가
[api]
enabled = true
address = "0.0.0.0:8686"
```

API 사용 예제:

```bash
# 헬스 체크
curl http://localhost:8686/health

# 메트릭 확인
curl http://localhost:8686/metrics

# 설정 정보
curl http://localhost:8686/config
```

### 로그 필터링

```toml
# 에러 로그만 필터링
[transforms.filter_errors]
type = "filter"
inputs = ["parse_logs"]
condition = '.level == "ERROR" || .level == "WARN"'
```

### 데이터 샘플링

```toml
# 10%만 샘플링
[transforms.sample_logs]
type = "sample"
inputs = ["parse_logs"]
rate = 10
```

## 모니터링 설정

### CloudWatch 메트릭 전송

```toml
[sinks.cloudwatch_metrics]
type = "aws_cloudwatch_metrics"
inputs = ["parse_logs"]
namespace = "GameLogs/Vector"
region = "ap-northeast-1"
```

### Prometheus 메트릭

```toml
[sources.internal_metrics]
type = "internal_metrics"

[sinks.prometheus]
type = "prometheus_exporter"
inputs = ["internal_metrics"]
address = "0.0.0.0:9598"
```

## 다음 단계

Vector 설치 및 설정이 완료되면:

1. Amazon Kinesis Data Stream 또는 Data Firehose 생성
2. EC2 인스턴스에 대한 IAM 권한 설정
3. 스트림 세부 정보로 Vector 설정 업데이트
4. AWS 콘솔에서 데이터 흐름 모니터링
5. 모니터링을 위한 CloudWatch 대시보드 설정

자세한 정보는 [Vector 공식 문서](https://vector.dev/docs/)를 참조하세요.

## 참고 자료

- [Vector GitHub 저장소](https://github.com/vectordotdev/vector)
- [Vector 설정 예제](https://vector.dev/docs/reference/configuration/)
- [AWS 통합 가이드](https://vector.dev/docs/reference/configuration/sinks/aws_kinesis_streams/)
- [성능 튜닝 가이드](https://vector.dev/docs/administration/tuning/)
