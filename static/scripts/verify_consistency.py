#!/usr/bin/env python3
"""
게임 로그 데이터 일관성 검증 스크립트
"""

import json
from datetime import datetime

def load_json_data(filename):
    """JSON 파일 로드"""
    with open(f"data/{filename}", 'r', encoding='utf-8') as f:
        return json.load(f)

def verify_consistency():
    """데이터 일관성 검증"""
    print("🔍 게임 로그 데이터 일관성 검증을 시작합니다...\n")
    
    # 데이터 로드
    sessions = load_json_data("session_logs.json")
    actions = load_json_data("ingame_action_logs.json")
    items = load_json_data("item_logs.json")
    payments = load_json_data("payment_logs.json")
    errors = load_json_data("error_logs.json")
    
    # 세션 정보를 딕셔너리로 변환
    session_dict = {}
    for session in sessions:
        session_dict[session["session_id"]] = {
            "user_id": session["user_id"],
            "login_time": datetime.fromisoformat(session["login_time"]),
            "logout_time": datetime.fromisoformat(session["logout_time"])
        }
    
    print(f"📊 로드된 데이터:")
    print(f"  - 세션 로그: {len(sessions):,}건")
    print(f"  - 인게임 액션 로그: {len(actions):,}건")
    print(f"  - 아이템 로그: {len(items):,}건")
    print(f"  - 결제 로그: {len(payments):,}건")
    print(f"  - 에러 로그: {len(errors):,}건\n")
    
    # 일관성 검증
    def check_log_consistency(logs, log_type):
        valid_count = 0
        invalid_count = 0
        
        for log in logs[:100]:  # 샘플 100개만 검증
            if "session_id" in log:
                session_id = log["session_id"]
                if session_id in session_dict:
                    session_info = session_dict[session_id]
                    log_time = datetime.fromisoformat(log["timestamp"])
                    
                    # 사용자 ID 일치 확인
                    if log["user_id"] == session_info["user_id"]:
                        # 시간 범위 확인
                        if session_info["login_time"] <= log_time <= session_info["logout_time"]:
                            valid_count += 1
                        else:
                            invalid_count += 1
                            print(f"  ❌ 시간 범위 오류: {log_type} - {log['log_id']}")
                    else:
                        invalid_count += 1
                        print(f"  ❌ 사용자 ID 불일치: {log_type} - {log['log_id']}")
                else:
                    invalid_count += 1
                    print(f"  ❌ 세션 ID 없음: {log_type} - {log['log_id']}")
            else:
                # 결제 로그는 session_id가 없으므로 user_id와 시간만 확인
                user_id = log["user_id"]
                log_time = datetime.fromisoformat(log["timestamp"])
                
                # 해당 사용자의 세션 중에서 시간 범위에 맞는 세션이 있는지 확인
                found_valid_session = False
                for session_id, session_info in session_dict.items():
                    if (session_info["user_id"] == user_id and 
                        session_info["login_time"] <= log_time <= session_info["logout_time"]):
                        found_valid_session = True
                        break
                
                if found_valid_session:
                    valid_count += 1
                else:
                    invalid_count += 1
                    print(f"  ❌ 유효한 세션 없음: {log_type} - {log['log_id']}")
        
        return valid_count, invalid_count
    
    # 각 로그 타입별 일관성 검증
    print("✅ 일관성 검증 결과:")
    
    valid, invalid = check_log_consistency(actions, "인게임 액션")
    print(f"  - 인게임 액션 로그: 유효 {valid}건, 무효 {invalid}건")
    
    valid, invalid = check_log_consistency(items, "아이템")
    print(f"  - 아이템 로그: 유효 {valid}건, 무효 {invalid}건")
    
    valid, invalid = check_log_consistency(payments, "결제")
    print(f"  - 결제 로그: 유효 {valid}건, 무효 {invalid}건")
    
    valid, invalid = check_log_consistency(errors, "에러")
    print(f"  - 에러 로그: 유효 {valid}건, 무효 {invalid}건")
    
    print("\n🎉 일관성 검증이 완료되었습니다!")

if __name__ == "__main__":
    verify_consistency()
