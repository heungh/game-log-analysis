# 로그 수집 도구 설치 스크립트

이 디렉토리에는 게임 로그 분석을 위한 다양한 로그 수집 도구들의 설치 스크립트가 포함되어 있습니다.

## 📦 포함된 도구들

### 1. Kinesis Agent
- **파일**: `install-kinesis-agent.sh`
- **설명**: AWS Kinesis Data Streams로 로그를 전송하는 에이전트
- **포트**: 없음 (파일 기반 모니터링)
- **관리 스크립트**: `manage-kinesis-agent.sh`

### 2. Vector
- **파일**: `install-vector.sh`
- **설명**: 고성능 로그 수집 및 처리 도구
- **포트**: 8686 (API)
- **관리 스크립트**: `manage-vector.sh`

### 3. Fluent Bit
- **파일**: `install-fluent-bit.sh`
- **설명**: 경량 로그 프로세서 및 포워더
- **포트**: 2020 (HTTP API)
- **관리 스크립트**: `manage-fluent-bit.sh`

## 🚀 사용법

### 개별 설치

각 도구를 개별적으로 설치할 수 있습니다:

```bash
# Kinesis Agent 설치
sudo bash install-kinesis-agent.sh

# Vector 설치
sudo bash install-vector.sh

# Fluent Bit 설치
sudo bash install-fluent-bit.sh
```

### 통합 설치 (Python)

모든 도구를 한 번에 설치할 수 있습니다:

```bash
# 모든 도구 설치
sudo python3 install-all-tools.py

# 특정 도구만 설치
sudo python3 install-all-tools.py kinesis-agent vector
sudo python3 install-all-tools.py fluent-bit
```

## 🔧 관리

### 개별 도구 관리

각 도구는 전용 관리 스크립트를 제공합니다:

```bash
# Kinesis Agent 관리
./manage-kinesis-agent.sh {start|stop|restart|status|logs|config|test}

# Vector 관리
./manage-vector.sh {start|stop|restart|status|logs|config|validate|test|api|metrics}

# Fluent Bit 관리
./manage-fluent-bit.sh {start|stop|restart|status|logs|config|validate|test|api|metrics|uptime|health}
```

### 통합 관리

통합 설치 후에는 모든 도구를 한 번에 관리할 수 있습니다:

```bash
# 통합 관리 스크립트 (통합 설치 후 생성됨)
./manage-log-collectors.sh {status|start|stop|restart|logs|test|report}
```

## 📋 주요 기능

### 공통 기능
- ✅ 자동 서비스 등록 및 시작
- ✅ 설정 파일 자동 생성
- ✅ 로그 디렉토리 자동 생성
- ✅ 권한 설정 자동화
- ✅ 상태 확인 및 모니터링
- ✅ 테스트 로그 생성

### Kinesis Agent 특징
- AWS Kinesis Data Streams 연동
- 파일 기반 로그 모니터링
- 자동 재시도 및 체크포인트
- CloudWatch 메트릭 전송

### Vector 특징
- 고성능 로그 처리
- 다양한 입력/출력 소스 지원
- 실시간 로그 변환 및 필터링
- REST API 제공 (포트 8686)
- 메트릭 및 헬스 체크

### Fluent Bit 특징
- 경량 메모리 사용량
- 다양한 플러그인 지원
- HTTP API 제공 (포트 2020)
- 실시간 메트릭 및 헬스 체크
- AWS 서비스 네이티브 지원

## 📁 디렉토리 구조

설치 후 생성되는 주요 디렉토리:

```
/var/log/game-logs/          # 게임 로그 파일 저장소
/etc/aws-kinesis/            # Kinesis Agent 설정
/etc/vector/                 # Vector 설정
/etc/fluent-bit/             # Fluent Bit 설정
/var/lib/vector/             # Vector 데이터 디렉토리
/var/lib/fluent-bit/         # Fluent Bit 데이터 디렉토리
```

## 🔍 로그 파일 위치

```
/var/log/kinesis-agent-install.log      # Kinesis Agent 설치 로그
/var/log/vector-install.log             # Vector 설치 로그
/var/log/fluent-bit-install.log         # Fluent Bit 설치 로그
/var/log/log-collector-install.log      # 통합 설치 로그

/var/log/aws-kinesis-agent/             # Kinesis Agent 런타임 로그
/var/log/vector/                        # Vector 런타임 로그
/var/log/fluent-bit/                    # Fluent Bit 런타임 로그
```

## 🧪 테스트

각 도구의 테스트 기능을 사용하여 정상 동작을 확인할 수 있습니다:

```bash
# 개별 테스트
./manage-kinesis-agent.sh test
./manage-vector.sh test
./manage-fluent-bit.sh test

# 통합 테스트
./manage-log-collectors.sh test
```

## 🔧 설정 파일 편집

```bash
# Kinesis Agent 설정
sudo nano /etc/aws-kinesis/agent.json

# Vector 설정
sudo nano /etc/vector/vector.toml

# Fluent Bit 설정
sudo nano /etc/fluent-bit/fluent-bit.conf
```

## 📊 모니터링

### API 엔드포인트

- **Vector API**: http://localhost:8686
  - 헬스 체크: `/health`
  - 메트릭: `/metrics`

- **Fluent Bit HTTP**: http://localhost:2020
  - 헬스 체크: `/api/v1/health`
  - 메트릭: `/api/v1/metrics`
  - 업타임: `/api/v1/uptime`

### 서비스 상태 확인

```bash
# 서비스 상태
sudo systemctl status aws-kinesis-agent
sudo systemctl status vector
sudo systemctl status fluent-bit

# 로그 확인
sudo journalctl -u aws-kinesis-agent -f
sudo journalctl -u vector -f
sudo journalctl -u fluent-bit -f
```

## ⚠️ 주의사항

1. **루트 권한 필요**: 모든 설치 스크립트는 `sudo` 권한이 필요합니다.
2. **포트 충돌**: Vector(8686)와 Fluent Bit(2020) 포트가 사용 중이지 않은지 확인하세요.
3. **AWS 권한**: AWS 서비스 연동을 위해 적절한 IAM 권한이 필요합니다.
4. **메모리 사용량**: 모든 도구를 동시에 실행할 때 메모리 사용량을 모니터링하세요.

## 🆘 문제 해결

### 설치 실패 시
1. 로그 파일 확인: `/var/log/*-install.log`
2. 서비스 로그 확인: `sudo journalctl -u <service-name> -n 50`
3. 포트 사용 확인: `sudo netstat -tlnp | grep <port>`
4. 권한 확인: 파일 및 디렉토리 권한 확인

### 성능 이슈
1. 메모리 사용량 확인: `htop` 또는 `free -h`
2. CPU 사용량 확인: `top`
3. 디스크 사용량 확인: `df -h`
4. 로그 파일 크기 확인: `du -sh /var/log/*`

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 설치 로그 파일
2. 서비스 상태 및 로그
3. 시스템 리소스 사용량
4. 네트워크 연결 상태
