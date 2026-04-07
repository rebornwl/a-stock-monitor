"""
增强版复盘生成器 v2.0
"""

import json
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


def generate_review(date: str = None) -> str:
    """生成每日复盘报告"""
    # 导入需要的数据服务
    try:
        from monitor_v2 import MarketDataService, DragonAnalyzer, SectorAnalyzer, SentimentAnalyzer, PushService
    except ImportError:
        from monitor import MarketDataService, DragonAnalyzer, MarketDataService as MDS

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
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

        review = _build_review_markdown(date, limit_up, limit_down, indices,
                                        sentiment, sector_analysis, dragon_analysis)
        return review
    except Exception as e:
        logger.error(f"生成复盘失败: {e}")
        return f"# 复盘生成失败\n\n错误: {e}"


def _build_review_markdown(date: str, limit_up: List, limit_down: List, indices: Dict,
                           sentiment: Dict, sector_analysis: Dict, dragon_analysis: Dict) -> str:
    """构建Markdown格式的复盘报告"""
    def format_amount(amount: int) -> str:
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万"
        return str(amount)

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

    review += f"""
---

## 四、连板股分析
"""
    consecutive = DragonAnalyzer.analyze_consecutive_boards(limit_up)
    if consecutive.get("consecutive_boards"):
        for s in consecutive["consecutive_boards"]:
            review += f"- **{s['name']}** ({s['code']}) +{s['change']:.1f}%\n"
    else:
        review += "- 暂无明显连板股\n"

    review += f"""
---

## 五、明日展望

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


def save_review(review: str, date: str = None) -> str:
    """保存复盘报告"""
    import os
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    os.makedirs("reviews", exist_ok=True)
    filename = f"reviews/{date}.md"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(review)
        return filename
    except Exception as e:
        logger.error(f"保存复盘失败: {e}")
        return ""


def push_review(review: str) -> bool:
    """推送复盘报告"""
    try:
        from monitor_v2 import PushService
    except ImportError:
        return False

    lines = review.split("\n")
    summary = "\n".join(lines[:15])  # 取前15行作为摘要

    title = "📋 今日复盘报告"
    PushService.send_bark(title, summary[:500], "🟠")
    PushService.send_serverchan(title, summary[:1000])
    return True


if __name__ == "__main__":
    review = generate_review()
    filename = save_review(review)
    push_review(review)
    print(review)
    print(f"\n复盘已保存: {filename}")
