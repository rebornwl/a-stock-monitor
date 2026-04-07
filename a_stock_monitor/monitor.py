"""
A股打板监控系统 - 核心模块
专注龙头战法、打板机会、实时推送
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# ==================== 推送配置 ====================
BARK_URL = "https://api.day.app/6GZ4yMmCzeyb9GJQgffWqW/"
SERVERCHAN_KEY = "SCT330705TA-151U7vBb7Y4QuvXLmVrSGvCz"

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 推送服务 ====================
class PushService:
    """iPhone推送服务"""
    
    @staticmethod
    def send_bark(title: str, content: str, level: str = "🔔") -> bool:
        """通过Bark推送消息"""
        try:
            url = f"{BARK_URL}{title}"
            params = {
                "body": content,
                "sound": "alarm",
            }
            # 根据紧急程度设置不同的提醒音
            if level == "🔴":
                params["sound"] = "alarm"
            elif level == "🟠":
                params["sound"] = "birdsong"
            else:
                params["sound"] = "note"
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                logger.info(f"Bark推送成功: {title}")
                return True
            else:
                logger.error(f"Bark推送失败: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Bark推送异常: {e}")
            return False
    
    @staticmethod
    def send_serverchan(title: str, content: str) -> bool:
        """通过Server酱推送消息"""
        try:
            url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
            data = {
                "title": title,
                "desp": content
            }
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            if result.get("code") == 0:
                logger.info(f"Server酱推送成功: {title}")
                return True
            else:
                logger.error(f"Server酱推送失败: {result}")
                return False
        except Exception as e:
            logger.error(f"Server酱推送异常: {e}")
            return False
    
    @staticmethod
    def push_opportunity(stock_name: str, stock_code: str, reason: str, 
                         action: str, risk: str, level: str = "🟠") -> bool:
        """推送投资机会"""
        emoji = level
        title = f"{emoji}【打板机会】{stock_name}({stock_code})"
        content = f"""
