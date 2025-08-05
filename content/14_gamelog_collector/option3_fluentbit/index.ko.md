---
title: "Option 3: Fluent Bit 설치"
weight: 30
---

# Ubuntu 20.04에서 Fluent Bit 설치 가이드

Fluent Bit은 경량화된 고성능 로그 프로세서 및 포워더로, 다양한 소스에서 데이터를 수집하고 여러 대상으로 전송할 수 있는 CNCF 프로젝트입니다. 낮은 메모리 사용량과 높은 처리량을 제공합니다.

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

# 메모리 확인
free -h
```

## 설치 과정

### 1단계: 시스템 업데이트 및 필수 패키지 설치

```bash
# 시스템 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 의존성 설치
sudo apt install -y curl wget gnupg2 software-properties-common apt-transport-https ca-certificates lsb-release
```

### 2단계: Fluent Bit 공식 리포지토리 추가

```bash
# Fluent Bit GPG 키 추가
wget -qO - https://packages.fluentbit.io/fluentbit.key | sudo apt-key add -

# Ubuntu 20.04 (focal)용 리포지토리 추가
echo "deb https://packages.fluentbit.io/ubuntu/focal focal main" | sudo tee /etc/apt/sources.list.d/fluent-bit.list

# 패키지 목록 업데이트
sudo apt update
```

### 3단계: Fluent Bit 설치

```bash
# Fluent Bit 설치
sudo apt install -y fluent-bit

# 설치 경로 확인
ls -la /opt/fluent-bit/bin/fluent-bit

# 버전 확인
/opt/fluent-bit/bin/fluent-bit --version
```

### 4단계: 실행 경로 설정

```bash
# 심볼릭 링크 생성 (편의를 위해)
sudo ln -sf /opt/fluent-bit/bin/fluent-bit /usr/local/bin/fluent-bit

# PATH 새로고침
hash -r
```

### 5단계: 디렉토리 및 권한 설정

```bash
# 필요한 디렉토리 생성
sudo mkdir -p /var/log/game
sudo mkdir -p /var/log/fluent-bit

# 권한 설정
sudo chown ubuntu:ubuntu /var/log/game
sudo chmod 755 /var/log/game
sudo chmod 755 /var/log/fluent-bit

# 디렉토리 확인
ls -la /var/log/ | grep -E "(game|fluent)"
```

## 설정

### 기본 설정 파일 생성

메모리 최적화가 포함된 설정 파일을 생성합니다:

```bash
# 기존 설정 파일 백업 (있다면)
sudo cp /etc/fluent-bit/fluent-bit.conf /etc/fluent-bit/fluent-bit.conf.backup 2>/dev/null || echo "기존 설정 파일 없음"

# 새로운 설정 파일 생성
sudo tee /etc/fluent-bit/fluent-bit.conf << 'EOF'
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off
    Parsers_File  parsers.conf
    HTTP_Server   On
    HTTP_Listen   0.0.0.0
    HTTP_Port     2020
    storage.path  /var/log/fluent-bit/
    storage.sync  normal
    storage.checksum off
    storage.backlog.mem_limit 5M

