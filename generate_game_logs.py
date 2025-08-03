#!/usr/bin/env python3
"""
게임 로그 데이터 생성기
각 로그 타입별로 1만건씩 샘플 데이터를 생성합니다.
"""

import json
import csv
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import os

# Faker 인스턴스 생성 (한국어 지원)
fake = Faker(['ko_KR', 'en_US'])
Faker.seed(42)  # 재현 가능한 결과를 위한 시드 설정
random.seed(42)

class GameLogGenerator:
    def __init__(self):
        self.user_ids = [str(uuid.uuid4()) for _ in range(1000)]  # 1000명의 가상 사용자
        self.item_ids = [f"item_{i:04d}" for i in range(1, 501)]  # 500개의 아이템
        self.quest_ids = [f"quest_{i:03d}" for i in range(1, 101)]  # 100개의 퀘스트
        self.skill_ids = [f"skill_{i:03d}" for i in range(1, 51)]  # 50개의 스킬
        self.regions = ["forest", "desert", "mountain", "city", "dungeon", "castle"]
        self.devices = ["iPhone", "Android", "iPad", "PC"]
        self.os_versions = ["iOS 17.0", "Android 13", "iOS 16.5", "Windows 11", "Android 12"]
        self.app_versions = ["1.0.0", "1.0.1", "1.1.0", "1.1.1", "1.2.0"]
        
    def generate_session_logs(self, count=10000):
        """세션 로그 생성"""
        logs = []
        for i in range(count):
            user_id = random.choice(self.user_ids)
            login_time = fake.date_time_between(start_date='-30d', end_date='now')
            session_duration = random.randint(300, 7200)  # 5분 ~ 2시간
            logout_time = login_time + timedelta(seconds=session_duration)
            
            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": str(uuid.uuid4()),
                "login_time": login_time.isoformat(),
                "logout_time": logout_time.isoformat(),
                "session_duration_seconds": session_duration,
                "device": random.choice(self.devices),
                "os_version": random.choice(self.os_versions),
                "app_version": random.choice(self.app_versions),
                "ip_address": fake.ipv4(),
                "country": fake.country_code(),
                "timestamp": login_time.isoformat()
            }
            logs.append(log)
        return logs
    
    def generate_ingame_action_logs(self, count=10000):
        """인게임 액션 로그 생성"""
        logs = []
        action_types = ["level_start", "level_complete", "level_fail", "quest_accept", 
                       "quest_progress", "quest_complete", "battle_start", "battle_end",
                       "skill_use", "friend_add", "guild_join", "chat_send", "region_move"]
        
        for i in range(count):
            user_id = random.choice(self.user_ids)
            action_type = random.choice(action_types)
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            
            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": str(uuid.uuid4()),
                "action_type": action_type,
                "timestamp": timestamp.isoformat(),
                "details": self._generate_action_details(action_type),
                "region": random.choice(self.regions),
                "level": random.randint(1, 100)
            }
            logs.append(log)
        return logs
    
    def _generate_action_details(self, action_type):
        """액션 타입별 상세 정보 생성"""
        if action_type in ["level_start", "level_complete", "level_fail"]:
            return {
                "level_id": f"level_{random.randint(1, 50):03d}",
                "difficulty": random.choice(["easy", "normal", "hard", "expert"]),
                "score": random.randint(0, 10000) if action_type == "level_complete" else 0
            }
        elif action_type in ["quest_accept", "quest_progress", "quest_complete"]:
            return {
                "quest_id": random.choice(self.quest_ids),
                "progress": random.randint(0, 100),
                "reward_exp": random.randint(100, 1000) if action_type == "quest_complete" else 0
            }
        elif action_type in ["battle_start", "battle_end"]:
            return {
                "enemy_type": random.choice(["goblin", "orc", "dragon", "skeleton", "boss"]),
                "battle_result": random.choice(["win", "lose", "draw"]) if action_type == "battle_end" else "ongoing",
                "damage_dealt": random.randint(100, 5000),
                "damage_received": random.randint(50, 3000)
            }
        elif action_type == "skill_use":
            return {
                "skill_id": random.choice(self.skill_ids),
                "target_type": random.choice(["enemy", "self", "ally"]),
                "mana_cost": random.randint(10, 100)
            }
        else:
            return {"additional_info": fake.text(max_nb_chars=100)}
    
    def generate_item_logs(self, count=10000):
        """아이템 로그 생성"""
        logs = []
        action_types = ["acquire", "use", "sell", "buy", "trade", "enhance", "synthesize"]
        acquire_methods = ["drop", "quest_reward", "purchase", "craft", "gift"]
        
        for i in range(count):
            user_id = random.choice(self.user_ids)
            action_type = random.choice(action_types)
            item_id = random.choice(self.item_ids)
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            
            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": str(uuid.uuid4()),
                "item_id": item_id,
                "action_type": action_type,
                "quantity": random.randint(1, 10),
                "timestamp": timestamp.isoformat(),
                "item_details": self._generate_item_details(action_type, acquire_methods)
            }
            logs.append(log)
        return logs
    
    def _generate_item_details(self, action_type, acquire_methods):
        """아이템 액션별 상세 정보 생성"""
        details = {
            "item_name": fake.word(),
            "item_type": random.choice(["weapon", "armor", "potion", "material", "accessory"]),
            "rarity": random.choice(["common", "uncommon", "rare", "epic", "legendary"])
        }
        
        if action_type == "acquire":
            details["acquire_method"] = random.choice(acquire_methods)
        elif action_type in ["sell", "buy", "trade"]:
            details["price"] = random.randint(100, 10000)
            details["currency"] = random.choice(["gold", "gem", "coin"])
        elif action_type in ["enhance", "synthesize"]:
            details["success"] = random.choice([True, False])
            details["enhancement_level"] = random.randint(1, 10)
            
        return details
    
    def generate_payment_logs(self, count=10000):
        """결제 로그 생성"""
        logs = []
        products = ["gem_pack_small", "gem_pack_medium", "gem_pack_large", "premium_pass", 
                   "character_skin", "weapon_pack", "exp_booster", "gold_pack"]
        payment_methods = ["credit_card", "paypal", "google_pay", "apple_pay", "bank_transfer"]
        
        for i in range(count):
            user_id = random.choice(self.user_ids)
            product = random.choice(products)
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            
            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "transaction_id": str(uuid.uuid4()),
                "product_id": product,
                "amount": round(random.uniform(0.99, 99.99), 2),
                "currency": random.choice(["USD", "KRW", "EUR", "JPY"]),
                "payment_method": random.choice(payment_methods),
                "status": random.choice(["completed", "pending", "failed", "refunded"]),
                "country": fake.country_code(),
                "promotion_code": fake.word() if random.random() < 0.3 else None,
                "timestamp": timestamp.isoformat()
            }
            logs.append(log)
        return logs
    
    def generate_error_logs(self, count=10000):
        """에러 로그 생성"""
        logs = []
        error_types = ["client_crash", "rendering_error", "server_connection_failed", 
                      "timeout", "gameplay_logic_error", "frame_drop", "loading_delay"]
        severity_levels = ["low", "medium", "high", "critical"]
        
        for i in range(count):
            user_id = random.choice(self.user_ids)
            error_type = random.choice(error_types)
            timestamp = fake.date_time_between(start_date='-30d', end_date='now')
            
            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": str(uuid.uuid4()),
                "error_type": error_type,
                "severity": random.choice(severity_levels),
                "error_message": fake.sentence(),
                "stack_trace": fake.text(max_nb_chars=500) if random.random() < 0.5 else None,
                "device": random.choice(self.devices),
                "os_version": random.choice(self.os_versions),
                "app_version": random.choice(self.app_versions),
                "timestamp": timestamp.isoformat(),
                "performance_metrics": self._generate_performance_metrics(error_type)
            }
            logs.append(log)
        return logs
    
    def _generate_performance_metrics(self, error_type):
        """성능 관련 메트릭 생성"""
        metrics = {
            "cpu_usage": round(random.uniform(10, 100), 2),
            "memory_usage": round(random.uniform(100, 2000), 2),  # MB
            "network_latency": random.randint(10, 500)  # ms
        }
        
        if error_type == "frame_drop":
            metrics["fps"] = random.randint(5, 30)
            metrics["target_fps"] = 60
        elif error_type == "loading_delay":
            metrics["loading_time"] = round(random.uniform(5, 30), 2)  # seconds
            
        return metrics
    
    def save_to_json(self, data, filename):
        """JSON 파일로 저장"""
        filepath = os.path.join("data", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {filename} 저장 완료 ({len(data)}건)")
    
    def save_to_csv(self, data, filename):
        """CSV 파일로 저장"""
        if not data:
            return
            
        filepath = os.path.join("data", filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            
            for row in data:
                # 중첩된 딕셔너리를 JSON 문자열로 변환
                flattened_row = {}
                for key, value in row.items():
                    if isinstance(value, dict):
                        flattened_row[key] = json.dumps(value, ensure_ascii=False)
                    else:
                        flattened_row[key] = value
                writer.writerow(flattened_row)
        print(f"✅ {filename} 저장 완료 ({len(data)}건)")

def main():
    """메인 실행 함수"""
    print("🎮 게임 로그 데이터 생성을 시작합니다...")
    
    generator = GameLogGenerator()
    
    # 1. 세션 로그 생성
    print("\n📊 세션 로그 생성 중...")
    session_logs = generator.generate_session_logs(10000)
    generator.save_to_json(session_logs, "session_logs.json")
    generator.save_to_csv(session_logs, "session_logs.csv")
    
    # 2. 인게임 액션 로그 생성
    print("\n🎯 인게임 액션 로그 생성 중...")
    action_logs = generator.generate_ingame_action_logs(10000)
    generator.save_to_json(action_logs, "ingame_action_logs.json")
    generator.save_to_csv(action_logs, "ingame_action_logs.csv")
    
    # 3. 아이템 로그 생성
    print("\n🎒 아이템 로그 생성 중...")
    item_logs = generator.generate_item_logs(10000)
    generator.save_to_json(item_logs, "item_logs.json")
    generator.save_to_csv(item_logs, "item_logs.csv")
    
    # 4. 결제 로그 생성
    print("\n💳 결제 로그 생성 중...")
    payment_logs = generator.generate_payment_logs(10000)
    generator.save_to_json(payment_logs, "payment_logs.json")
    generator.save_to_csv(payment_logs, "payment_logs.csv")
    
    # 5. 에러 로그 생성
    print("\n🚨 에러 로그 생성 중...")
    error_logs = generator.generate_error_logs(10000)
    generator.save_to_json(error_logs, "error_logs.json")
    generator.save_to_csv(error_logs, "error_logs.csv")
    
    print("\n🎉 모든 게임 로그 데이터 생성이 완료되었습니다!")
    print(f"📁 생성된 파일들은 'data' 폴더에 저장되었습니다.")
    
    # 생성된 파일 목록 출력
    print("\n📋 생성된 파일 목록:")
    for filename in os.listdir("data"):
        filepath = os.path.join("data", filename)
        size = os.path.getsize(filepath)
        print(f"  - {filename} ({size:,} bytes)")

if __name__ == "__main__":
    main()
