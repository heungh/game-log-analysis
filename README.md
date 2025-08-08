# Game Log Analytics Workshop

AWS를 활용한 게임 로그 분석 워크샵입니다. 실시간 게임 로그 수집, 처리, 분석을 위한 완전한 데이터 파이프라인을 구축하는 방법을 학습합니다.

## 📋 프로젝트 개요

이 워크샵은 게임 개발자와 데이터 엔지니어를 위한 실습 중심의 교육 자료로, AWS 서비스를 활용하여 게임 로그 데이터를 효과적으로 수집, 저장, 분석하는 방법을 다룹니다.

## 🏗️ 아키텍처

- **로그 수집**: Kinesis Agent, Vector, Fluent Bit
- **데이터 스트리밍**: Amazon Kinesis Data Streams
- **데이터 저장**: Amazon S3
- **로그 모니터링**: Amazon CloudWatch Logs
- **인프라 관리**: AWS CloudFormation

## 📁 프로젝트 구조

```
.
├── README.md                           # 프로젝트 설명서
├── contentspec.yaml                    # 워크샵 설정 파일
├── content/                            # 워크샵 콘텐츠 (다국어 지원)
│   ├── index.ko.md                     # 메인 페이지 (한국어)
│   ├── index.en.md                     # 메인 페이지 (영어)
│   ├── 10_introduction/                # 소개 섹션
│   ├── 14_gamelog_collector/           # 로그 수집기 섹션
│   ├── configuration/                  # 설정 가이드
│   └── summary/                        # 요약
├── static/                             # 정적 자산
│   ├── cfn/                           # CloudFormation 템플릿
│   ├── images/                        # 워크샵 이미지
│   └── scripts/                       # 설치 및 관리 스크립트
├── data/                              # 샘플 게임 로그 데이터
│   ├── session_logs.json/csv          # 세션 로그 (10,000건)
│   ├── ingame_action_logs.json/csv    # 인게임 액션 로그 (10,000건)
│   ├── item_logs.json/csv             # 아이템 로그 (10,000건)
│   ├── payment_logs.json/csv          # 결제 로그 (10,000건)
│   └── error_logs.json/csv            # 에러 로그 (10,000건)
├── *.py                               # 데이터 분석 스크립트
├── deploy-stack.sh                    # 스택 배포 스크립트
└── find-resources.sh                  # 리소스 검색 스크립트
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# CloudFormation 스택 배포
./deploy-stack.sh

# 리소스 확인
./find-resources.sh
```

### 2. 로그 수집기 설치

```bash
# 모든 도구 설치
cd static/scripts
python3 install-all-tools.py

# 개별 설치
./install-kinesis-agent.sh    # Kinesis Agent
./install-vector.sh           # Vector
./install-fluent-bit.sh       # Fluent Bit
```

### 3. 샘플 데이터 생성

```bash
# 게임 로그 생성
python3 static/scripts/generate_game_logs.py

# 데이터 검증
python3 static/scripts/validate_data.py
```

## 📊 포함된 로그 타입

| 로그 타입 | 설명 | 샘플 수 | 형식 |
|-----------|------|---------|------|
| Session Logs | 사용자 세션 정보 | 10,000 | JSON/CSV |
| Ingame Action Logs | 게임 내 액션 | 10,000 | JSON/CSV |
| Item Logs | 아이템 사용/획득 | 10,000 | JSON/CSV |
| Payment Logs | 결제 정보 | 10,000 | JSON/CSV |
| Error Logs | 에러 및 예외 | 10,000 | JSON/CSV |

## 🛠️ 지원 도구

### 로그 수집기
- **Kinesis Agent**: AWS 네이티브 로그 수집
- **Vector**: 고성능 로그 처리
- **Fluent Bit**: 경량 로그 포워더

### 분석 스크립트
- `analyze_user_patterns.py`: 사용자 패턴 분석
- `show_data_samples.py`: 데이터 샘플 표시
- `show_consistency_example.py`: 데이터 일관성 검증
- `verify_consistency.py`: 데이터 무결성 확인

## 🌐 다국어 지원

- 한국어 (ko-KR) - 기본 언어
- 영어 (en-US)

## 📚 워크샵 섹션

1. **Introduction**: AWS 게임 분석 개요
2. **Environment Setup**: 개발 환경 구성
3. **Log Collector**: 로그 수집기 설정
4. **Data Pipeline**: 데이터 파이프라인 구축
5. **Analysis**: 로그 데이터 분석

## 🔧 요구사항

- AWS 계정
- AWS CLI 설정
- Python 3.7+
- Bash 셸 환경

## 📖 사용법

1. 워크샵 환경을 배포합니다
2. 선택한 로그 수집기를 설치합니다
3. 샘플 데이터를 생성하고 검증합니다
4. 데이터 파이프라인을 구성합니다
5. 로그 데이터를 분석합니다

## 🤝 기여

이 프로젝트는 AWS 솔루션 아키텍처 교육을 위한 오픈 소스 워크샵입니다. 개선사항이나 버그 리포트는 언제든 환영합니다.

## 📄 라이선스

이 프로젝트는 AWS 워크샵 템플릿을 기반으로 합니다.
