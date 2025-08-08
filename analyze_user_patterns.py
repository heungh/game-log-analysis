#!/usr/bin/env python3
"""
사용자 이탈 패턴 분석 스크립트
"""

import json
import pandas as pd
from datetime import datetime

def analyze_user_patterns():
    # 데이터 로드
    with open('data/session_logs.json', 'r', encoding='utf-8') as f:
        sessions = json.load(f)
    
    with open('data/ingame_action_logs.json', 'r', encoding='utf-8') as f:
        actions = json.load(f)
    
    with open('data/item_logs.json', 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    with open('data/payment_logs.json', 'r', encoding='utf-8') as f:
        payments = json.load(f)
    
    # DataFrame 변환
    df_sessions = pd.DataFrame(sessions)
    df_actions = pd.DataFrame(actions)
    df_items = pd.DataFrame(items)
    df_payments = pd.DataFrame(payments)
    
    print("🔍 사용자 이탈 패턴 분석 결과")
    print("=" * 50)
    
    # 1. 일별 활성 사용자 수 분석
    df_sessions['login_date'] = pd.to_datetime(df_sessions['login_time']).dt.date
    daily_users = df_sessions.groupby('login_date')['user_id'].nunique().reset_index()
    daily_users = daily_users.sort_values('login_date')
    
    print(f"\n📅 일별 활성 사용자 수:")
    print(f"초기 (첫 3일 평균): {daily_users.head(3)['user_id'].mean():.0f}명")
    print(f"후기 (마지막 3일 평균): {daily_users.tail(3)['user_id'].mean():.0f}명")
    print(f"감소율: {(1 - daily_users.tail(3)['user_id'].mean() / daily_users.head(3)['user_id'].mean()) * 100:.1f}%")
    
    # 2. 스테이지별 사용자 분포
    stage_users = df_actions.groupby('stage')['user_id'].nunique().reset_index()
    stage_users['stage_num'] = stage_users['stage'].str.extract('(\d+)').astype(int)
    stage_users = stage_users.sort_values('stage_num')
    
    print(f"\n🎯 스테이지별 활성 사용자 수:")
    for _, row in stage_users.iterrows():
        print(f"  {row['stage']}: {row['user_id']}명")
    
    # 3. 특별 무기 구매 분석
    special_weapon_buyers = df_items[df_items['item_id'] == 'weapon_legendary_001']['user_id'].unique()
    print(f"\n⚔️ 특별 무기 구매 분석:")
    print(f"특별 무기 구매자: {len(special_weapon_buyers)}명")
    
    # 특별 무기 구매자의 스테이지 진행도
    weapon_buyer_stages = df_actions[df_actions['user_id'].isin(special_weapon_buyers)]
    weapon_buyer_max_stages = weapon_buyer_stages.groupby('user_id')['stage'].apply(
        lambda x: x.str.extract('(\d+)').astype(int).max()
    )
    
    print(f"특별 무기 구매자 평균 최대 스테이지: {weapon_buyer_max_stages.mean():.1f}")
    
    # 4. 결제 패턴 분석
    paying_users = df_payments['user_id'].unique()
    total_users = df_sessions['user_id'].nunique()
    
    print(f"\n💳 결제 패턴 분석:")
    print(f"전체 사용자: {total_users}명")
    print(f"결제 사용자: {len(paying_users)}명 ({len(paying_users)/total_users*100:.1f}%)")
    
    # 결제자와 비결제자의 스테이지 진행도 비교
    payer_stages = df_actions[df_actions['user_id'].isin(paying_users)]
    non_payer_stages = df_actions[~df_actions['user_id'].isin(paying_users)]
    
    payer_max_stages = payer_stages.groupby('user_id')['stage'].apply(
        lambda x: x.str.extract('(\d+)').astype(int).max()
    )
    non_payer_max_stages = non_payer_stages.groupby('user_id')['stage'].apply(
        lambda x: x.str.extract('(\d+)').astype(int).max()
    )
    
    print(f"결제자 평균 최대 스테이지: {payer_max_stages.mean():.1f}")
    print(f"비결제자 평균 최대 스테이지: {non_payer_max_stages.mean():.1f}")
    
    # 5. 세션 지속 시간 분석
    df_sessions['session_hours'] = df_sessions['session_duration_seconds'] / 3600
    
    payer_sessions = df_sessions[df_sessions['user_id'].isin(paying_users)]
    non_payer_sessions = df_sessions[~df_sessions['user_id'].isin(paying_users)]
    
    print(f"\n⏰ 세션 지속 시간 분석:")
    print(f"결제자 평균 세션 시간: {payer_sessions['session_hours'].mean():.1f}시간")
    print(f"비결제자 평균 세션 시간: {non_payer_sessions['session_hours'].mean():.1f}시간")
    
    # 6. 스테이지 6-7에서의 이탈 패턴
    stage_6_7_users = df_actions[df_actions['stage'].isin(['stage_06', 'stage_07'])]['user_id'].unique()
    stage_8_plus_users = df_actions[df_actions['stage'].str.extract('(\d+)').astype(int)[0] >= 8]['user_id'].unique()
    
    print(f"\n🚪 이탈 패턴 분석:")
    print(f"스테이지 6-7 도달 사용자: {len(stage_6_7_users)}명")
    print(f"스테이지 8+ 진행 사용자: {len(stage_8_plus_users)}명")
    print(f"스테이지 6-7에서 이탈률: {(1 - len(stage_8_plus_users)/len(stage_6_7_users))*100:.1f}%")
    
    return {
        'daily_users': daily_users,
        'stage_users': stage_users,
        'special_weapon_buyers': special_weapon_buyers,
        'paying_users': paying_users
    }

if __name__ == "__main__":
    results = analyze_user_patterns()
