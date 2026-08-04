"""Balanced High-Quality Option Selection Engine (v2)."""

from __future__ import annotations

import datetime as dt
import logging
import math
import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

MIN_TECHNICAL_CONFIDENCE = 75.0
HIGH_QUALITY_CONFIDENCE = 88.0
MIN_EFFECTIVENESS_SCORE = 85.0

MIN_VOLUME = 15
MIN_OPEN_INTEREST = 80

MAX_SPREAD_PCT = 0.16
MAX_SPREAD_RELAXED = 0.22

DELTA_SWEET_SPOT_LOW = 0.22
DELTA_SWEET_SPOT_HIGH = 0.68
DELTA_HARD_MIN = 0.08
DELTA_HARD_MAX = 0.92

MIN_PREMIUM = 0.03
MAX_PREMIUM_PCT_OF_SPOT = 0.50

MAX_PREFERRED_DTE = 7
MIN_SURVIVORS_BEFORE_RELAX = 3
NEAR_LEVEL_PROXIMITY_PCT = 0.012

TARGET1_CAPTURE = 0.55
TARGET2_CAPTURE = 0.90
STOP_CAPTURE = 0.40

FACTOR_LABELS_AR = {
    "technical": "توافق المؤشرات الفنية مع الاتجاه",
    "proximity": "قرب سعر التنفيذ من المستوى المناسب",
    "liquidity": "السيولة (حجم التداول والعقود المفتوحة)",
    "spread": "ضيق الفارق بين سعري العرض والطلب",
    "risk_reward": "نسبة المخاطرة إلى العائد",
    "delta": "دلتا العقد ضمن نطاق مناسب",
    "dte": "قرب تاريخ الانتهاء",
    "liquidity_conf": "ثقة بيانات السيولة",
}

_CONTRACT_SYMBOL_RE = re.compile(r"^[A-Z]+(\d{6})([CP])\d{8}$")
_last_no_trade_reason: str = ""


def get_last_no_trade_reason() -> str:
    return _last_no_trade_reason


def _set_no_trade_reason(reason: str) -> None:
   1) / (1 - stop_mult) if (1 - stop_mult) > 0 else 0.0
    return target1_mult, target2_mult, stop_mult, rr_ratio


def _apply_filters(df, proxy_spot, option_type, relaxed=False, expiration=None):
    option_type = (option_type or "").lower().strip()
    max_spread = MAX_SPREAD_RELAXED if relaxed else MAX_SPREAD_PCT
    kept = []
    for _, row in df.iterrows():
        strike = float(row.get("strike") or 0.0)
        bid = float(row.get("bid") or 0.0)
        ask = float(row.get("ask") or 0.0)
        last_price = float(row.get("lastPrice") or 0.0)
        volume = float(row.get("volume") or 0.0)
        open_interest = float(row.get("openInterest") or 0.0)
        contract_symbol = str(row.get("contractSymbol", ""))
        reasons = []
        if bid <= 0 or ask <= 0 or last_price <= 0:
            reasons.append("bad quote")
        if bid > 0 and ask > 0 and ask < bid:
            reasons.append("crossed market")
        mid = (bid + ask) / 2 if (bid > 0 and ask > 0) else 0.0
        spread_pct = ((ask - bid) / mid) if mid > 0 else 1.0
        if mid > 0 and (mid < MIN_PREMIUM or mid > proxy_spot * MAX_PREMIUM_PCT_OF_SPOT):
            reasons.append("unrealistic premium")
        if mid > 0 and spread_pct > max_spread:
            reasons.append(f"spread too wide ({spread_pct
