#!/usr/bin/env python3
"""
게임 로그 데이터 생성기 - 사용자 이탈 패턴 반영
초기 유입 후 시간이 지날수록 감소, 특정 스테이지에서 이탈하는 패턴 구현
"""

import json
import csv
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker(["ko_KR", "en_US"])
Faker.seed(42)
random.seed(42)

log_dir = "/var/log/game"
os.makedirs(log_dir, exist_ok=True)


class GameLogGenerator:
    def __init__(self):
        self.user_ids = [str(uuid.uuid4()) for _ in range(1000)]
        self.item_ids = [f"item_{i:04d}" for i in range(1, 501)]
        self.special_weapon = "weapon_legendary_001"  # 클리어 핵심 아이템
        self.quest_ids = [f"quest_{i:03d}" for i in range(1, 101)]
        self.skill_ids = [f"skill_{i:03d}" for i in range(1, 51)]
        self.regions = ["forest", "desert", "mountain", "city", "dungeon", "castle"]
        self.devices = ["iPhone", "Android", "iPad", "PC"]
        self.os_versions = [
            "iOS 17.0",
            "Android 13",
            "iOS 16.5",
            "Windows 11",
            "Android 12",
        ]
        self.app_versions = ["1.0.0", "1.0.1", "1.1.0", "1.1.1", "1.2.0"]
        self.sessions = []
        self.user_progress = {}
        self.successful_users = set()

    def generate_session_logs(self, count=10000):
        """세션 로그 생성 - 시간이 지날수록 유저 수 감소"""
        logs = []

        # 30%의 성공 유저 선정
        success_count = int(len(self.user_ids) * 0.3)
        self.successful_users = set(random.sample(self.user_ids, success_count))

        start_date = datetime.now() - timedelta(days=30)
        for i in range(count):
            days_passed = random.randint(0, 30)
            retention_rate = max(0.2, 1.0 - (days_passed * 0.027))

            if random.random() < 0.3:
                user_id = random.choice(list(self.successful_users))
                retention_rate = max(0.7, retention_rate + 0.5)
            else:
                if random.random() > retention_rate:
                    continue
                user_id = random.choice(
                    [u for u in self.user_ids if u not in self.successful_users]
                )

            login_time = start_date + timedelta(
                days=days_passed,
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            if user_id in self.successful_users:
                session_duration = random.randint(1800, 10800)
            else:
                session_duration = random.randint(300, 3600)

            logout_time = login_time + timedelta(seconds=session_duration)
            session_id = str(uuid.uuid4())

            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session_id,
                "login_time": login_time.isoformat(),
                "logout_time": logout_time.isoformat(),
                "session_duration_seconds": session_duration,
                "device": random.choice(self.devices),
                "os_version": random.choice(self.os_versions),
                "app_version": random.choice(self.app_versions),
                "ip_address": fake.ipv4(),
                "country": fake.country_code(),
                "timestamp": login_time.isoformat(),
            }
            logs.append(log)

            self.sessions.append(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "login_time": login_time,
                    "logout_time": logout_time,
                }
            )
        return logs

    def generate_ingame_action_logs(self, count=10000):
        """인게임 액션 로그 생성 - 스테이지별 진행도 반영"""
        if not self.sessions:
            print("세션 로그를 먼저 생성해주세요.")
            return []

        logs = []
        stages = [f"stage_{i:02d}" for i in range(1, 11)]

        for i in range(count):
            session = random.choice(self.sessions)
            user_id = session["user_id"]

            if user_id not in self.user_progress:
                if user_id in self.successful_users:
                    max_stage = 10
                else:
                    max_stage = random.choices([5, 6, 7], weights=[30, 50, 20])[0]
                self.user_progress[user_id] = max_stage

            current_stage = random.randint(1, self.user_progress[user_id])
            stage_name = f"stage_{current_stage:02d}"

            if current_stage <= 5:
                action_types = ["move", "attack", "collect", "jump"]
            elif current_stage <= 7:
                action_types = ["move", "attack", "defend", "special_attack"]
            else:
                action_types = [
                    "move",
                    "attack",
                    "defend",
                    "special_attack",
                    "ultimate",
                ]

            session_start = session["login_time"]
            session_end = session["logout_time"]
            action_time = session_start + timedelta(
                seconds=random.randint(
                    0, int((session_end - session_start).total_seconds())
                )
            )

            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session["session_id"],
                "timestamp": action_time.isoformat(),
                "action_type": random.choice(action_types),
                "stage": stage_name,
                "region": random.choice(self.regions),
                "quest_id": random.choice(self.quest_ids),
                "skill_used": random.choice(self.skill_ids),
                "experience_gained": random.randint(10, 100),
                "level": min(current_stage * 5 + random.randint(1, 10), 50),
            }
            logs.append(log)

        return logs

    def generate_item_logs(self, count=10000):
        """아이템 로그 생성 - 특별 무기 구매 패턴 반영"""
        if not self.sessions:
            print("세션 로그를 먼저 생성해주세요.")
            return []

        logs = []
        action_types = ["acquire", "use", "sell", "buy", "trade", "enhance"]

        for i in range(count):
            session = random.choice(self.sessions)
            user_id = session["user_id"]

            session_start = session["login_time"]
            session_end = session["logout_time"]
            timestamp = session_start + timedelta(
                seconds=random.randint(
                    0, int((session_end - session_start).total_seconds())
                )
            )

            # 성공 유저는 특별 무기 구매 확률 높음
            if user_id in self.successful_users and random.random() < 0.1:
                item_id = self.special_weapon
                action_type = "buy"
                price = 9900  # 고가 아이템
            else:
                item_id = random.choice(self.item_ids)
                action_type = random.choice(action_types)
                price = random.randint(100, 5000)

            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session["session_id"],
                "timestamp": timestamp.isoformat(),
                "action_type": action_type,
                "item_id": item_id,
                "item_name": f"아이템_{item_id.split('_')[-1]}",
                "quantity": random.randint(1, 5),
                "price": price,
                "currency": "gold",
                "item_level": random.randint(1, 20),
                "rarity": (
                    "legendary"
                    if item_id == self.special_weapon
                    else random.choice(["common", "rare", "epic"])
                ),
            }
            logs.append(log)

        return logs

    def generate_payment_logs(self, count=10000):
        """결제 로그 생성 - 성공 유저의 결제 패턴"""
        if not self.sessions:
            print("세션 로그를 먼저 생성해주세요.")
            return []

        logs = []

        for i in range(count):
            session = random.choice(self.sessions)
            user_id = session["user_id"]

            # 성공 유저가 결제할 확률이 훨씬 높음
            if user_id in self.successful_users:
                payment_prob = 0.3
            else:
                payment_prob = 0.05

            if random.random() > payment_prob:
                continue

            session_start = session["login_time"]
            session_end = session["logout_time"]
            timestamp = session_start + timedelta(
                seconds=random.randint(
                    0, int((session_end - session_start).total_seconds())
                )
            )

            # 성공 유저는 더 비싼 결제
            if user_id in self.successful_users:
                amount = random.choice([9.99, 19.99, 49.99, 99.99])
                product = random.choice(
                    ["special_weapon_pack", "premium_currency", "exp_booster"]
                )
            else:
                amount = random.choice([0.99, 2.99, 4.99])
                product = random.choice(["basic_currency", "small_booster"])

            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session["session_id"],
                "timestamp": timestamp.isoformat(),
                "transaction_id": str(uuid.uuid4()),
                "product_id": product,
                "product_name": product.replace("_", " ").title(),
                "amount": amount,
                "currency": "USD",
                "payment_method": random.choice(
                    ["credit_card", "paypal", "google_pay", "apple_pay"]
                ),
                "status": random.choices(["success", "failed"], weights=[95, 5])[0],
                "country": fake.country_code(),
            }
            logs.append(log)

        return logs

    def generate_error_logs(self, count=10000):
        """에러 로그 생성"""
        if not self.sessions:
            print("세션 로그를 먼저 생성해주세요.")
            return []

        logs = []
        error_types = [
            "network_timeout",
            "server_error",
            "client_crash",
            "payment_failed",
            "login_failed",
            "data_sync_error",
            "memory_error",
        ]

        for i in range(count):
            session = random.choice(self.sessions)
            user_id = session["user_id"]

            session_start = session["login_time"]
            session_end = session["logout_time"]
            timestamp = session_start + timedelta(
                seconds=random.randint(
                    0, int((session_end - session_start).total_seconds())
                )
            )

            error_type = random.choice(error_types)

            log = {
                "log_id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": session["session_id"],
                "timestamp": timestamp.isoformat(),
                "error_type": error_type,
                "error_code": f"E{random.randint(1000, 9999)}",
                "error_message": f"{error_type.replace('_', ' ').title()} occurred",
                "severity": random.choice(["low", "medium", "high", "critical"]),
                "device": random.choice(self.devices),
                "os_version": random.choice(self.os_versions),
                "app_version": random.choice(self.app_versions),
                "stack_trace": fake.text(max_nb_chars=200),
            }
            logs.append(log)

        return logs

    def save_to_json(self, data, filename):
        """JSON 파일로 저장"""
        if not data:
            print(f"❌ {filename} 저장 실패: 데이터가 없습니다.")
            return

        filepath = os.path.join(log_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {filename} 저장 완료 ({len(data)}건)")

    def save_to_csv(self, data, filename):
        """CSV 파일로 저장"""
        if not data:
            print(f"❌ {filename} 저장 실패: 데이터가 없습니다.")
            return

        filepath = os.path.join(log_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"✅ {filename} 저장 완료 ({len(data)}건)")


def main():
    generator = GameLogGenerator()

    # 데이터 디렉토리 생성
    os.makedirs("data", exist_ok=True)

    print("🎮 게임 로그 데이터 생성 시작...")

    # 1. 세션 로그 생성 (가장 먼저)
    print("\n📊 세션 로그 생성 중...")
    session_logs = generator.generate_session_logs(10000)
    generator.save_to_json(session_logs, "session.log")

    # 2. 인게임 액션 로그 생성
    print("\n🎯 인게임 액션 로그 생성 중...")
    ingame_logs = generator.generate_ingame_action_logs(10000)
    generator.save_to_json(ingame_logs, "ingame_action.log")

    # 3. 아이템 로그 생성
    print("\n🎒 아이템 로그 생성 중...")
    item_logs = generator.generate_item_logs(10000)
    generator.save_to_json(item_logs, "item.log")

    # 4. 결제 로그 생성
    print("\n💳 결제 로그 생성 중...")
    payment_logs = generator.generate_payment_logs(10000)
    generator.save_to_json(payment_logs, "payment.log")

    # 5. 에러 로그 생성
    print("\n❌ 에러 로그 생성 중...")
    error_logs = generator.generate_error_logs(10000)
    generator.save_to_json(error_logs, "error.log")

    print(f"\n🎉 모든 로그 생성 완료!")
    print(f"📈 성공 유저: {len(generator.successful_users)}명 (30%)")
    print(
        f"📉 실패 유저: {len(generator.user_ids) - len(generator.successful_users)}명 (70%)"
    )


if __name__ == "__main__":
    main()
