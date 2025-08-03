# 게임 로그 데이터 샘플

이 디렉토리에는 게임 분석을 위한 5가지 타입의 로그 데이터가 포함되어 있습니다. 각 타입별로 10,000건의 샘플 데이터가 JSON과 CSV 형태로 제공됩니다.

## 📁 파일 구조

```
data/
├── session_logs.json          # 세션 로그 (JSON)
├── session_logs.csv           # 세션 로그 (CSV)
├── ingame_action_logs.json    # 인게임 액션 로그 (JSON)
├── ingame_action_logs.csv     # 인게임 액션 로그 (CSV)
├── item_logs.json             # 아이템 로그 (JSON)
├── item_logs.csv              # 아이템 로그 (CSV)
├── payment_logs.json          # 결제 로그 (JSON)
├── payment_logs.csv           # 결제 로그 (CSV)
├── error_logs.json            # 에러 로그 (JSON)
└── error_logs.csv             # 에러 로그 (CSV)
```

## 📊 데이터 타입별 설명

### 1. 세션 로그 (Session Logs)
사용자의 게임 접속 및 종료 정보를 기록합니다.

**주요 필드:**
- `user_id`: 사용자 고유 식별자
- `session_id`: 세션 고유 식별자
- `login_time`: 로그인 시간
- `logout_time`: 로그아웃 시간
- `session_duration_seconds`: 세션 지속 시간 (초)
- `device`: 사용 기기 (iPhone, Android, iPad, PC)
- `os_version`: 운영체제 버전
- `app_version`: 앱 버전
- `ip_address`: IP 주소
- `country`: 국가 코드

### 2. 인게임 액션 로그 (In-game Action Logs)
게임 내에서 발생하는 모든 사용자 행동을 기록합니다.

**주요 필드:**
- `user_id`: 사용자 고유 식별자
- `action_type`: 액션 타입 (level_start, quest_complete, battle_end 등)
- `details`: 액션별 상세 정보 (JSON 형태)
- `region`: 게임 내 지역
- `level`: 사용자 레벨
- `timestamp`: 액션 발생 시간

**액션 타입:**
- `level_start`, `level_complete`, `level_fail`: 레벨 진행
- `quest_accept`, `quest_progress`, `quest_complete`: 퀘스트 활동
- `battle_start`, `battle_end`: 전투 활동
- `skill_use`: 스킬 사용
- `friend_add`, `guild_join`, `chat_send`: 사회적 활동
- `region_move`: 지역 이동

### 3. 아이템 로그 (Item Logs)
아이템 획득, 사용, 거래 등의 정보를 기록합니다.

**주요 필드:**
- `user_id`: 사용자 고유 식별자
- `item_id`: 아이템 고유 식별자
- `action_type`: 액션 타입 (acquire, use, sell, buy, trade, enhance, synthesize)
- `quantity`: 수량
- `item_details`: 아이템 상세 정보 (JSON 형태)
- `timestamp`: 액션 발생 시간

### 4. 결제 로그 (Payment Logs)
인앱 구매 및 결제 정보를 기록합니다.

**주요 필드:**
- `user_id`: 사용자 고유 식별자
- `transaction_id`: 거래 고유 식별자
- `product_id`: 상품 식별자
- `amount`: 결제 금액
- `currency`: 통화 (USD, KRW, EUR, JPY)
- `payment_method`: 결제 수단
- `status`: 결제 상태 (completed, pending, failed, refunded)
- `country`: 결제 국가
- `promotion_code`: 프로모션 코드 (선택적)

### 5. 에러 로그 (Error Logs)
게임 실행 중 발생하는 오류 및 성능 이슈를 기록합니다.

**주요 필드:**
- `user_id`: 사용자 고유 식별자
- `error_type`: 에러 타입
- `severity`: 심각도 (low, medium, high, critical)
- `error_message`: 에러 메시지
- `stack_trace`: 스택 트레이스 (선택적)
- `device`: 사용 기기
- `performance_metrics`: 성능 메트릭 (JSON 형태)

**에러 타입:**
- `client_crash`: 클라이언트 충돌
- `rendering_error`: 렌더링 오류
- `server_connection_failed`: 서버 연결 실패
- `timeout`: 타임아웃
- `gameplay_logic_error`: 게임플레이 로직 오류
- `frame_drop`: 프레임 드롭
- `loading_delay`: 로딩 지연

## 🔧 데이터 생성 및 검증

### 데이터 생성
```bash
python generate_game_logs.py
```

### 데이터 검증
```bash
python validate_data.py
```

## 📈 데이터 통계

- **총 레코드 수**: 50,000건 (각 타입별 10,000건)
- **고유 사용자 수**: 1,000명
- **데이터 기간**: 최근 30일
- **파일 형식**: JSON, CSV
- **총 파일 크기**: 약 40MB

## 🎯 활용 예시

### 1. 사용자 세션 분석
```python
import pandas as pd

# 세션 데이터 로드
sessions = pd.read_csv('session_logs.csv')

# 평균 세션 시간 계산
avg_session_time = sessions['session_duration_seconds'].mean()
print(f"평균 세션 시간: {avg_session_time/60:.1f}분")
```

### 2. 에러 발생 패턴 분석
```python
import json

# 에러 로그 로드
with open('error_logs.json', 'r') as f:
    errors = json.load(f)

# 디바이스별 에러 분포
device_errors = {}
for error in errors:
    device = error['device']
    device_errors[device] = device_errors.get(device, 0) + 1

print("디바이스별 에러 발생 수:", device_errors)
```

### 3. 결제 성공률 분석
```python
payments = pd.read_csv('payment_logs.csv')

# 결제 상태별 분포
status_counts = payments['status'].value_counts()
success_rate = status_counts['completed'] / len(payments) * 100

print(f"결제 성공률: {success_rate:.1f}%")
```

## 📝 주의사항

1. 이 데이터는 분석 및 테스트 목적으로 생성된 가상 데이터입니다.
2. 실제 게임 환경에서는 데이터 구조나 필드가 다를 수 있습니다.
3. CSV 파일에서 JSON 형태의 중첩 데이터는 문자열로 저장되어 있습니다.
4. 시간 데이터는 ISO 8601 형식으로 저장되어 있습니다.

## 🔗 관련 파일

- `generate_game_logs.py`: 데이터 생성 스크립트
- `validate_data.py`: 데이터 검증 스크립트
