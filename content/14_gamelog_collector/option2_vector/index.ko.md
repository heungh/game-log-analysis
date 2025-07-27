+++
title = "Option 2: Vector 설치"
weight = 20
+++

# Vector 설치 가이드

Vector는 고성능 관찰 가능성 데이터 파이프라인으로, 로그, 메트릭, 트레이스를 수집, 변환 및 라우팅할 수 있는 현대적인 도구입니다.

## 사전 요구사항

- Amazon Linux 2023 인스턴스
- curl, wget, tar, gzip 패키지
- 적절한 IAM 권한 (CloudWatch, S3, Kinesis 접근 권한)

## 자동 설치

다음 스크립트를 사용하여 Vector를 자동으로 설치할 수 있습니다:

```bash
curl -O https://raw.githubusercontent.com/your-repo/game-log-analytics/main/static/scripts/install-vector.sh
chmod +x install-vector.sh
sudo ./install-vector.sh
```

## 수동 설치 단계

### 1단계: 필수 패키지 설치

```bash
# 시스템 업데이트 및 필수 패키지 설치
sudo yum update -y
sudo yum install -y curl wget tar gzip
```

### 2단계: Vector 다운로드 및 설치

```bash
# Vector 버전 설정
VECTOR_VERSION="0.34.1"
VECTOR_ARCH="x86_64"
VECTOR_URL="https://packages.timber.io/vector/${VECTOR_VERSION}/vector-${VECTOR_VERSION}-${VECTOR_ARCH}-unknown-linux-musl.tar.gz"

# 임시 디렉토리로 이동
cd /tmp

# Vector 다운로드
wget -O vector.tar.gz "$VECTOR_URL"

# 압축 해제
tar -xzf vector.tar.gz
cd vector-*

# 바이너리 설치
sudo cp bin/vector /usr/local/bin/
sudo chmod +x /usr/local/bin/vector
```

### 3단계: 사용자 및 디렉토리 생성

```bash
# Vector 시스템 사용자 생성
sudo useradd --system --shell /bin/false --home-dir /var/lib/vector vector

# 필요한 디렉토리 생성
sudo mkdir -p /etc/vector
sudo mkdir -p /var/lib/vector
sudo mkdir -p /var/log/vector
sudo mkdir -p /var/log/game-logs

# 권한 설정
sudo chown -R vector:vector /var/lib/vector
sudo chown -R vector:vector /var/log/vector
sudo chown -R ec2-user:ec2-user /var/log/game-logs
```

### 4단계: Vector 설정 파일 생성

```bash
sudo tee /etc/vector/vector.toml << 'EOF'
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
```

### 5단계: systemd 서비스 파일 생성

```bash
sudo tee /etc/systemd/system/vector.service << 'EOF'
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
```

### 6단계: 서비스 시작

```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 및 시작
sudo systemctl enable vector
sudo systemctl start vector

# 상태 확인
sudo systemctl status vector
```

## 설정 파일 상세 설명

### Sources (입력)

- `file`: 로그 파일 모니터링
- `journald`: systemd 저널 로그 수집

### Transforms (변환)

- `remap`: 로그 데이터 파싱 및 변환
- `filter`: 조건에 따른 로그 필터링

### Sinks (출력)

- `aws_cloudwatch_logs`: CloudWatch Logs로 전송
- `aws_s3`: S3 버킷으로 아카이브
- `aws_kinesis_streams`: Kinesis Data Streams로 전송
- `console`: 콘솔 출력 (디버깅용)

## 관리 명령어

설치 후 다음 관리 스크립트를 사용할 수 있습니다:

```bash
# 관리 스크립트 사용법
./manage-vector.sh {start|stop|restart|status|logs|config|validate|test|api|metrics}
```

### 주요 명령어

```bash
# 서비스 상태 확인
./manage-vector.sh status

# 로그 실시간 확인
./manage-vector.sh logs

# 설정 파일 검증
./manage-vector.sh validate

# 테스트 로그 생성
./manage-vector.sh test

# API 상태 확인
./manage-vector.sh api

# 메트릭 확인
./manage-vector.sh metrics
```

## API 엔드포인트

Vector는 HTTP API를 제공합니다 (포트 8686):

```bash
# 헬스 체크
curl http://localhost:8686/health

# 메트릭 확인
curl http://localhost:8686/metrics

# 설정 정보
curl http://localhost:8686/config
```

## 테스트

설치가 완료되면 테스트 로그를 생성하여 정상 작동을 확인할 수 있습니다:

```bash
# 테스트 로그 생성
echo '{"timestamp":"'$(date -Iseconds)'","level":"INFO","message":"Test game event","player_id":"test123","event_type":"login"}' >> /var/log/game-logs/game.log

# Vector 로그 확인
sudo journalctl -u vector -f
```

## 문제 해결

### 일반적인 문제

1. **서비스 시작 실패**
   ```bash
   sudo journalctl -u vector -n 50
   ```

2. **설정 파일 오류**
   ```bash
   sudo /usr/local/bin/vector validate /etc/vector/vector.toml
   ```

3. **권한 문제**
   ```bash
   sudo chown -R vector:vector /var/lib/vector
   sudo chown -R vector:vector /var/log/vector
   ```

### 로그 파일 위치

- Vector 로그: `sudo journalctl -u vector`
- 설치 로그: `/var/log/vector-install.log`
- 게임 로그: `/var/log/game-logs/`
- Vector 데이터: `/var/lib/vector/`

## 성능 최적화

### 메모리 사용량 최적화

```toml
# vector.toml에 추가
[sources.game_logs]
type = "file"
include = ["/var/log/game-logs/*.log"]
max_line_bytes = 102400
max_read_bytes = 2048
```

### 배치 처리 최적화

```toml
[sinks.cloudwatch_logs]
type = "aws_cloudwatch_logs"
batch.max_events = 1000
batch.timeout_secs = 1
```

## 다음 단계

Vector 설치가 완료되면:

1. 로그 파싱 규칙 세부 조정
2. 메트릭 및 알람 설정
3. 대시보드 구성
4. 성능 모니터링 설정

자세한 내용은 [Vector 공식 문서](https://vector.dev/docs/)를 참조하세요.
