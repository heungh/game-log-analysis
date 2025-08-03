#!/usr/bin/env python3
"""
생성된 게임 로그 데이터 검증 스크립트
"""

import json
import csv
import os
from collections import Counter

def validate_json_files():
    """JSON 파일들의 레코드 수와 구조 검증"""
    json_files = [
        "session_logs.json",
        "ingame_action_logs.json", 
        "item_logs.json",
        "payment_logs.json",
        "error_logs.json"
    ]
    
    print("📊 JSON 파일 검증 결과:")
    print("-" * 50)
    
    for filename in json_files:
        filepath = os.path.join("data", filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ {filename}: {len(data):,}건")
                
                # 첫 번째 레코드의 키 구조 출력
                if data:
                    keys = list(data[0].keys())
                    print(f"   📋 필드: {', '.join(keys[:5])}{'...' if len(keys) > 5 else ''}")
        else:
            print(f"❌ {filename}: 파일이 존재하지 않습니다")
    print()

def validate_csv_files():
    """CSV 파일들의 레코드 수 검증"""
    csv_files = [
        "session_logs.csv",
        "ingame_action_logs.csv",
        "item_logs.csv", 
        "payment_logs.csv",
        "error_logs.csv"
    ]
    
    print("📈 CSV 파일 검증 결과:")
    print("-" * 50)
    
    for filename in csv_files:
        filepath = os.path.join("data", filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)  # 헤더 스킵
                row_count = sum(1 for row in reader)
                print(f"✅ {filename}: {row_count:,}건")
                print(f"   📋 컬럼 수: {len(header)}개")
        else:
            print(f"❌ {filename}: 파일이 존재하지 않습니다")
    print()

def analyze_sample_data():
    """샘플 데이터 분석"""
    print("🔍 샘플 데이터 분석:")
    print("-" * 50)
    
    # 세션 로그 분석
    with open("data/session_logs.json", 'r', encoding='utf-8') as f:
        session_data = json.load(f)
        devices = [log['device'] for log in session_data]
        device_counts = Counter(devices)
        print(f"📱 디바이스 분포: {dict(device_counts)}")
    
    # 인게임 액션 로그 분석
    with open("data/ingame_action_logs.json", 'r', encoding='utf-8') as f:
        action_data = json.load(f)
        actions = [log['action_type'] for log in action_data]
        action_counts = Counter(actions)
        print(f"🎯 액션 타입 분포 (상위 5개): {dict(list(action_counts.most_common(5)))}")
    
    # 에러 로그 분석
    with open("data/error_logs.json", 'r', encoding='utf-8') as f:
        error_data = json.load(f)
        error_types = [log['error_type'] for log in error_data]
        error_counts = Counter(error_types)
        print(f"🚨 에러 타입 분포: {dict(error_counts)}")
        
        severities = [log['severity'] for log in error_data]
        severity_counts = Counter(severities)
        print(f"⚠️  심각도 분포: {dict(severity_counts)}")
    
    # 결제 로그 분석
    with open("data/payment_logs.json", 'r', encoding='utf-8') as f:
        payment_data = json.load(f)
        statuses = [log['status'] for log in payment_data]
        status_counts = Counter(statuses)
        print(f"💳 결제 상태 분포: {dict(status_counts)}")
        
        currencies = [log['currency'] for log in payment_data]
        currency_counts = Counter(currencies)
        print(f"💰 통화 분포: {dict(currency_counts)}")
    
    print()

def check_data_consistency():
    """데이터 일관성 검증"""
    print("🔧 데이터 일관성 검증:")
    print("-" * 50)
    
    # 모든 JSON 파일에서 user_id 수집
    all_user_ids = set()
    
    files_to_check = [
        "session_logs.json",
        "ingame_action_logs.json", 
        "item_logs.json",
        "payment_logs.json",
        "error_logs.json"
    ]
    
    for filename in files_to_check:
        with open(f"data/{filename}", 'r', encoding='utf-8') as f:
            data = json.load(f)
            user_ids = {log['user_id'] for log in data}
            all_user_ids.update(user_ids)
            print(f"📊 {filename}: {len(user_ids)}개의 고유 사용자")
    
    print(f"👥 전체 고유 사용자 수: {len(all_user_ids)}명")
    print()

def main():
    """메인 검증 함수"""
    print("🎮 게임 로그 데이터 검증을 시작합니다...\n")
    
    validate_json_files()
    validate_csv_files()
    analyze_sample_data()
    check_data_consistency()
    
    print("✅ 데이터 검증이 완료되었습니다!")

if __name__ == "__main__":
    main()
