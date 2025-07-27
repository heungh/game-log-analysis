---
title: "Option 3: Fluent Bit 설치"
weight: 30
---

# Fluent Bit 설치 가이드

Fluent Bit은 경량화된 고성능 로그 프로세서 및 포워더로, 다양한 소스에서 데이터를 수집하고 여러 대상으로 전송할 수 있는 CNCF 프로젝트입니다.

## 사전 요구사항

- Amazon Linux 2023 인스턴스
- curl, wget, tar, gzip 패키지
- 적절한 IAM 권한 (CloudWatch, S3, Kinesis 접근 권한)

## 자동 설치

다음 스크립트를 사용하여 Fluent Bit을 자동으로 설치할 수 있습니다:

```bash
curl -O https://raw.githubusercontent.com/your-repo/game-log-analytics/main/static/scripts/install-fluent-bit.sh
chmod +x install-fluent-bit.sh
sudo ./install-fluent-bit.sh
```

## 수동 설치 단계

### 1단계: 필수 패키지 설치

```bash
# 시스템 업데이트 및 필수 패키지 설치
sudo yum update -y
sudo yum install -y curl wget tar gzip
```

### 2단계: Fluent Bit 리포지토리 추가

```bash
# Fluent Bit 공식 리포지토리 추가
sudo tee /etc/yum.repos.d/fluent-bit.repo << 'EOF'
[fluent-bit]
name = Fluent Bit
baseurl = https://packages.fluentbit.io/amazonlinux/2023/$basearch/
gpgcheck=1
gpgkey=https://packages.fluentbit.io/fluentbit.key
enabled=1
EOF
```

### 3단계: Fluent Bit 설치

```bash
# Fluent Bit 설치
sudo yum install -y fluent-bit
```

### 4단계: 디렉토리 생성 및 권한 설정

```bash
# 필요한 디렉토리 생성
sudo mkdir -p /etc/fluent-bit
sudo mkdir -p /var/log/fluent-bit
sudo mkdir -p /var/log/game-logs
sudo mkdir -p /var/lib/fluent-bit

# 권한 설정
sudo chown -R fluent-bit:fluent-bit /var/log/fluent-bit
sudo chown -R fluent-bit:fluent-bit /var/lib/fluent-bit
sudo chown -R ec2-user:ec2-user /var/log/game-logs
```

### 5단계: Fluent Bit 설정 파일 생성

#### 메인 설정 파일 생성

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

#### 파서 설정 파일 생성

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

### 6단계: systemd 서비스 설정

```bash
# systemd 서비스 파일 생성 (필요시)
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

### 7단계: 서비스 시작

```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 서비스 활성화 및 시작
sudo systemctl enable fluent-bit
sudo systemctl start fluent-bit

# 상태 확인
sudo systemctl status fluent-bit
```

## 설정 파일 상세 설명

### SERVICE 섹션

- `Flush`: 출력 플러시 간격 (초)
- `Log_Level`: 로그 레벨 (error, warn, info, debug, trace)
- `HTTP_Server`: HTTP 서버 활성화
- `HTTP_Port`: HTTP API 포트

### INPUT 섹션

- `tail`: 파일 모니터링
- `systemd`: systemd 저널 로그 수집

### FILTER 섹션

- `aws`: AWS 메타데이터 추가
- `modify`: 필드 추가/수정

### OUTPUT 섹션

- `cloudwatch_logs`: CloudWatch Logs로 전송
- `kinesis_streams`: Kinesis Data Streams로 전송
- `s3`: S3 버킷으로 아카이브

## 관리 명령어

설치 후 다음 관리 스크립트를 사용할 수 있습니다:

```bash
# 관리 스크립트 사용법
./manage-fluent-bit.sh {start|stop|restart|status|logs|config|validate|test|api|metrics|uptime|health}
```

### 주요 명령어

```bash
# 서비스 상태 확인
./manage-fluent-bit.sh status

# 로그 실시간 확인
./manage-fluent-bit.sh logs

# 설정 파일 검증
./manage-fluent-bit.sh validate

# 테스트 로그 생성
./manage-fluent-bit.sh test

# HTTP API 상태 확인
./manage-fluent-bit.sh api

# 헬스 체크
./manage-fluent-bit.sh health
```

## HTTP API

Fluent Bit은 HTTP API를 제공합니다 (포트 2020):

```bash
# 헬스 체크
curl http://localhost:2020/api/v1/health

# 메트릭 확인
curl http://localhost:2020/api/v1/metrics

# 업타임 확인
curl http://localhost:2020/api/v1/uptime

# 설정 정보
curl http://localhost:2020/
```

## 테스트

설치가 완료되면 테스트 로그를 생성하여 정상 작동을 확인할 수 있습니다:

```bash
# 테스트 로그 생성
echo '{"timestamp":"'$(date -Iseconds)'","level":"INFO","message":"Test game event from Fluent Bit","player_id":"test456","event_type":"logout","score":1500}' >> /var/log/game-logs/game.log

# Fluent Bit 로그 확인
sudo journalctl -u fluent-bit -f
```

## 문제 해결

### 일반적인 문제

1. **서비스 시작 실패**
   ```bash
   sudo journalctl -u fluent-bit -n 50
   ```

2. **설정 파일 오류**
   ```bash
   sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run
   ```

3. **권한 문제**
   ```bash
   sudo chown -R fluent-bit:fluent-bit /var/log/fluent-bit
   sudo chown -R fluent-bit:fluent-bit /var/lib/fluent-bit
   ```

4. **메모리 사용량 문제**
   ```bash
   # fluent-bit.conf에서 Mem_Buf_Limit 조정
   Mem_Buf_Limit     10MB
   ```

### 로그 파일 위치

- Fluent Bit 로그: `sudo journalctl -u fluent-bit`
- 설치 로그: `/var/log/fluent-bit-install.log`
- 게임 로그: `/var/log/game-logs/`
- Fluent Bit 데이터: `/var/lib/fluent-bit/`

## 성능 최적화

### 메모리 사용량 최적화

```ini
[INPUT]
    Name              tail
    Path              /var/log/game-logs/*.log
    Mem_Buf_Limit     10MB
    Skip_Long_Lines   On
    Buffer_Chunk_Size 32k
    Buffer_Max_Size   256k
```

### 배치 처리 최적화

```ini
[OUTPUT]
    Name                cloudwatch_logs
    Match               game.logs
    workers             2
```

## 모니터링

### 메트릭 수집

```bash
# Prometheus 메트릭 형식으로 확인
curl http://localhost:2020/api/v1/metrics/prometheus
```

### 로그 통계

```bash
# 입력/출력 통계 확인
curl http://localhost:2020/api/v1/metrics | jq '.input'
curl http://localhost:2020/api/v1/metrics | jq '.output'
```

## 다음 단계

Fluent Bit 설치가 완료되면:

1. 로그 파싱 규칙 세부 조정
2. 메트릭 및 알람 설정
3. 대시보드 구성
4. 성능 모니터링 설정
5. 로그 보존 정책 설정

자세한 내용은 [Fluent Bit 공식 문서](https://docs.fluentbit.io/)를 참조하세요.
