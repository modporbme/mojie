#!/usr/bin/env python3
"""Daily updater for README dates and random blank lines after invite-code headings."""

from __future__ import annotations

import random
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
ROOT = Path(__file__).resolve().parents[1]

# Eastern Arabic-Indic digits used in the Persian README
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

EN_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
RU_MONTHS_GEN = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]
FA_MONTHS = [
    "ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
    "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر",
]

FILES = [
    {
        "path": ROOT / "README.md",
        "heading": "## 魔戒机场邀请码",
        "date_patterns": [
            (re.compile(r"\d{4}年\d{1,2}月\d{1,2}日"), "zh"),
        ],
    },
    {
        "path": ROOT / "README_EN.md",
        "heading": "## Mojie Invite Code",
        "date_patterns": [
            (re.compile(
                r"Updated (?:January|February|March|April|May|June|July|"
                r"August|September|October|November|December) \d{1,2}, \d{4}"
            ), "en"),
        ],
    },
    {
        "path": ROOT / "README_RU.md",
        "heading": "## Пригласительный код Mojie",
        "date_patterns": [
            (re.compile(
                r"обновлено \d{1,2} (?:января|февраля|марта|апреля|мая|июня|"
                r"июля|августа|сентября|октября|ноября|декабря) \d{4}"
            ), "ru"),
        ],
    },
    {
        "path": ROOT / "README_FA.md",
        "heading": "## کد دعوت موجی",
        "date_patterns": [
            (re.compile(
                r"به‌روزرسانی [0-9۰-۹]{1,2} "
                r"(?:ژانویه|فوریه|مارس|آوریل|مه|ژوئن|ژوئیه|اوت|سپتامبر|اکتبر|نوامبر|دسامبر) "
                r"[0-9۰-۹]{4}"
            ), "fa"),
        ],
    },
]


def format_date(kind: str, now: datetime) -> str:
    y, m, d = now.year, now.month, now.day
    if kind == "zh":
        return f"{y}年{m}月{d}日"
    if kind == "en":
        return f"Updated {EN_MONTHS[m - 1]} {d}, {y}"
    if kind == "ru":
        return f"обновлено {d} {RU_MONTHS_GEN[m - 1]} {y}"
    if kind == "fa":
        text = f"به‌روزرسانی {d} {FA_MONTHS[m - 1]} {y}"
        return text.translate(FA_DIGITS)
    raise ValueError(kind)


def update_dates(text: str, patterns: list[tuple[re.Pattern, str]], now: datetime) -> str:
    for pattern, kind in patterns:
        replacement = format_date(kind, now)
        text = pattern.sub(replacement, text)
    return text


def tweak_blank_lines_after_heading(text: str, heading: str) -> str:
    lines = text.splitlines(keepends=True)
    idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\r\n") == heading:
            idx = i
            break
    if idx is None:
        print(f"warning: heading not found: {heading!r}")
        return text

    start = idx + 1
    end = start
    while end < len(lines) and lines[end].strip() == "":
        end += 1
    blank_count = end - start

    # Keep the file newline style of the heading line.
    nl = "\n"
    if lines[idx].endswith("\r\n"):
        nl = "\r\n"

    if blank_count == 0:
        new_count = random.randint(1, 3)
    else:
        if random.random() < 0.5:
            new_count = min(5, blank_count + random.randint(1, 2))
        else:
            new_count = max(0, blank_count - 1)
            if new_count == 0:
                new_count = random.randint(1, 3)

    new_blanks = [nl] * new_count
    lines[start:end] = new_blanks
    print(f"  {heading!r}: blank lines {blank_count} -> {new_count}")
    return "".join(lines)


def main() -> None:
    now = datetime.now(TZ)
    print(f"Updating READMEs for {now.date().isoformat()} ({TZ.key})")
    random.seed()

    for spec in FILES:
        path: Path = spec["path"]
        if not path.exists():
            print(f"skip missing file: {path}")
            continue
        original = path.read_text(encoding="utf-8")
        updated = update_dates(original, spec["date_patterns"], now)
        updated = tweak_blank_lines_after_heading(updated, spec["heading"])
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"wrote {path.name}")
        else:
            print(f"unchanged {path.name}")


if __name__ == "__main__":
    main()
