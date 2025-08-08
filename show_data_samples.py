#!/usr/bin/env python3
"""
생성된 데이터 샘플 확인
"""

import json
import pandas as pd

def show_samples():
    print("📊 생성된 게임 로그 데이터 샘플")
    print("=" * 60)
    
    # 세션 로그 샘플
    with open('data/session_logs.json', 'r', encoding='utf-8') as f:
        sessions = json.load(f)
    
    print("\n🔐 세션 로그 샘플 (최근 5건):")
    for session in sessions[:5]:
        print(f"  사용자: {session['user_id'][:8]}...")
        print(f"  로그인: {session['login_time']}")
        print(f"  세션시간: {session['session_duration_seconds']/60:.1f}분")
        print(f"  디바이스: {session['device']}")
        print()
    
    # 인게임 액션 로그에서 스테이지별 샘플
    with open('data/ingame_action_logs.json', 'r', encoding='utf-8') as f:
        actions = json.load(f)
    
    print("\n🎯 스테이지별 액션 로그 샘플:")
    df_actions = pd.DataFrame(actions)
    
    for stage in ['stage_01', 'stage_06', 'stage_10']:
        stage_actions = df_actions[df_actions['stage'] == stage].head(2)
        print(f"\n  {stage}:")
        for _, action in stage_actions.iterrows():
            print(f"    사용자: {action['user_id'][:8]}... | 액션: {action['action_type']} | 레벨: {action['level']}")
    
    # 특별 무기 구매 로그
    with open('data/item_logs.json', 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    special_weapons = [item for item in items if item['item_id'] == 'weapon_legendary_001']
    print(f"\n⚔️ 특별 무기 구매 로그 ({len(special_weapons)}건):")
    for weapon in special_weapons[:3]:
        print(f"  사용자: {weapon['user_id'][:8]}... | 가격: ${weapon['price']} | 등급: {weapon['rarity']}")
    
    # 결제 로그 샘플
    with open('data/payment_logs.json', 'r', encoding='utf-8') as f:
        payments = json.load(f)
    
    high_payments = [p for p in payments if p['amount'] >= 49.99]
    print(f"\n💰 고액 결제 로그 ({len(high_payments)}건):")
    for payment in high_payments[:3]:
        print(f"  사용자: {payment['user_id'][:8]}... | 금액: ${payment['amount']} | 상품: {payment['product_name']}")

if __name__ == "__main__":
    show_samples()