📈 板块：{reason}
🎯 信号：涨停板
💡 建议：{action}
⚠️ 风险：{risk}
⏰ 时间：{datetime.now().strftime('%H:%M:%S')}
"""
        # 同时发送Bark和Server酱
        bark_ok = PushService.send_bark(title, content, level)
        server_ok = PushService.send_serverchan(title, content)
        return bark_ok or server_ok


# ==================== 市场数据获取 ====================
class MarketDataService:
    """市场数据服务"""
    
    # 使用东方财富免费API
    BASE_URL = "https://push2.eastmoney.com"
    
    @staticmethod
    def get_limit_up_stocks() -> List[Dict]:
        """获取涨停股票列表"""
        try:
            # 东方财富涨停榜API
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "cb": "jQuery",
                "pn": "1",
                "pz": "50",
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
                "_": "1625467890123"
            }
            headers = {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                # 解析JSONP
                json_str = text[7:-1] if text.startswith("jQuery") else text
                data = json.loads(json_str)
                stocks = data.get("data", {}).get("diff", [])
                
                limit_up_stocks = []
                for stock in stocks:
                    # 涨幅 >= 9.9% 视为涨停
                    if float(stock.get("f3", 0)) >= 9.9:
                        limit_up_stocks.append({
                            "code": stock.get("f12", ""),
                            "name": stock.get("f14", ""),
                            "change": stock.get("f3", 0),
                            "close": stock.get("f2", 0),
                            "volume": stock.get("f5", 0),
                            "amount": stock.get("f6", 0),
                        })
                return limit_up_stocks
            return []
        except Exception as e:
            logger.error(f"获取涨停股票失败: {e}")
            return []
    
    @staticmethod
    def get_market_sentiment() -> Dict:
        """获取市场情绪指标"""
        try:
            # 涨跌停统计
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": "1",
                "po": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f12,f14",
            }
            headers = {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": "Mozilla/5.0"
            }
            
            # 获取涨停数
            up_params = params.copy()
            up_params["fs"] = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
            up_params["fzds"] = "0"
            response_up = requests.get(url, params=up_params, headers=headers, timeout=10)
            
            # 获取跌停数
            down_params = params.copy()
            down_params["fs"] = "m:0+t:7,m:0+t:81,m:1+t:3,m:1+t:24"
            response_down = requests.get(url, params=down_params, headers=headers, timeout=10)
            
            # 获取大盘指数
            index_url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            index_params = {
                "fltt": "2",
                "invt": "2",
                "fields": "f1,f2,f3,f4,f12,f14",
                "secids": "1.000001,0.399001,0.399006",
            }
            response_index = requests.get(index_url, params=index_params, headers=headers, timeout=10)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "market_open": MarketDataService._is_market_open()
            }
        except Exception as e:
            logger.error(f"获取市场情绪失败: {e}")
            return {}
    
    @staticmethod
    def _is_market_open() -> bool:
        """判断当前是否开盘时间"""
        now = datetime.now()
        weekday = now.weekday()
        
        # 周一到周五，9:15-15:00
        if weekday >= 5:  # 周六周日
            return False
        
        hour = now.hour
        minute = now.minute
        
        if hour < 9 or hour >= 15:
            return False
        if hour == 9 and minute < 15:
            return False
        
        return True


# ==================== 龙头分析 ====================
class DragonAnalyzer:
    """龙头股分析器"""
    
    @staticmethod
    def analyze_limit_up_stocks(stocks: List[Dict]) -> Dict:
        """分析涨停股票，找出龙头"""
        if not stocks:
            return {
                "summary": "今日无涨停股票",
                "dragon_stocks": [],
                "opportunities": []
            }
        
        # 按成交量排序（成交量大=资金关注度高）
        sorted_stocks = sorted(stocks, key=lambda x: x.get("amount", 0), reverse=True)
        
        dragons = []
        for i, stock in enumerate(sorted_stocks[:5]):  # 取前5只
            dragons.append({
                "rank": i + 1,
                "code": stock.get("code", ""),
                "name": stock.get("name", ""),
                "change": f"+{stock.get('change', 0):.2f}%",
                "volume": DragonAnalyzer._format_amount(stock.get("amount", 0)),
            })
        
        return {
            "total_limit_up": len(stocks),
            "top_volume_stocks": dragons,
            "opportunities": DragonAnalyzer._generate_opportunities(dragons)
        }
    
    @staticmethod
    def _format_amount(amount: int) -> str:
        """格式化金额"""
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万"
        return str(amount)
    
    @staticmethod
    def _generate_opportunities(stocks: List[Dict]) -> List[Dict]:
        """生成机会列表"""
        opportunities = []
        for stock in stocks[:3]:  # 取前3只推荐
            opportunities.append({
                "name": stock["name"],
                "code": stock["code"],
                "action": "强势涨停，关注明日溢价",
                "risk": "高位风险，追涨需谨慎",
                "level": "🟠"
            })
        return opportunities


# ==================== 推送官 ====================
class PushOfficer:
    """推送官 - 负责推送决策"""
    
    def __init__(self):
        self.push_service = PushService()
        self.hourly_count = 0
        self.last_push_hour = None
    
    def should_push(self, content: str) -> bool:
        """判断是否应该推送（每小时最多3条）"""
        now = datetime.now()
        current_hour = now.hour
        
        # 新的一小时重置计数
        if self.last_push_hour != current_hour:
            self.hourly_count = 0
            self.last_push_hour = current_hour
        
        # 非交易时段不推送
        if not MarketDataService._is_market_open():
            logger.info("非交易时段，跳过推送")
            return False
        
        # 每小时限制3条
        if self.hourly_count >= 3:
            logger.warning("本小时推送已达上限(3条)")
            return False
        
        self.hourly_count += 1
        return True
    
    def push_opportunity(self, stock: Dict, reason: str = "强势涨停") -> bool:
        """推送投资机会"""
        if not self.should_push(f"机会推送: {stock['name']}"):
            return False
        
        return self.push_service.push_opportunity(
            stock_name=stock.get("name", ""),
            stock_code=stock.get("code", ""),
            reason=reason,
            action=stock.get("action", "强势涨停，关注"),
            risk=stock.get("risk", "追涨风险"),
            level=stock.get("level", "🟠")
        )
    
    def push_market_report(self, report: Dict) -> bool:
        """推送市场报告"""
        if not self.should_push("市场报告"):
            return False
        
        title = "📊 盘前/盘中市场报告"
        content = json.dumps(report, ensure_ascii=False, indent=2)
        return self.push_service.send_bark(title, content)


# ==================== 竞价阶段监控 ====================
class AuctionMonitor:
    """竞价阶段监控 - 9:15-9:25"""
    
    @staticmethod
    def is_auction_time() -> bool:
        """判断是否在竞价时段"""
        now = datetime.now()
        weekday = now.weekday()
        if weekday >= 5:
            return False
        hour = now.hour
        minute = now.minute
        return hour == 9 and 15 <= minute <= 24
    
    @staticmethod
    def is_auction_ending() -> bool:
        """判断是否即将结束竞价（9:24）"""
        now = datetime.now()
        weekday = now.weekday()
        if weekday >= 5:
            return False
        return now.hour == 9 and now.minute == 24
    
    @staticmethod
    def push_auction_warning() -> bool:
        """推送竞价即将结束警告"""
        try:
            # 获取竞价情况
            stocks = MarketDataService.get_limit_up_stocks()
            
            auction_stocks = [s for s in stocks if float(s.get("change", 0)) >= 9.9]
            
            title = "🚨 竞价即将结束！"
            content = f"""
