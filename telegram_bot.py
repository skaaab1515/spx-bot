

from __future__ import annotations

import logging
import os
from datetime import datetime

import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from analysis_balanced import (
    analyze_technicals,
    select_best_contract,
    get_last_no_trade_reason,
    compute_technical_confidence,
    classify_technical_quality,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8876216753:AAHjfByuMl9XQjTt-SyN70J5CArQp4gB6RI")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_analysis(force_type: str | None = None) -> str:
    symbol = "^SPX"
    price_symbol = "^GSPC"
    lines: list[str] = []
    lines.append("📊 تحليل SPX")
    lines.append(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    try:
        price_ticker = yf.Ticker(price_symbol)
        history = price_ticker.history(period="6mo", interval="1d")
        if history.empty:
            history = yf.Ticker(symbol).history(period="6mo", interval="1d")
        if history.empty:
            return "❌ فشل جلب البيانات التاريخية لـ SPX."
        ticker = yf.Ticker(symbol)
    except
