"""Industry classification heuristics."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Dict, List, Sequence

PRESET_SECTORS = [
    "区块链",
    "AI",
    "机器人",
    "自动驾驶",
    "数据中心",
    "半导体",
    "互联网",
    "基因编辑",
    "生物制药",
    "医疗健康",
]

_KEYWORD_MAP: Dict[str, Sequence[str]] = {
    "区块链": ("blockchain", "crypto", "web3", "bitcoin"),
    "AI": ("artificial intelligence", "machine learning", "ai", "deep learning"),
    "机器人": ("robot", "automation", "robotics"),
    "自动驾驶": ("autonomous", "self-driving", "autopilot"),
    "数据中心": ("data center", "cloud", "infrastructure", "colocation"),
    "半导体": ("semiconductor", "chip", "foundry", "wafer"),
    "互联网": ("internet", "software", "platform", "social"),
    "基因编辑": ("gene editing", "crispr"),
    "生物制药": ("biopharma", "biotechnology", "biopharmaceutical", "pharma", "drug"),
    "医疗健康": ("health", "medical", "healthcare", "diagnostic", "hospital"),
}

_FALLBACK_KEYWORDS: Dict[str, Sequence[str]] = {
    "能源": ("energy", "oil", "gas", "solar", "wind"),
    "金融": ("bank", "finance", "insurance", "broker"),
    "消费": ("retail", "consumer", "restaurant", "apparel"),
    "工业": ("manufacturing", "industrial", "aerospace", "defense"),
    "原材料": ("materials", "mining", "chemical", "steel"),
    "通信": ("telecom", "communication", "wireless"),
}


def _normalise(text: str | None) -> str:
    return text.lower() if text else ""


def classify_sectors(*descriptions: str | None) -> List[str]:
    """Infer sectors from free-form descriptions."""

    haystack = " ".join(filter(None, (_normalise(desc) for desc in descriptions)))
    sectors: set[str] = set()

    for sector, keywords in _KEYWORD_MAP.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", haystack) for keyword in keywords):
            sectors.add(sector)

    for sector, keywords in _FALLBACK_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            sectors.add(sector)

    if not sectors:
        sectors.add("其他")

    return sorted(sectors)


def merge_sector_lists(existing: Iterable[str], new: Iterable[str]) -> List[str]:
    """Merge sector names preserving uniqueness."""

    merged = {sector.strip() for sector in existing if sector}
    merged.update(sector.strip() for sector in new if sector)
    return sorted(merged)
