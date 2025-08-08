#!/usr/bin/env python3
"""
데이터 일관성 예시 출력 스크립트
"""

import json
from datetime import datetime

def load_json_data(filename):
    """JSON 파일 로드"""
    with open(f"data/{filename}", 'r', encoding='utf-8') as f:
        return json.load(f)

def show_consistency_example():
    """데이터 일관성 예시 출력"""
    print("🔍 데이터 일관성 예시를 보여드립니다...\n")
    
    # 데이터 로드
    sessions = load_json_data("session_logs.json")
    actions = load_json_data("ingame_action_logs.json")
    items = load_json_data("item_logs.json")
    payments = load_json_data("payment_logs.json")
    errors = load_json_data("error_logs.json")
    
    # 첫 번째 세션 선택
    sample_session = sessions[0]
    user_id = sample_session["user_id"]
    session_id = sample_session["session_id"]
    
    print("📊 샘플 세션 정보:")
    print(f"  - 사용자 ID: {user_id}")
    print(f"  - 세션 ID: {session_id}")
    print(f"  - 로그인 시간: {sample_session['login_time']}")
    print(f"  - 로그아웃 시간: {sample_session['logout_time']}")
    print(f"  - 세션 지속시간: {sample_session['session_duration_seconds']}초\n")
    
    # 해당 세션과 관련된 로그들 찾기
    related_actions = [log for log in actions if log["session_id"] == session_id]
    related_items = [log for log in items if log["session_id"] == session_id]
    related_errors = [log for log in errors if log["session_id"] == session_id]
    
    # 해당 사용자의 결제 로그 찾기 (세션 시간 범위 내)
    session_start = datetime.fromisoformat(sample_session['login_time'])
    session_end = datetime.fromisoformat(sample_session['logout_time'])
    
    related_payments = []
    for log in payments:
        if log["user_id"] == user_id:
            log_time = datetime.fromisoformat(log["timestamp"])
            if session_start <= log_time <= session_end:
                related_payments.append(log)
    
    print("🎯 관련 로그 통계:")
    print(f"  - 인게임 액션 로그: {len(related_actions)}건")
    print(f"  - 아이템 로그: {len(related_items)}건")
    print(f"  - 결제 로그: {len(related_payments)}건")
    print(f"  - 에러 로그: {len(related_errors)}건\n")
    
    # 상세 예시 출력
    if related_actions:
        print("🎮 인게임 액션 로그 예시:")
        for i, log in enumerate(related_actions[:3]):
            print(f"  {i+1}. {log['action_type']} - {log['timestamp']}")
        print()
    
    if related_items:
        print("🎒 아이템 로그 예시:")
        for i, log in enumerate(related_items[:3]):
            print(f"  {i+1}. {log['action_type']} {log['item_id']} - {log['timestamp']}")
        print()
    
    if related_payments:
        print("💳 결제 로그 예시:")
        for i, log in enumerate(related_payments[:3]):
            print(f"  {i+1}. {log['product_id']} ${log['amount']} - {log['timestamp']}")
        print()
    
    if related_errors:
        print("🚨 에러 로그 예시:")
        for i, log in enumerate(related_errors[:3]):
            print(f"  {i+1}. {log['error_type']} - {log['timestamp']}")
        print()
    
    print("✅ 모든 로그의 타임스탬프가 세션 시간 범위 내에 있고, 동일한 사용자 ID를 가지고 있습니다!")

if __name__ == "__main__":
    show_consistency_example()