竞价时间仅剩60秒！
涨停股数量：{len(auction_stocks)}只

"""
            if auction_stocks:
                content += "🔥 强势涨停：\n"
                for s in auction_stocks[:5]:
                    content += f"• {s.get('name', '-')} ({s.get('code', '-')}) +{s.get('change', 0):.1f}%\n"
            
            content += """
⏰ 9:25开盘后立即确认！
"""
            
            # 使用紧急推送
            PushService.send_bark(title, content, "🔴")
            PushService.send_serverchan(title, content)
            logger.info("竞价警告推送成功")
            return True
        except Exception as e:
            logger.error(f"竞价警告推送失败: {e}")
            return False
    
    @staticmethod
    def push_auction_summary() -> bool:
        """推送竞价阶段汇总"""
        try:
            stocks = MarketDataService.get_limit_up_stocks()
            
            title = "📊 竞价阶段汇总"
            content = f"""
竞价涨停：{len(stocks)}只

"""
            if stocks:
                content += "TOP 5：\n"
                sorted_stocks = sorted(stocks, key=lambda x: x.get("amount", 0), reverse=True)
                for i, s in enumerate(sorted_stocks[:5], 1):
                    content += f"{i}. {s.get('name', '-')} ({s.get('code', '-')})\n"
            
            PushService.send_bark(title, content, "🟠")
            return True
        except Exception as e:
            logger.error(f"竞价汇总推送失败: {e}")
            return False


# ==================== 复盘服务 ====================
class ReviewService:
    """每日盘后复盘"""
    
    @staticmethod
    def generate_daily_review(date: str = None) -> str:
        """生成每日复盘报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        review = f"""
# 📋 每日复盘报告
**日期：{date}**

## 一、今日市场概况
- 涨停家数：待统计
- 跌停家数：待统计
- 市场情绪：待评估

## 二、龙头股表现
待补充

## 三、打板机会回顾
待补充

## 四、明日展望
待补充

## 五、操作记录
| 时间 | 股票 | 操作 | 结果 |
|------|------|------|------|
| - | - | - | - |

---
*由A股打板监控系统自动生成*
"""
        return review
    
    @staticmethod
    def save_review(review: str, date: str = None) -> str:
        """保存复盘报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"reviews/{date}.md"
        try:
            import os
            os.makedirs("reviews", exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(review)
            return filename
        except Exception as e:
            logger.error(f"保存复盘失败: {e}")
            return ""


# ==================== 导入复盘模块 ====================
try:
    from review_generator import generate_review, save_review, push_review
except ImportError:
    pass

# ==================== 主程序 ====================
def main():
    """主程序入口"""
    import sys
    
    logger.info("=" * 50)
    logger.info("A股打板监控系统启动")
    logger.info("=" * 50)
    
    # 检查运行模式
    mode = sys.argv[1] if len(sys.argv) > 1 else "monitor"
    
    if mode == "review":
        # 运行复盘模式
        logger.info("运行模式：盘后复盘")
        review = generate_review()
        filename = save_review(review)
        push_review(review)
        print(review)
        print(f"\n复盘已保存: {filename}")
        return
    
    # 运行监控模式
    logger.info("运行模式：实时监控")
    
    # 检查竞价阶段
    if AuctionMonitor.is_auction_ending():
        logger.info("检测到竞价即将结束（9:24），推送警告...")
        AuctionMonitor.push_auction_warning()
    elif AuctionMonitor.is_auction_time():
        logger.info("竞价时段，发送竞价汇总...")
        AuctionMonitor.push_auction_summary()
    
    # 获取市场数据
    logger.info("正在获取涨停股票...")
    stocks = MarketDataService.get_limit_up_stocks()
    
    if stocks:
        logger.info(f"今日涨停股票: {len(stocks)}只")
        
        # 分析龙头
        analyzer = DragonAnalyzer()
        analysis = analyzer.analyze_limit_up_stocks(stocks)
        
        logger.info(f"龙头股分析: {json.dumps(analysis, ensure_ascii=False)}")
        
        # 推送机会
        push_officer = PushOfficer()
        for opp in analysis.get("opportunities", []):
            push_officer.push_opportunity(opp)
        
        print("\n" + "=" * 50)
        print("🔥 涨停股票 TOP 5（按成交量）")
        print("=" * 50)
        for stock in analysis.get("top_volume_stocks", []):
            print(f"{stock['rank']}. {stock['name']}({stock['code']}) - {stock['change']} - 成交: {stock['volume']}")
    else:
        logger.info("今日暂无涨停股票或获取失败")


if __name__ == "__main__":
    main()
