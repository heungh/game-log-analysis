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

## Vector 설치

### 바이너리 직접 설치 방법

시스템 패키지 업데이트
```bash
sudo apt update && sudo apt upgrade -y
```
필수 의존성 설치
```bash

sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates
```
Vector 바이너리 다운로드
```bash
#cd /tmp
wget https://github.com/vectordotdev/vector/releases/download/v0.34.1/vector-0.34.1-x86_64-unknown-linux-musl.tar.gz
```

압축 해제 및 설치 및 Vector 사용자 생성
```bash
tar -xzf vector-0.34.1-x86_64-unknown-linux-musl.tar.gz
sudo cp vector-x86_64-unknown-linux-musl/bin/vector /usr/local/bin/
sudo chmod +x /usr/local/bin/vector
sudo useradd --system --shell /bin/false --home-dir /var/lib/vector vector
```

## 디렉토리 및 권한 설정

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

# 권한 설정
sudo chmod -R 755 /var/lib/vector
sudo chmod -R 755 /var/log/vector
sudo chmod 755 /var/log/game
```

## Vector 설정

### 기본 설정 파일 생성

```bash
# Vector 기본 설정 파일 생성
sudo tee /etc/vector/vector.toml << 'EOF'
data_dir = "/var/lib/vector"

# 소스: 게임 로그 파일 모니터링
[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"

# 변환: 기본 메타데이터 추가
[transforms.add_metadata]
type = "remap"
inputs = ["game_logs"]
source = '''
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"
.original_message = .message
'''

# 싱크: 콘솔 출력
[sinks.console]
type = "console"
inputs = ["add_metadata"]
encoding.codec = "json"

# 싱크: 파일 출력
[sinks.file_output]
type = "file"
inputs = ["add_metadata"]
path = "/var/log/vector/processed_logs.log"
encoding.codec = "json"
EOF
```

### JSON 파싱이 포함된 고급 설정 (선택사항)

```bash
# JSON 파싱을 포함한 고급 설정 
sudo tee /etc/vector/vector-advanced.toml << 'EOF'
data_dir = "/var/lib/vector"

[sources.game_logs]
type = "file"
include = ["/var/log/game/*.log"]
read_from = "beginning"
ignore_older_secs = 86400

[transforms.parse_logs]
type = "remap"
inputs = ["game_logs"]
source = '''
# 기본 메타데이터 추가
.timestamp = now()
.hostname = get_hostname!()
.source = "vector-agent"

# JSON 파싱 시도 (안전한 방법)
if is_string(.message) {
  parsed_json, parse_err = parse_json(.message)
  if parse_err == null {
    .parsed_data = parsed_json
    .is_json = true
  } else {
    .is_json = false
    .parse_error = to_string(parse_err)
  }
} else {
  .is_json = false
}
'''

[sinks.console]
type = "console"
inputs = ["parse_logs"]
encoding.codec = "json"

[sinks.file_output]
type = "file"
inputs = ["parse_logs"]
path = "/var/log/vector/processed_logs.log"
encoding.codec = "json"
EOF
```

## systemd 서비스 설정

### 서비스 파일 생성

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
ExecStartPre=/usr/local/bin/vector validate --no-environment /etc/vector/vector.toml
ExecStart=/usr/local/bin/vector --config /etc/vector/vector.toml
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF
```

### 서비스 시작 및 활성화

```bash
# systemd 데몬 리로드
sudo systemctl daemon-reload

# 설정 검증
sudo /usr/local/bin/vector validate /etc/vector/vector.toml

# 서비스 활성화 및 시작
sudo systemctl enable vector
sudo systemctl start vector

# 서비스 상태 확인
sudo systemctl status vector
```

## 설치 확인 및 테스트

### Vector 설치 확인

```bash
# Vector 버전 확인
/usr/local/bin/vector --version

# 서비스 상태 확인
sudo systemctl is-active vector

# 프로세스 확인
ps aux | grep vector
```

### 테스트 로그 생성

```bash
# 기본 테스트 로그 생성
echo "Test message from game" | sudo tee /var/log/game/test.log

# JSON 형식 테스트 로그 생성
echo '{"user_id": "user123", "action": "login", "level": 25}' | sudo tee -a /var/log/game/test.log

# 추가 테스트 로그
echo "$(date -Iseconds) - Game server started" | sudo tee -a /var/log/game/test.log
```

### Vector 출력 확인

```bash
# Vector 서비스 로그 실시간 확인
sudo journalctl -u vector -f

# 처리된 로그 파일 확인
sudo tail -f /var/log/vector/processed_logs.log

# 콘솔 출력 확인 (별도 터미널에서)
sudo journalctl -u vector -n 20
```

### 성능 모니터링

```bash
# Vector 프로세스 리소스 사용량
top -p $(pgrep vector)

# 메모리 사용량 확인
ps aux | grep vector | grep -v grep

# 디스크 사용량 확인
du -sh /var/lib/vector /var/log/vector
```

### 일반적인 문제 해결

1. **서비스 시작 실패**
   ```bash
   # 자세한 로그 확인
   sudo journalctl -u vector -n 50
   
   # 설정 검증
   sudo /usr/local/bin/vector validate /etc/vector/vector.toml
   
   # 직접 실행으로 문제 확인
   sudo /usr/local/bin/vector --config /etc/vector/vector.toml
   ```

2. **권한 문제**
   ```bash
   # 권한 재설정
   sudo chown -R vector:vector /var/lib/vector
   sudo chown -R vector:vector /var/log/vector
   sudo chmod 755 /var/log/game
   ```

3. **로그 파일 접근 문제**
   ```bash
   # 로그 파일 권한 확인
   ls -la /var/log/game/
   
   # 필요시 권한 수정
   sudo chmod 644 /var/log/game/*.log
   ```

## 연속 테스트 로그 생성

### 자동 로그 생성 스크립트

```bash
# 연속 테스트 로그 생성 스크립트
cat > ~/continuous_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/continuous.log"
counter=1

echo "연속 테스트 로그 생성 시작..."

while true; do
    # 다양한 형태의 로그 생성
    case $((counter % 4)) in
        0)
            echo "$(date -Iseconds) - User login: user_$((RANDOM%100))" >> $LOG_FILE
            ;;
        1)
            echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_'$((RANDOM%100))'","action":"gameplay","level":'$((RANDOM%50))'}' >> $LOG_FILE
            ;;
        2)
            echo "$(date -Iseconds) - Server event: maintenance_check" >> $LOG_FILE
            ;;
        3)
            echo '{"timestamp":"'$(date -Iseconds)'","event":"purchase","item_id":"item_'$((RANDOM%20))'","price":'$((RANDOM%1000))'}' >> $LOG_FILE
            ;;
    esac
    
    echo "로그 항목 $counter 생성됨"
    counter=$((counter + 1))
    sleep 3
done
EOF

chmod +x ~/continuous_test_logs.sh
```

### 백그라운드 실행

```bash
# 백그라운드에서 연속 로그 생성
nohup ~/continuous_test_logs.sh > ~/log_generator.out 2>&1 &

# 프로세스 확인
ps aux | grep continuous_test_logs

# 로그 생성 중지 (필요시)
pkill -f continuous_test_logs.sh
```

## 서비스 관리 명령어

```bash
# 서비스 시작
sudo systemctl start vector

# 서비스 중지
sudo systemctl stop vector

# 서비스 재시작
sudo systemctl restart vector

# 서비스 상태 확인
sudo systemctl status vector

# 서비스 활성화 (부팅시 자동 시작)
sudo systemctl enable vector

# 서비스 비활성화
sudo systemctl disable vector

# 설정 리로드
sudo systemctl reload vector
```

## 다음 단계

Vector 설치 및 설정이 완료되면 다음과 같은 작업을 진행합니다. 

1. **Amazon Data Firehose 생성**
   - AWS 콘솔에서 Amazon Data Firehose 생성

2. **IAM 권한 설정**
   - EC2 인스턴스에 Kinesis 접근 권한 부여
   - 필요한 IAM 역할 및 정책 생성

3. **Vector 설정 업데이트**
   - Amazon Data Firehose 정보로 설정 파일 업데이트
   - 배치 및 재시도 설정 최적화

## 참고 자료

- [Vector 공식 문서](https://vector.dev/docs/)
- [Vector GitHub 저장소](https://github.com/vectordotdev/vector)
- [Vector 설정 예제](https://vector.dev/docs/reference/configuration/)
- [AWS Kinesis 통합 가이드](https://vector.dev/docs/reference/configuration/sinks/aws_kinesis_streams/)
- [VRL (Vector Remap Language) 문서](https://vrl.dev/)
- [Vector 성능 튜닝 가이드](https://vector.dev/docs/administration/tuning/)
