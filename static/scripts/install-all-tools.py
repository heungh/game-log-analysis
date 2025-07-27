#!/usr/bin/env python3
"""
통합 로그 수집 도구 설치 스크립트
Kinesis Agent, Vector, Fluent Bit을 순차적으로 설치합니다.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class LogCollectorInstaller:
    def __init__(self):
        self.log_file = "/var/log/log-collector-install.log"
        self.script_dir = Path(__file__).parent
        self.tools = {
            'kinesis-agent': {
                'name': 'Kinesis Agent',
                'script': 'install-kinesis-agent.sh',
                'service': 'aws-kinesis-agent',
                'port': None,
                'description': 'AWS Kinesis Agent for streaming data to Kinesis'
            },
            'vector': {
                'name': 'Vector',
                'script': 'install-vector.sh',
                'service': 'vector',
                'port': 8686,
                'description': 'High-performance log collector and processor'
            },
            'fluent-bit': {
                'name': 'Fluent Bit',
                'script': 'install-fluent-bit.sh',
                'service': 'fluent-bit',
                'port': 2020,
                'description': 'Lightweight log processor and forwarder'
            }
        }
        
    def log(self, message, level="INFO"):
        """로그 메시지 출력 및 파일 저장"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"로그 파일 쓰기 실패: {e}")
    
    def run_command(self, command, check=True):
        """명령어 실행"""
        try:
            self.log(f"명령어 실행: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                check=check
            )
            
            if result.stdout:
                self.log(f"출력: {result.stdout.strip()}")
            if result.stderr:
                self.log(f"에러: {result.stderr.strip()}", "WARN")
                
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"명령어 실행 실패: {e}", "ERROR")
            if check:
                raise
            return e
    
    def check_root_privileges(self):
        """루트 권한 확인"""
        if os.geteuid() != 0:
            self.log("이 스크립트는 루트 권한이 필요합니다.", "ERROR")
            self.log("sudo python3 install-all-tools.py 로 실행해주세요.", "ERROR")
            sys.exit(1)
    
    def install_prerequisites(self):
        """필수 패키지 설치"""
        self.log("=== 필수 패키지 설치 시작 ===")
        
        packages = [
            "curl", "wget", "tar", "gzip", "unzip", 
            "python3-pip", "jq", "htop", "nano"
        ]
        
        for package in packages:
            self.log(f"{package} 설치 중...")
            self.run_command(f"yum install -y {package}", check=False)
        
        self.log("=== 필수 패키지 설치 완료 ===")
    
    def install_tool(self, tool_key):
        """개별 도구 설치"""
        tool = self.tools[tool_key]
        script_path = self.script_dir / tool['script']
        
        self.log(f"=== {tool['name']} 설치 시작 ===")
        
        if not script_path.exists():
            self.log(f"설치 스크립트를 찾을 수 없습니다: {script_path}", "ERROR")
            return False
        
        try:
            # 스크립트 실행 권한 부여
            self.run_command(f"chmod +x {script_path}")
            
            # 스크립트 실행
            result = self.run_command(f"bash {script_path}")
            
            # 설치 확인
            time.sleep(5)
            if self.check_service_status(tool['service']):
                self.log(f"✅ {tool['name']} 설치 및 시작 성공")
                return True
            else:
                self.log(f"❌ {tool['name']} 서비스 시작 실패", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ {tool['name']} 설치 실패: {e}", "ERROR")
            return False
    
    def check_service_status(self, service_name):
        """서비스 상태 확인"""
        try:
            result = self.run_command(f"systemctl is-active {service_name}", check=False)
            return result.returncode == 0
        except:
            return False
    
    def check_port_status(self, port):
        """포트 상태 확인"""
        try:
            result = self.run_command(f"netstat -tlnp | grep :{port}", check=False)
            return result.returncode == 0
        except:
            return False
    
    def generate_status_report(self):
        """설치 상태 보고서 생성"""
        self.log("=== 설치 상태 보고서 생성 ===")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "tools": {},
            "summary": {
                "total": len(self.tools),
                "installed": 0,
                "failed": 0
            }
        }
        
        for tool_key, tool in self.tools.items():
            service_status = self.check_service_status(tool['service'])
            port_status = self.check_port_status(tool['port']) if tool['port'] else None
            
            tool_status = {
                "name": tool['name'],
                "service_active": service_status,
                "port_listening": port_status,
                "port": tool['port'],
                "description": tool['description']
            }
            
            report["tools"][tool_key] = tool_status
            
            if service_status:
                report["summary"]["installed"] += 1
            else:
                report["summary"]["failed"] += 1
        
        # JSON 보고서 저장
        report_file = "/home/ec2-user/installation-report.json"
        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            self.log(f"설치 보고서 저장: {report_file}")
        except Exception as e:
            self.log(f"보고서 저장 실패: {e}", "ERROR")
        
        # 콘솔 출력
        print("\n" + "="*60)
        print("📊 설치 상태 보고서")
        print("="*60)
        
        for tool_key, status in report["tools"].items():
            status_icon = "✅" if status["service_active"] else "❌"
            port_info = f" (포트: {status['port']})" if status['port'] else ""
            print(f"{status_icon} {status['name']}{port_info}")
            
            if status["service_active"]:
                print(f"   └─ 서비스: 활성화")
                if status['port'] and status['port_listening']:
                    print(f"   └─ 포트 {status['port']}: 리스닝 중")
                elif status['port']:
                    print(f"   └─ 포트 {status['port']}: 비활성화")
            else:
                print(f"   └─ 서비스: 비활성화")
        
        print(f"\n📈 요약: {report['summary']['installed']}/{report['summary']['total']} 도구 설치 완료")
        print("="*60)
        
        return report
    
    def create_management_script(self):
        """통합 관리 스크립트 생성"""
        self.log("=== 통합 관리 스크립트 생성 ===")
        
        script_content = '''#!/bin/bash

echo "=================================================="
echo "🔧 로그 수집 도구 통합 관리 스크립트"
echo "=================================================="

show_status() {
    echo "📊 서비스 상태:"
    echo "----------------------------------------"
    
    services=("aws-kinesis-agent" "vector" "fluent-bit")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet $service; then
            echo "✅ $service: 활성화"
        else
            echo "❌ $service: 비활성화"
        fi
    done
    
    echo ""
    echo "🌐 포트 상태:"
    echo "----------------------------------------"
    
    ports=("8686:Vector API" "2020:Fluent Bit HTTP")
    for port_info in "${ports[@]}"; do
        port=$(echo $port_info | cut -d: -f1)
        name=$(echo $port_info | cut -d: -f2)
        
        if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
            echo "✅ $name (포트 $port): 리스닝 중"
        else
            echo "❌ $name (포트 $port): 비활성화"
        fi
    done
}

case "$1" in
    status)
        show_status
        ;;
    start)
        echo "모든 로그 수집 도구 시작 중..."
        sudo systemctl start aws-kinesis-agent vector fluent-bit
        echo "✅ 완료"
        show_status
        ;;
    stop)
        echo "모든 로그 수집 도구 중지 중..."
        sudo systemctl stop aws-kinesis-agent vector fluent-bit
        echo "✅ 완료"
        show_status
        ;;
    restart)
        echo "모든 로그 수집 도구 재시작 중..."
        sudo systemctl restart aws-kinesis-agent vector fluent-bit
        echo "✅ 완료"
        show_status
        ;;
    logs)
        echo "통합 로그 확인 (Ctrl+C로 종료)..."
        sudo journalctl -u aws-kinesis-agent -u vector -u fluent-bit -f
        ;;
    test)
        echo "테스트 로그 생성 중..."
        timestamp=$(date -Iseconds)
        echo "{\\"timestamp\\":\\"$timestamp\\",\\"level\\":\\"INFO\\",\\"message\\":\\"Integration test log\\",\\"player_id\\":\\"test999\\",\\"event_type\\":\\"test\\",\\"source\\":\\"integration-test\\"}" >> /var/log/game-logs/game.log
        echo "✅ 테스트 로그가 생성되었습니다."
        ;;
    report)
        if [ -f /home/ec2-user/installation-report.json ]; then
            echo "📋 설치 보고서:"
            cat /home/ec2-user/installation-report.json | jq . 2>/dev/null || cat /home/ec2-user/installation-report.json
        else
            echo "❌ 설치 보고서를 찾을 수 없습니다."
        fi
        ;;
    *)
        echo "사용법: $0 {status|start|stop|restart|logs|test|report}"
        echo ""
        echo "명령어 설명:"
        echo "  status  - 모든 서비스 상태 확인"
        echo "  start   - 모든 서비스 시작"
        echo "  stop    - 모든 서비스 중지"
        echo "  restart - 모든 서비스 재시작"
        echo "  logs    - 통합 로그 실시간 확인"
        echo "  test    - 테스트 로그 생성"
        echo "  report  - 설치 보고서 확인"
        exit 1
        ;;
esac
'''
        
        script_path = "/home/ec2-user/manage-log-collectors.sh"
        try:
            with open(script_path, "w") as f:
                f.write(script_content)
            
            os.chmod(script_path, 0o755)
            self.run_command(f"chown ec2-user:ec2-user {script_path}")
            self.log(f"통합 관리 스크립트 생성: {script_path}")
            
        except Exception as e:
            self.log(f"관리 스크립트 생성 실패: {e}", "ERROR")
    
    def install_all(self, tools_to_install=None):
        """모든 도구 설치"""
        if tools_to_install is None:
            tools_to_install = list(self.tools.keys())
        
        self.log("🚀 로그 수집 도구 통합 설치 시작")
        self.log(f"설치할 도구: {', '.join([self.tools[t]['name'] for t in tools_to_install])}")
        
        # 루트 권한 확인
        self.check_root_privileges()
        
        # 필수 패키지 설치
        self.install_prerequisites()
        
        # 각 도구 설치
        success_count = 0
        for tool_key in tools_to_install:
            if self.install_tool(tool_key):
                success_count += 1
            time.sleep(2)  # 설치 간 대기
        
        # 통합 관리 스크립트 생성
        self.create_management_script()
        
        # 상태 보고서 생성
        report = self.generate_status_report()
        
        # 최종 결과
        total = len(tools_to_install)
        self.log(f"🎉 설치 완료: {success_count}/{total} 도구 성공")
        
        if success_count == total:
            self.log("✅ 모든 도구가 성공적으로 설치되었습니다!")
            print("\n🔧 사용법:")
            print("- 상태 확인: ./manage-log-collectors.sh status")
            print("- 모든 서비스 시작: ./manage-log-collectors.sh start")
            print("- 테스트 로그 생성: ./manage-log-collectors.sh test")
            print("- 설치 보고서: ./manage-log-collectors.sh report")
        else:
            self.log("⚠️  일부 도구 설치에 실패했습니다. 로그를 확인해주세요.", "WARN")
        
        return success_count == total

def main():
    """메인 함수"""
    installer = LogCollectorInstaller()
    
    if len(sys.argv) > 1:
        # 특정 도구만 설치
        tools_to_install = []
        for arg in sys.argv[1:]:
            if arg in installer.tools:
                tools_to_install.append(arg)
            else:
                print(f"알 수 없는 도구: {arg}")
                print(f"사용 가능한 도구: {', '.join(installer.tools.keys())}")
                sys.exit(1)
        
        installer.install_all(tools_to_install)
    else:
        # 모든 도구 설치
        installer.install_all()

if __name__ == "__main__":
    main()
