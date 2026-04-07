"""
A股打板监控系统 - 增强版 v2.0
新增：热点板块分析、板块轮动监控、连板统计
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
            logger.error(f"Server酱异常: {e}")
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
        bark_ok = PushService.send_bark(title, content, level)
        server_ok = PushService.send_serverchan(title, content)
        return bark_ok or server_ok

    @staticmethod
    def push_sector_alert(sector_name: str, stocks: List[Dict], reason: str = "") -> bool:
        """推送板块异动预警"""
        title = f"🔥【板块异动】{sector_name}"
        content = f"涨停个股：{len(stocks)}只\n\n"
        for s in stocks[:5]:
            content += f"• {s.get('name', '-')} ({s.get('code', '-')}) +{s.get('change', 0):.1f}%\n"
        if reason:
            content += f"\n📌 {reason}"

        PushService.send_bark(title, content, "🔴")
        PushService.send_serverchan(title, content)
        return True


# ==================== 市场数据获取 ====================
class MarketDataService:
    """市场数据服务"""

    BASE_URL = "https://push2.eastmoney.com"

    @staticmethod
    def get_limit_up_stocks() -> List[Dict]:
        """获取涨停股票列表"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 100,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
            }
            headers = {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stocks = data.get("data", {}).get("diff", [])

                limit_up_stocks = []
                for stock in stocks:
                    if float(stock.get("f3", 0)) >= 9.9:
                        limit_up_stocks.append({
                            "code": stock.get("f12", ""),
                            "name": stock.get("f14", ""),
                            "change": stock.get("f3", 0),
                            "close": stock.get("f2", 0),
                            "volume": stock.get("f5", 0),
                            "amount": stock.get("f6", 0),
                            "sector": stock.get("f100", "未知"),  # 板块信息
                        })
                return limit_up_stocks
            return []
        except Exception as e:
            logger.error(f"获取涨停股票失败: {e}")
            return []

    @staticmethod
    def get_limit_down_stocks() -> List[Dict]:
        """获取跌停股票列表"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 50,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f3",
                "fs": "m:0+t:7,m:0+t:81,m:1+t:3,m:1+t:24",
                "fields": "f1,f2,f3,f12,f13,f14",
            }
            headers = {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stocks = data.get("data", {}).get("diff", [])

                limit_down_stocks = []
                for stock in stocks:
                    if float(stock.get("f3", 0)) <= -9.9:
                        limit_down_stocks.append({
                            "code": stock.get("f12", ""),
                            "name": stock.get("f14", ""),
                            "change": stock.get("f3", 0),
                        })
                return limit_down_stocks
            return []
        except Exception as e:
            logger.error(f"获取跌停股票失败: {e}")
            return []

    @staticmethod
    def get_sector_leaders() -> List[Dict]:
        """获取板块涨跌榜（涨幅前20）"""
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 20,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f4",
                "fs": "m:90+t:3,m:90+t:4,m:90+t:5,m:90+t:6,m:90+t:7,m:90+t:8,m:90+t:9,m:90+t:10,m:90+t:11,m:90+t:12,m:90+t:13,m:90+t:14,m:90+t:15,m:90+t:16,m:90+t:17,m:90+t:18",
                "fields": "f2,f3,f12,f14,f20,f62",
            }
            headers = {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                sectors = data.get("data", {}).get("diff", [])

                leaders = []
                for s in sectors:
                    leaders.append({
                        "name": s.get("f14", "未知"),
                        "change": s.get("f3", 0),
                        "lead_stock": s.get("f20", ""),  # 龙头股
                    })
                return leaders
            return []
        except Exception as e:
            logger.error(f"获取板块榜失败: {e}")
            return []

    @staticmethod
    def get_market_index() -> Dict:
        """获取大盘指数"""
        try:
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "invt": 2,
                "fields": "f1,f2,f3,f4,f12,f14",
                "secids": "1.000001,0.399001,0.399006",
            }
            headers = {
                "Referer": "https://quote.eastmoney.com/",
                "User-Agent": "Mozilla/5.0"
            }
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                indices = data.get("data", {}).get("diff", [])

                result = {}
                name_map = {"000001": "上证指数", "399001": "深证成指", "399006": "创业板"}
                for idx in indices:
                    code = idx.get("f12", "")
                    name = name_map.get(code, code)
                    result[code] = {
                        "name": name,
                        "price": idx.get("f2", 0),
                        "change": idx.get("f3", 0),
                        "volume": idx.get("f5", 0),
                    }
                return result
            return {}
        except Exception as e:
            logger.error(f"获取指数失败: {e}")
            return {}

    @staticmethod
    def _is_market_open() -> bool:
        """判断当前是否开盘时间"""
        now = datetime.now()
        weekday = now.weekday()
        if weekday >= 5:
            return False
        hour = now.hour
        minute = now.minute
        if hour < 9 or hour >= 15:
            return False
        if hour == 9 and minute < 15:
            return False
        return True


# ==================== 热点板块分析 ====================
class SectorAnalyzer:
    """热点板块分析器"""

    # 常见板块关键词映射
    SECTOR_KEYWORDS = {
        "AI": ["人工智能", "ChatGPT", "AIGC", "大模型"],
        "芯片": ["半导体", "芯片", "集成电路", "光刻"],
        "新能源": ["锂电池", "储能", "光伏", "风电", "新能源汽车"],
        "医药": ["生物医药", "医疗器械", "中药", "创新药"],
        "军工": ["国防军工", "航天航空", "船舶"],
        "数字经济": ["数字货币", "数据要素", "信创", "软件"],
        "消费": ["食品饮料", "白酒", "旅游", "零售"],
    }

    @staticmethod
    def analyze_hot_sectors(stocks: List[Dict]) -> Dict:
        """分析热点板块"""
        if not stocks:
            return {"hot_sectors": [], "summary": "暂无涨停股"}

        # 按涨停股数量统计板块
        sector_count = {}
        for stock in stocks:
            name = stock.get("name", "")
            # 简单关键词匹配（实际应该用API获取真实板块）
            sector = SectorAnalyzer._guess_sector(name)
            if sector not in sector_count:
                sector_count[sector] = {"count": 0, "stocks": [], "total_amount": 0}
            sector_count[sector]["count"] += 1
            sector_count[sector]["stocks"].append(stock)
            sector_count[sector]["total_amount"] += stock.get("amount", 0)

        # 排序
        sorted_sectors = sorted(
            sector_count.items(),
            key=lambda x: (x[1]["count"], x[1]["total_amount"]),
            reverse=True
        )

        hot_sectors = []
        for sector, data in sorted_sectors[:5]:
            stocks_sorted = sorted(data["stocks"], key=lambda x: x.get("amount", 0), reverse=True)
            hot_sectors.append({
                "name": sector,
                "count": data["count"],
                "total_amount": SectorAnalyzer._format_amount(data["total_amount"]),
                "leader_stock": stocks_sorted[0] if stocks_sorted else {},
                "all_stocks": stocks_sorted[:5],
            })

        return {
            "hot_sectors": hot_sectors,
            "total_sectors": len(sector_count),
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

    @staticmethod
    def _guess_sector(stock_name: str) -> str:
        """根据股票名称猜测板块（简化版）"""
        for sector, keywords in SectorAnalyzer.SECTOR_KEYWORDS.items():
            for kw in keywords:
                if kw in stock_name:
                    return sector
        return "其他"

    @staticmethod
    def _format_amount(amount: int) -> str:
        """格式化金额"""
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万"
        return str(amount)


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

        # 按成交量排序
        sorted_stocks = sorted(stocks, key=lambda x: x.get("amount", 0), reverse=True)

        dragons = []
        for i, stock in enumerate(sorted_stocks[:10]):
            dragons.append({
                "rank": i + 1,
                "code": stock.get("code", ""),
                "name": stock.get("name", ""),
                "change": f"+{stock.get('change', 0):.2f}%",
                "amount": DragonAnalyzer._format_amount(stock.get("amount", 0)),
            })

        opportunities = []
        for stock in sorted_stocks[:3]:
            opportunities.append({
                "name": stock.get("name", ""),
                "code": stock.get("code", ""),
                "action": "强势涨停，关注明日溢价",
                "risk": "高位风险，追涨需谨慎",
                "level": "🟠"
            })

        return {
            "total_limit_up": len(stocks),
            "top_volume_stocks": dragons,
            "opportunities": opportunities,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

    @staticmethod
    def analyze_consecutive_boards(stocks: List[Dict]) -> Dict:
        """分析连板股票"""
        # 简化版：按名称关键词识别（实际需要历史数据）
        consecutive = []
        for stock in stocks:
            name = stock.get("name", "")
            # 识别可能的连板股（名称中含特定字）
            if any(kw in name for kw in ["药业", "科技", "股份", "集团"]):
                consecutive.append({
                    "code": stock.get("code", ""),
                    "name": name,
                    "change": stock.get("change", 0),
                    "amount": DragonAnalyzer._format_amount(stock.get("amount", 0)),
                })

        return {
            "consecutive_boards": consecutive[:5],
            "count": len(consecutive),
        }

    @staticmethod
    def _format_amount(amount: int) -> str:
        """格式化金额"""
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万"
        return str(amount)


# ==================== 市场情绪分析 ====================
class SentimentAnalyzer:
    """市场情绪分析器"""

    @staticmethod
    def analyze_sentiment(limit_up: int, limit_down: int, indices: Dict) -> Dict:
        """分析市场情绪"""
        # 计算涨跌停比
        up_down_ratio = limit_up / max(limit_down, 1)

        # 计算指数平均涨跌
        avg_change = 0
        if indices:
            changes = [idx.get("change", 0) for idx in indices.values()]
            avg_change = sum(changes) / len(changes) if changes else 0

        # 情绪判定
        if avg_change > 1.5 and up_down_ratio > 3:
            sentiment = "极度亢奋"
            level = "🔴"
        elif avg_change > 0.5 and up_down_ratio > 2:
            sentiment = "偏强"
            level = "🟢"
        elif avg_change > -0.5:
            sentiment = "中性"
            level = "🟡"
        elif avg_change > -1.5:
            sentiment = "偏弱"
            level = "🟠"
        else:
            sentiment = "极度低迷"
            level = "🔴"

        return {
            "sentiment": sentiment,
            "level": level,
            "up_down_ratio": round(up_down_ratio, 2),
            "avg_change": round(avg_change, 2),
            "limit_up": limit_up,
            "limit_down": limit_down,
        }


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

        if self.last_push_hour != current_hour:
            self.hourly_count = 0
            self.last_push_hour = current_hour

        if not MarketDataService._is_market_open():
            return False

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

    def push_sector_alert(self, sector_name: str, stocks: List[Dict], reason: str = "") -> bool:
        """推送板块异动预警"""
        if not self.should_push(f"板块预警: {sector_name}"):
            return False

        return self.push_service.push_sector_alert(sector_name, stocks, reason)

    def push_market_report(self, report: Dict) -> bool:
        """推送市场报告"""
        if not self.should_push("市场报告"):
            return False

        title = "📊 盘中市场报告"
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


# ==================== 增强版复盘服务 ====================
class ReviewService:
    """每日盘后复盘 - 增强版"""

    @staticmethod
    def generate_daily_review(date: str = None) -> str:
        """生成每日复盘报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # 获取数据
        limit_up = MarketDataService.get_limit_up_stocks()
        limit_down = MarketDataService.get_limit_down_stocks()
        indices = MarketDataService.get_market_index()

        # 分析
        dragon_analyzer = DragonAnalyzer()
        sector_analyzer = SectorAnalyzer()
        sentiment = SentimentAnalyzer.analyze_sentiment(len(limit_up), len(limit_down), indices)
        sector_analysis = sector_analyzer.analyze_hot_sectors(limit_up)
        dragon_analysis = dragon_analyzer.analyze_limit_up_stocks(limit_up)

        review = f"""# 📋 每日复盘报告
**日期：{date}**
**生成时间：{datetime.now().strftime('%H:%M:%S')}**

---

## 一、市场概况

| 指标 | 数值 |
|------|------|
| 涨停家数 | {len(limit_up)} |
| 跌停家数 | {len(limit_down)} |
| 涨跌停比 | {sentiment['up_down_ratio']} |
| 市场情绪 | {sentiment['level']} {sentiment['sentiment']} |

### 大盘指数
"""
        for code, idx in indices.items():
            emoji = "🟢" if idx.get("change", 0) >= 0 else "🔴"
            review += f"- **{idx['name']}**: {emoji} {idx.get('change', 0):.2f}%\n"

        review += f"""
---

## 二、热点板块

| 排名 | 板块 | 涨停数 | 成交额 |
|------|------|--------|--------|
"""
        for i, sector in enumerate(sector_analysis.get("hot_sectors", [])[:5], 1):
            review += f"| {i} | {sector['name']} | {sector['count']} | {sector['total_amount']} |\n"

        review += """
---

## 三、龙头股 TOP 10

| 排名 | 股票 | 代码 | 涨幅 | 成交额 |
|------|------|------|------|--------|
"""
        for stock in dragon_analysis.get("top_volume_stocks", [])[:10]:
            review += f"| {stock['rank']} | {stock['name']} | {stock['code']} | {stock['change']} | {stock['amount']} |\n"

        review += """
---

## 四、连板股分析
"""
        consecutive = dragon_analyzer.analyze_consecutive_boards(limit_up)
        if consecutive["consecutive_boards"]:
            for s in consecutive["consecutive_boards"]:
                review += f"- **{s['name']}** ({s['code']}) +{s['change']:.1f}%\n"
        else:
            review += "- 暂无明显连板股\n"

        review += f"""
---

## 五、打板机会回顾

### 今日涨停股板块分布
"""
        if sector_analysis.get("hot_sectors"):
            for sector in sector_analysis["hot_sectors"][:3]:
                review += f"**{sector['name']}** 板块涨停 {sector['count']} 只\n"
                for s in sector["all_stocks"][:3]:
                    review += f"  - {s.get('name', '-')} ({s.get('code', '-')})\n"

        review += f"""
---

## 六、明日展望

### 🎯 重点关注方向
"""
        if sector_analysis.get("hot_sectors"):
            top_sector = sector_analysis["hot_sectors"][0]
            review += f"1. **{top_sector['name']}** 板块持续性（{top_sector['count']}只涨停）\n"
        review += "2. 龙头股溢价开盘情况\n"
        review += "3. 竞价阶段强势股\n"

        review += f"""
### ⚠️ 风险提示
- 涨停家数 {len(limit_up)} {'偏多，注意分化' if len(limit_up) > 50 else '正常范围'}
- 跌停家数 {len(limit_down)} {'需警惕' if len(limit_down) > 10 else '正常'}
- 情绪指示：{sentiment['sentiment']}

---
*由A股打板监控系统 v2.0 自动生成*
"""

        return review

    @staticmethod
    def save_review(review: str, date: str = None) -> str:
        """保存复盘报告"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        import os
        os.makedirs("reviews", exist_ok=True)
        filename = f"reviews/{date}.md"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(review)
            return filename
        except Exception as e:
            logger.error(f"保存复盘失败: {e}")
            return ""

    @staticmethod
    def push_review(review: str) -> bool:
        """推送复盘报告摘要"""
        lines = review.split("\n")
        summary = "\n".join(lines[:20])  # 取前20行作为摘要

        title = "📋 今日复盘报告"
        PushService.send_bark(title, summary[:500], "🟠")
        PushService.send_serverchan(title, summary[:1000])
        return True


# ==================== 实时数据服务（供网页端使用） ====================
class DataService:
    """实时数据服务 - 生成JSON供网页端使用"""

    @staticmethod
    def get_realtime_data() -> Dict:
        """获取实时数据 - 字段与网页index.html完全匹配"""
        limit_up = MarketDataService.get_limit_up_stocks()
        limit_down = MarketDataService.get_limit_down_stocks()
        indices_dict = MarketDataService.get_market_index()

        dragon_analyzer = DragonAnalyzer()
        sector_analyzer = SectorAnalyzer()

        sentiment_data = SentimentAnalyzer.analyze_sentiment(len(limit_up), len(limit_down), indices_dict)
        sector_analysis = sector_analyzer.analyze_hot_sectors(limit_up)
        dragon_analysis = dragon_analyzer.analyze_limit_up_stocks(limit_up)

        # 将 indices dict 转成 list（网页期望的格式）
        indices_list = []
        for code, idx in indices_dict.items():
            indices_list.append({
                "name": idx.get("name", ""),
                "price": str(idx.get("price", "--")),
                "change": float(idx.get("change", 0)),
            })

        # 将 hot_sectors 中的 leader_stock/all_stocks 字段移除（网页不需要）
        hot_sectors = []
        for s in sector_analysis.get("hot_sectors", []):
            hot_sectors.append({
                "name": s.get("name", "--"),
                "count": s.get("count", 0),
                "total_amount": s.get("total_amount", "--"),
            })

        # dragon_stocks 字段对齐
        dragon_stocks = []
        for s in dragon_analysis.get("top_volume_stocks", []):
            dragon_stocks.append({
                "name": s.get("name", "--"),
                "code": s.get("code", "--"),
                "change": s.get("change", "--"),
                "amount": s.get("amount", "--"),
            })

        # opportunities 字段对齐
        opportunities = []
        for o in dragon_analysis.get("opportunities", []):
            opportunities.append({
                "name": "打板机会",
                "stock": f"{o.get('name', '--')} {o.get('code', '')}",
                "entry": o.get("action", "--"),
                "risk": "高",
                "potential": "涨停溢价",
            })

        is_open = MarketDataService._is_market_open()
        return {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "market_status": "盘中" if is_open else "休市",
            "sentiment": sentiment_data.get("sentiment", "--"),
            "limit_up_count": len(limit_up),
            "limit_down_count": len(limit_down),
            "indices": indices_list,
            "hot_sectors": hot_sectors,
            "dragon_stocks": dragon_stocks,
            "opportunities": opportunities,
        }

    @staticmethod
    def save_realtime_data():
        """保存实时数据到JSON文件（供网页端读取）"""
        import os
        data = DataService.get_realtime_data()

        # 同时保存到 output/ 和 docs/data/ 两个位置
        os.makedirs("output", exist_ok=True)
        os.makedirs("docs/data", exist_ok=True)

        with open("output/realtime.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        with open("docs/data/realtime.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"数据已保存: output/realtime.json 和 docs/data/realtime.json")
        return data


# ==================== 主程序 ====================
def main():
    """主程序入口"""
    import sys
    import argparse

    logger.info("=" * 50)
    logger.info("A股打板监控系统 v2.0 启动")
    logger.info("=" * 50)

    # 支持两种格式：python monitor_v2.py --mode data / python monitor_v2.py data
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=None)
    parser.add_argument("positional_mode", nargs="?", default=None)
    args, _ = parser.parse_known_args()
    mode = args.mode or args.positional_mode or "monitor"
    logger.info(f"运行模式: {mode}")

    if mode == "review":
        # 复盘模式
        logger.info("运行模式：盘后复盘")
        review = ReviewService.generate_daily_review()
        filename = ReviewService.save_review(review)
        ReviewService.push_review(review)
        print(review)
        print(f"\n复盘已保存: {filename}")
        return

    if mode == "data":
        # 数据模式 - 生成JSON供网页端
        logger.info("运行模式：生成实时数据")
        data = DataService.save_realtime_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    # 监控模式
    logger.info("运行模式：实时监控")

    # 检查竞价阶段
    if AuctionMonitor.is_auction_ending():
        logger.info("检测到竞价即将结束（9:24），推送警告...")
        AuctionMonitor.push_auction_warning()
    elif AuctionMonitor.is_auction_time():
        logger.info("竞价时段，发送竞价汇总...")
        AuctionMonitor.push_auction_summary()

    # 获取市场数据
    logger.info("正在获取市场数据...")
    limit_up = MarketDataService.get_limit_up_stocks()
    limit_down = MarketDataService.get_limit_down_stocks()
    indices = MarketDataService.get_market_index()

    logger.info(f"涨停: {len(limit_up)} | 跌停: {len(limit_down)}")

    # 分析
    dragon_analyzer = DragonAnalyzer()
    sector_analyzer = SectorAnalyzer()
    sentiment = SentimentAnalyzer.analyze_sentiment(len(limit_up), len(limit_down), indices)
    sector_analysis = sector_analyzer.analyze_hot_sectors(limit_up)
    dragon_analysis = dragon_analyzer.analyze_limit_up_stocks(limit_up)

    # 输出报告
    print("\n" + "=" * 60)
    print(f"📊 市场情绪: {sentiment['level']} {sentiment['sentiment']}")
    print(f"📈 涨停: {len(limit_up)} | 跌停: {len(limit_down)} | 涨跌停比: {sentiment['up_down_ratio']}")
    print("=" * 60)

    print("\n🔥 热点板块 TOP 5")
    print("-" * 40)
    for i, sector in enumerate(sector_analysis.get("hot_sectors", [])[:5], 1):
        print(f"{i}. {sector['name']} ({sector['count']}只) - {sector['total_amount']}")

    print("\n🐉 龙头股 TOP 10（按成交额）")
    print("-" * 40)
    for stock in dragon_analysis.get("top_volume_stocks", [])[:10]:
        print(f"{stock['rank']:2}. {stock['name']}({stock['code']}) {stock['change']} {stock['amount']}")

    # 保存实时数据（monitor模式也同步更新网页数据）
    DataService.save_realtime_data()
    logger.info("实时数据已同步到 docs/data/realtime.json")

    # 推送机会
    push_officer = PushOfficer()
    for opp in dragon_analysis.get("opportunities", []):
        push_officer.push_opportunity(opp)


if __name__ == "__main__":
    main()