[INPUT]
    Name              tail
    Path              /var/log/game/*.log
    Tag               game.logs
    Refresh_Interval  5
    Read_from_Head    true
    Buffer_Chunk_Size 32k
    Buffer_Max_Size   256k
    Mem_Buf_Limit     1M

[OUTPUT]
    Name  stdout
    Match *
EOF
```

### 설정 옵션 설명

**SERVICE 섹션:**
- `Flush`: 출력 플러시 간격 (초)
- `Log_Level`: 로그 레벨 (error, warn, info, debug, trace)
- `HTTP_Server`: HTTP API 서버 활성화
- `HTTP_Port`: HTTP API 포트
- `storage.backlog.mem_limit`: 메모리 백로그 제한

**INPUT 섹션:**
- `Name`: 입력 플러그인 이름 (tail)
- `Path`: 모니터링할 로그 파일 경로
- `Tag`: 로그에 할당할 태그
- `Read_from_Head`: 파일 처음부터 읽기
- `Mem_Buf_Limit`: 메모리 버퍼 제한

**OUTPUT 섹션:**
- `Name`: 출력 플러그인 이름 (stdout)
- `Match`: 매칭할 태그 패턴

## 서비스 관리

### 서비스 시작 및 활성화

```bash
# 설정 파일 검증
sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run

# 서비스 시작
sudo systemctl start fluent-bit

# 서비스 상태 확인
sudo systemctl status fluent-bit

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable fluent-bit
```

### 설치 확인

```bash
# 서비스 활성 상태 확인
sudo systemctl is-active fluent-bit

# 프로세스 확인
ps aux | grep fluent-bit

# HTTP API 확인
curl http://localhost:2020/

# 메트릭 확인
curl http://localhost:2020/api/v1/metrics
```

## 테스트

### 테스트 로그 생성

```bash
# 간단한 테스트 로그 생성
echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_001","action":"login","level":1}' >> /var/log/game/test.log
echo '{"timestamp":"'$(date -Iseconds)'","user_id":"user_002","action":"logout","level":5}' >> /var/log/game/test.log

# 생성된 로그 확인
cat /var/log/game/test.log
```

### 연속 테스트 로그 생성

```bash
# 테스트 로그 생성 스크립트 생성
cat > ~/generate_test_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/game/game.log"
counter=1

echo "Fluent Bit 테스트 로그 생성 시작..."

while true; do
    timestamp=$(date -Iseconds)
    user_id="user_$((RANDOM%100))"
    actions=("login" "logout" "level_up" "purchase" "battle")
    action=${actions[$RANDOM % ${#actions[@]}]}
    level=$((RANDOM%100))
    
    echo "{\"timestamp\":\"$timestamp\",\"user_id\":\"$user_id\",\"action\":\"$action\",\"level\":$level,\"counter\":$counter}" >> $LOG_FILE
    echo "로그 항목 $counter 생성됨: $action by $user_id"
    
    counter=$((counter + 1))
    sleep 2
done
EOF

chmod +x ~/generate_test_logs.sh

# 백그라운드에서 실행
nohup ~/generate_test_logs.sh > ~/test_log_generator.out 2>&1 &
```

## 모니터링

### 실시간 로그 모니터링

```bash
# 게임 로그 실시간 모니터링
tail -f /var/log/game/game.log

# Fluent Bit 서비스 로그 모니터링
sudo journalctl -u fluent-bit -f

# 최근 로그 확인
sudo journalctl -u fluent-bit -n 20
```

### 성능 모니터링

```bash
# 리소스 사용량 확인
top -p $(pgrep fluent-bit)

# 메모리 사용량 확인
ps aux | grep fluent-bit | grep -v grep

# 네트워크 연결 확인
sudo ss -tulpn | grep 2020
```

### HTTP API를 통한 모니터링

```bash
# 기본 정보 확인
curl http://localhost:2020/

# 메트릭 확인
curl http://localhost:2020/api/v1/metrics

# 설정 정보 확인
curl http://localhost:2020/api/v1/config

# 헬스 체크
curl http://localhost:2020/api/v1/health
```

### CloudWatch Logs 연동

```bash
# CloudWatch Logs용 설정 파일 생성
sudo tee /etc/fluent-bit/cloudwatch.conf << 'EOF'
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off

[INPUT]
    Name              tail
    Path              /var/log/game/*.log
    Tag               game.logs
    Read_from_Head    true

[OUTPUT]
    Name cloudwatch_logs
    Match *
    region ap-northeast-2
    log_group_name /aws/ec2/game-logs
    log_stream_name ${hostname}
    auto_create_group true
EOF
```

## 문제 해결

### 일반적인 문제

1. **서비스 시작 실패**
   ```bash
   sudo journalctl -u fluent-bit -n 50
   sudo systemctl restart fluent-bit
   ```

2. **설정 파일 오류**
   ```bash
   sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run
   ```

3. **권한 문제**
   ```bash
   sudo chown -R fluent-bit:fluent-bit /var/log/fluent-bit
   sudo chmod 644 /var/log/game/*.log
   ```

4. **메모리 부족**
   ```bash
   # 설정 파일에서 메모리 제한 조정
   Mem_Buf_Limit     512k
   storage.backlog.mem_limit 2M
   ```

### 로그 파일 위치

- Fluent Bit 서비스 로그: `sudo journalctl -u fluent-bit`
- 설정 파일: `/etc/fluent-bit/fluent-bit.conf`
- 게임 로그: `/var/log/game/`
- Fluent Bit 데이터: `/var/log/fluent-bit/`

## 관리 명령어

```bash
# 서비스 시작
sudo systemctl start fluent-bit

# 서비스 중지
sudo systemctl stop fluent-bit

# 서비스 재시작
sudo systemctl restart fluent-bit

# 상태 확인
sudo systemctl status fluent-bit

# 로그 확인
sudo journalctl -u fluent-bit -f

# 설정 검증
sudo /opt/fluent-bit/bin/fluent-bit -c /etc/fluent-bit/fluent-bit.conf --dry-run

# 테스트 로그 생성기 중지
pkill -f generate_test_logs.sh
```



## 다음 단계

Fluent Bit 설치 및 설정이 완료되면 다음과 같은 작업을 진행합니다.

1. **Amazon Data Firehose 생성**
   - AWS 콘솔에서 Amazon Data Firehose 생성

2. **IAM 권한 설정**
   - EC2 인스턴스에 Kinesis 접근 권한 부여
   - 필요한 IAM 역할 및 정책 생성

3. **Fluent Bit 설정 업데이트**
   - Amazon Data Firehose 정보로 설정 파일 업데이트
   - 배치 및 재시도 설정 최적화

자세한 정보는 [Fluent Bit 공식 문서](https://docs.fluentbit.io/)를 참조하세요.

## 참고 자료

- [Fluent Bit GitHub 저장소](https://github.com/fluent/fluent-bit)
- [Fluent Bit 설정 가이드](https://docs.fluentbit.io/manual/administration/configuring-fluent-bit)
- [AWS 출력 플러그인](https://docs.fluentbit.io/manual/pipeline/outputs/kinesis)
- [성능 튜닝 가이드](https://docs.fluentbit.io/manual/administration/memory-management)
