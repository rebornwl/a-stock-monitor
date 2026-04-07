"""
推送测试脚本 - 验证Bark和Server酱连接
"""
import requests
import sys

BARK_URL = "https://api.day.app/6GZ4yMmCzeyb9GJQgffWqW/"
SERVERCHAN_KEY = "SCT330705TA-151U7vBb7Y4QuvXLmVrSGvCz"

def test_bark():
    """测试Bark推送"""
    print("📱 测试 Bark 推送...")
    try:
        url = f"{BARK_URL}A股监控测试"
        params = {
            "body": "✅ A股打板监控系统已成功部署！\n\n📊 实时监控中...\n🔔 发现机会立即推送",
            "sound": "note"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ Bark 推送成功！")
            return True
        else:
            print(f"❌ Bark 推送失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Bark 异常: {e}")
        return False

def test_serverchan():
    """测试Server酱推送"""
    print("💬 测试 Server酱 推送...")
    try:
        url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
        data = {
            "title": "A股监控测试",
            "desp": "✅ Server酱推送通道正常！"
        }
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ Server酱 推送成功！")
            return True
        else:
            print(f"❌ Server酱 推送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ Server酱 异常: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 A股打板监控系统 - 推送测试")
    print("=" * 50)
    print()
    
    bark_ok = test_bark()
    print()
    server_ok = test_serverchan()
    
    print()
    print("=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    print(f"Bark:      {'✅ 成功' if bark_ok else '❌ 失败'}")
    print(f"Server酱:   {'✅ 成功' if server_ok else '❌ 失败'}")
    
    if bark_ok or server_ok:
        print()
        print("🎉 推送服务已就绪！")
        return 0
    else:
        print()
        print("⚠️ 推送服务异常，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
