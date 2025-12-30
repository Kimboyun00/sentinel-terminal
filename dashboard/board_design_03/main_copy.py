import random
import threading
import time
import textwrap
from datetime import datetime, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# 위기경보 단계
LEVEL_INTEREST = "관심"
LEVEL_CAUTION = "주의"
LEVEL_ALERT = "경계"
LEVEL_SEVERE = "심각"

THEMES = {
    LEVEL_INTEREST: {"accent": "#1f6feb", "bg": "#0d2345"},
    LEVEL_CAUTION: {"accent": "#f6a04d", "bg": "#422b0f"},
    LEVEL_ALERT: {"accent": "#e67e22", "bg": "#3a220e"},
    LEVEL_SEVERE: {"accent": "#e74c3c", "bg": "#3a0e0e"},
}

BANNER_EN = {
    "NORMAL": [
        "███╗   ██╗ ██████╗ ██████╗ ███╗   ███╗  █████╗ ██╗     ",
        "████╗  ██║██╔═══██╗██╔══██╗████╗ ████║ ██╔══██╗██║     ",
        "██╔██╗ ██║██║   ██║██████╔╝██╔████╔██║ ███████║██║     ",
        "██║╚██╗██║██║   ██║██╔══██╗██║╚██╔╝██║ ██╔══██║██║     ",
        "██║ ╚████║╚██████╔╝██║  ██║██║ ╚═╝ ██║ ██║  ██║███████╗",
        "╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═╝  ╚═╝╚══════╝",
    ],
    "ATTENTION": [
        " █████╗ ████████╗████████╗███████╗███╗   ██╗████████╗██╗ █████╗ ███╗   ██╗",
        "██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝████╗  ██║╚══██╔══╝██║██╔══██╗████╗  ██║",
        "███████║   ██║      ██║   █████╗  ██╔██╗ ██║   ██║   ██║██║  ██║██╔██╗ ██║",
        "██╔══██║   ██║      ██║   ██╔══╝  ██║╚██╗██║   ██║   ██║██║  ██║██║╚██╗██║",
        "██║  ██║   ██║      ██║   ███████╗██║ ╚████║   ██║   ██║╚█████╔╝██║ ╚████║",
        "╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚════╝ ╚═╝  ╚═══╝",
    ],
    "CAUTION": [
        " ██████╗ █████╗ ██╗   ██╗████████╗██╗ ██████╗ ███╗   ██╗",
        "██╔════╝██╔══██╗██║   ██║╚══██╔══╝██║██╔═══██╗████╗  ██║",
        "██║     ███████║██║   ██║   ██║   ██║██║   ██║██╔██╗ ██║",
        "██║     ██╔══██║██║   ██║   ██║   ██║██║   ██║██║╚██╗██║",
        "╚██████╗██║  ██║╚██████╔╝   ██║   ██║╚██████╔╝██║ ╚████║",
        " ╚═════╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝",
    ],
    "WARNING": [
        "██╗    ██╗ █████╗ ██████╗ ███╗   ██╗██╗███╗   ██╗ ██████╗ ",
        "██║    ██║██╔══██╗██╔══██╗████╗  ██║██║████╗  ██║██╔════╝ ",
        "██║ █╗ ██║███████║██████╔╝██╔██╗ ██║██║██╔██╗ ██║██║  ███╗",
        "██║███╗██║██╔══██║██╔══██╗██║╚██╗██║██║██║╚██╗██║██║   ██║",
        "╚███╔███╔╝██║  ██║██║  ██║██║ ╚████║██║██║ ╚████║╚██████╔╝",
        " ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ",
    ],
    "CRISIS": [
        " ██████╗██████╗ ██╗███████╗██╗███████╗",
        "██╔════╝██╔══██╗██║██╔════╝██║██╔════╝",
        "██║     ██████╔╝██║███████╗██║███████╗",
        "██║     ██╔══██╗██║╚════██║██║╚════██║",
        "╚██████╗██║  ██║██║███████║██║███████║",
        " ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚══════╝",
    ],
}

BANNER_KO = {
    "NORMAL": "Normal",
    "ATTENTION": "Attention",
    "CAUTION": "Caution",
    "WARNING": "Warning",
    "CRISIS": "Crisis",
}

NOTICE_IT = [
    "  ██╗████████╗     ███████╗███████╗██████╗ ██╗   ██╗██╗ ██████╗███████╗███████╗      ██████╗ ███████╗███████╗██╗ ██████╗███████╗                          ███╗      ",
    "  ██║╚══██╔══╝     ██╔════╝██╔════╝██╔══██╗██║   ██║██║██╔════╝██╔════╝██╔════╝     ██╔═══██╗██╔════╝██╔════╝██║██╔════╝██╔════╝                          ██████╗   ",
    "  ██║   ██║        ███████╗█████╗  ██████╔╝██║   ██║██║██║     █████╗  ███████╗     ██║   ██║█████╗  █████╗  ██║██║     █████╗     ████████████████████████████████╗",
    "  ██║   ██║        ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██║██║     ██╔══╝  ╚════██║     ██║   ██║██╔══╝  ██╔══╝  ██║██║     ██╔══╝     ╚══════════════════════██████╔══╝",
    "  ██║   ██║        ███████║███████╗██║  ██║ ╚████╔╝ ██║╚██████╗███████╗███████║     ╚██████╔╝██║     ██║     ██║╚██████╗███████╗                          ███╔══╝   ",
    "  ╚═╝   ╚═╝        ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝ ╚═════╝╚══════╝╚══════╝      ╚═════╝ ╚═╝     ╚═╝     ╚═╝ ╚═════╝╚══════╝                          ╚══╝      ",
]

ALERT_THEMES = {
    "NORMAL": {"accent": "#00B15E", "bg": "#0d2345"},
    "ATTENTION": {"accent": "#1f6feb", "bg": "#0d2345"},
    "CAUTION": {"accent": "#f6a04d", "bg": "#422b0f"},
    "WARNING": {"accent": "#e67e22", "bg": "#3a220e"},
    "CRISIS": {"accent": "#e74c3c", "bg": "#3a0e0e"},
}

LEVEL_TOKEN_MAP = {
    "NORMAL": ["normal", "정상"],
    "ATTENTION": ["attention", "관심"],
    "CAUTION": ["caution", "주의"],
    "WARNING": ["warning", "경계"],
    "CRISIS": ["crisis", "심각"],
}


# 대형 로고
LOGO_MAIN = [
    "██╗  ██╗██████╗ ██╗    ███████╗ ██████╗██╗  ██╗ ██████╗  ██████╗ ██╗     ",
    "██║ ██╔╝██╔══██╗██║    ██╔════╝██╔════╝██║  ██║██╔═══██╗██╔═══██╗██║     ",
    "█████╔╝ ██║  ██║██║    ███████╗██║     ███████║██║   ██║██║   ██║██║     ",
    "██╔═██╗ ██║  ██║██║    ╚════██║██║     ██╔══██║██║   ██║██║   ██║██║     ",
    "██║  ██╗██████╔╝██║    ███████║╚██████╗██║  ██║╚██████╔╝╚██████╔╝███████╗",
    "╚═╝  ╚═╝╚═════╝ ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝",
]

LOGO_SUB = [
    "╔═══════════════════════════════════════════════════════════════════════════════╗",
    "║ ██████╗  █████╗ ████████╗ █████╗    ██╗  ██╗███╗   ██╗██╗████████╗   ██████╗  ║",
    "║ ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗   ██║  ██║████╗  ██║██║╚══██╔══╝   ╚════██╗ ║",
    "║ ██║  ██║███████║   ██║   ███████║   ██║  ██║██╔██╗ ██║██║   ██║       █████╔╝ ║",
    "║ ██║  ██║██╔══██║   ██║   ██╔══██║   ██║  ██║██║╚██╗██║██║   ██║      ██╔═══╝  ║",
    "║ ██████╔╝██║  ██║   ██║   ██║  ██║   ╚█████╔╝██║ ╚████║██║   ██║      ███████╗ ║",
    "║ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝    ╚════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝      ╚══════╝ ║",
    "╚═══════════════════════════════════════════════════════════════════════════════╝",
]


class WeatherService:
    """Background updater for weather."""

    def __init__(self, city: str, interval: int = 120):
        self.city = city
        self.interval = interval
        self.condition = "Clear"
        self.temp = "N/A"
        self.desc = "Pending"
        self.humidity = "N/A"
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.running = True
        self._thread = None
        self.forecast = []  # 오전/오후 예보 스냅샷

    def _update_once(self):
        headers = {"User-Agent": "Mozilla/5.0 (compatible; CodexBot/1.0)"}
        res = requests.get(f"https://wttr.in/{self.city}?format=j1", timeout=5, headers=headers)
        res.raise_for_status()
        data = res.json()
        current_list = data.get("current_condition", [])
        if not current_list:
            raise ValueError("current_condition missing")
        current = current_list[0]
        weather_desc = current.get("weatherDesc", [{"value": "N/A"}])[0].get("value", "N/A")
        self.temp = f"{current.get('temp_C', 'N/A')}°C"
        self.humidity = f"{current.get('humidity', 'N/A')}%"
        self.desc = weather_desc
        lower = weather_desc.lower()
        if "snow" in lower or "ice" in lower:
            self.condition = "Snow"
        elif "rain" in lower or "drizzle" in lower or "shower" in lower:
            self.condition = "Rain"
        else:
            self.condition = "Clear"
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M")

        weather_days = data.get("weather", [])
        today_hours = weather_days[0].get("hourly", []) if weather_days else []
        self.forecast = self._build_forecast(today_hours, datetime.now())

    def _closest_hourly(self, hourly, target_hour: int):
        def hour_value(entry):
            raw = str(entry.get("time", "0")).zfill(4)
            return int(raw[:2])

        if not hourly:
            return None
        return min(hourly, key=lambda h: abs(hour_value(h) - target_hour))

    def _build_forecast(self, hourly, now: datetime):
        snapshots = []
        targets = [("Morning", 9), ("Afternoon", 15)]
        for label, hour in targets:
            slot = self._closest_hourly(hourly, hour)
            if not slot:
                continue
            raw_time = str(slot.get("time", "0")).zfill(4)
            hh = int(raw_time[:2])
            desc = slot.get("weatherDesc", [{"value": "N/A"}])[0].get("value", "N/A")
            temp = slot.get("tempC", "N/A")
            rain = slot.get("chanceofrain", "0")
            humidity = slot.get("humidity", "N/A")
            snapshots.append(
                {
                    "time": f"{hh:02d}:00",
                    "label": f"{label}({hh:02d}:00)",
                    "temp": temp,
                    "desc": desc,
                    "rain": rain,
                    "humidity": humidity,
                }
            )
        return snapshots

    def fetch_weather(self):
        while self.running:
            try:
                self._update_once()
            except Exception:
                pass
            time.sleep(self.interval)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self.fetch_weather, daemon=True)
        self._thread.start()


weather_service = WeatherService("Sejong,KR")
weather_service.start()

news_cache = []
news_cache_fetched = 0.0


def fetch_alert():
    """
    Fetch the first board row's stage/title/date from NCSC for theming.
    """
    url = (
        "https://www.ncsc.go.kr/cop/bbs/selectBoardList.do"
        "?bbsId=CyberCrisis_main&nttId=0&menuNo=020000&subMenuNo=020100&thirdMenuNo="
    )
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CodexBot/1.0)"}
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.raise_for_status()
        if not res.encoding or res.encoding.lower() == "iso-8859-1":
            res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.select("table.board_list tbody tr")

        def valid_row(row):
            level_el = row.select_one("td.level span")
            title_el = row.select_one("td.tit")
            has_level = bool(level_el and level_el.get_text(strip=True))
            has_title = bool(title_el and title_el.get_text(strip=True))
            return has_level and has_title

        first_row = next((r for r in rows if valid_row(r)), None)
        level_el = first_row.select_one("td.level span") if first_row else None
        title_el = first_row.select_one("td.tit") if first_row else None
        date_el = first_row.select_one("td.date") if first_row else None

        status = level_el.get_text(strip=True) if level_el else "Status unavailable"
        desc = title_el.get_text(strip=True) if title_el else "Title unavailable"
        posted = date_el.get_text(strip=True) if date_el else "Date unavailable"
        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {"status": status, "desc": desc, "date": posted, "updated": updated, "ok": True}
    except Exception as e:
        return {
            "status": "Unavailable",
            "desc": str(e),
            "date": "Date unavailable",
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ok": False,
        }


def fetch_weather_sejong():
    """Return latest weather snapshot from background service."""
    return {
        "desc": weather_service.desc,
        "temp": weather_service.temp,
        "humidity": weather_service.humidity,
        "updated": weather_service.updated,
        "forecast": weather_service.forecast,
    }


def fetch_notices_top3():
    """
    Scrape top 3 rows (Title, Name, Date) from KDI School notice board.
    """
    url = "https://www.kdischool.ac.kr/board.es?mid=a20602000000&bid=0041"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CodexBot/1.0)"}
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.raise_for_status()
        if not res.encoding or res.encoding.lower() == "iso-8859-1":
            res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.select_one("table.tstyle_list tbody")
        rows = table.select("tr") if table else []
        notices = []
        for tr in rows[:5]:
            title_td = tr.find("td", attrs={"aria-label": "Title"})
            name_td = tr.find("td", attrs={"aria-label": "Name"})
            date_td = tr.find("td", attrs={"aria-label": "Date"})
            title_text = title_td.get_text(" ", strip=True) if title_td else "N/A"
            name_text = name_td.get_text(" ", strip=True) if name_td else "N/A"
            date_text = date_td.get_text(" ", strip=True) if date_td else "N/A"
            notices.append({"title": title_text, "name": name_text, "date": date_text})
        return notices
    except Exception:
        return []

def make_forecast_panel(theme):
    forecast = fetch_weather_sejong().get("forecast", [])

    cards = []
    for slot in forecast[:3]:
        cards.append(
            build_weather_card(
                slot.get("desc", "N/A"),
                f"{slot.get('temp', 'N/A')}°C",
                f"{slot.get('humidity', 'N/A')}%",
                title=f"Sejong {slot.get('label', '')}",
                accent=theme["accent"],
            )
        )
    while len(cards) < 3:
        cards.append(Panel(Text("No data", style="bright_black"), border_style="white"))

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    for card in cards:
        grid.add_row(card)

    return grid


def fetch_koreatimes_news(limit: int = 10, cache_ttl: int = 300):
    """Fetch tech-science headlines/leads with simple cache to avoid heavy polling."""
    global news_cache, news_cache_fetched
    now = time.time()
    if news_cache and now - news_cache_fetched < cache_ttl:
        return news_cache

    url = "https://www.koreatimes.co.kr/business/tech-science"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CodexBot/1.0)"}
    try:
        res = requests.get(url, timeout=8, headers=headers)
        res.raise_for_status()
        if not res.encoding or res.encoding.lower() == "iso-8859-1":
            res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        items = []
        for h3 in soup.select("h3.SectionModule_headline__t8DAC")[:limit]:
            article = h3.find_parent("article")
            headline = h3.get_text(strip=True)
            lead_el = article.select_one("p.SectionModule_lead__6dwJt") if article else None
            lead = lead_el.get_text(" ", strip=True) if lead_el else ""
            items.append({"headline": headline, "lead": lead})
        if items:
            news_cache = items
            news_cache_fetched = now
        return items
    except Exception:
        return news_cache

WEATHER_ASCII = {
    "clear": [
        "    \\   / ",
        "     .-.   ",
        "  ― (   ) ―",
        "     `-’   ",
        "    /   \\ ",
    ],
    "partly": [
        "   \\  /    ",
        ' _ /""-.    ',
        "   \\_(   ).",
        "   /(___(__)",
        "            ",
    ],
    "cloudy": [
        "     .--.   ",
        "  .-(    ). ",
        " (___.__)__)",
        "            ",
        "            ",
    ],
    "overcast": [
        "     .--.   ",
        "  .-(    ). ",
        " (___.__)__)",
        "  (___(__)) ",
        "            ",
    ],
    "fog": [
        "            ",
        " _ - _ - _ -",
        "  _ - _ - _ ",
        " _ - _ - _ -",
        "            ",
    ],
    "light rain": [
        "     .-.    ",
        "    (   ).  ",
        "   (___(__) ",
        "    ‘ ‘ ‘ ‘ ",
        "    ‘ ‘ ‘ ‘ ",
    ],
    "heavy rain": [
        "     .-.    ",
        "    (   ).  ",
        "   (___(__) ",
        "   ‘ ‘ ‘ ‘ ‘",
        "   ‘ ‘ ‘ ‘ ‘",
    ],
    "light showers": [
        "   \\  /    ",
        ' _ /""-.    ',
        "   \\_(   ).",
        "   /(___(__)",
        "    ‘ ‘ ‘ ‘ ",
    ],
    "heavy showers": [
        ' _/"".-.   ',
        " ,\\_(   ).",
        "  /(___(__)",
        "  ‘ ‘ ‘ ‘ ‘",
        "  ‘ ‘ ‘ ‘ ‘",
    ],
    "light snow": [
        "     .-.   ",
        "    (   ). ",
        "   (___(__)",
        "    *  *  *",
        "    *  *  *",
    ],
    "heavy snow": [
        "     .-.    ",
        "    (   ).  ",
        "   (___(__) ",
        "   * * * * *",
        "   * * * * *",
    ],
    "sleet": [
        "     .-.    ",
        "    (   ).  ",
        "   (___(__) ",
        "    * ‘ * ‘ ",
        "    ‘ * ‘ * ",
    ],
    "thunder": [
        "     .-.     ",
        "    (   ).   ",
        "   (___(__)  ",
        "    ⚡‘ ‘⚡‘",
        "    ‘ ‘ ‘ ‘  ",
    ],
}


def pick_weather_ascii(desc: str):
    low = desc.lower()
    mapping = [
        (["thunder", "번개", "천둥"], "thunder"),
        (["sleet", "진눈깨비"], "sleet"),
        (["heavy snow", "폭설"], "heavy snow"),
        (["snow", "눈"], "light snow"),
        (["heavy showers"], "heavy showers"),
        (["light showers", "shower"], "light showers"),
        (["heavy rain", "폭우"], "heavy rain"),
        (["rain", "비"], "light rain"),
        (["fog", "mist", "안개"], "fog"),
        (["overcast", "매우 흐림"], "overcast"),
        (["cloudy", "흐림"], "cloudy"),
        (["partly", "구름 조금"], "partly"),
        (["clear", "sunny", "맑음"], "clear"),
    ]
    for keywords, key in mapping:
        if any(k in low for k in keywords):
            return WEATHER_ASCII.get(key, WEATHER_ASCII["clear"])
    return WEATHER_ASCII["clear"]


def build_weather_card(desc: str, temp: str, humidity: str, title: Optional[str] = None, accent: str = "cyan"):
    """Weather card with ASCII art on top and condition/temperature/humidity below."""
    art = "\n".join(pick_weather_ascii(desc))

    body = Table.grid(expand=True)
    body.add_row(Align.center(Text("  ")))
    body.add_row(Align.center(Text(art)))
    body.add_row(Align.center(Text("  ")))

    details = Table.grid(padding=(0, 1))
    details.add_column(style=accent, no_wrap=True)
    details.add_column(style="white")
    details.add_row(Align.center(Text("  ")))
    details.add_row(Text("Condition", style=accent), desc)
    details.add_row(Text("Temp", style=accent), temp)
    details.add_row(Text("Humidity", style=accent), humidity)
    body.add_row(details)

    if title is None:
        return body
    return Panel(body, title=title, border_style="white")


def normalize_alert_level(level: str) -> str:
    """Map scraped status text to a normalized level key."""
    text = (level or "").strip().lower()
    for key, tokens in LEVEL_TOKEN_MAP.items():
        if any(token.lower() in text for token in tokens):
            return key
    return "NORMAL"


def resolve_theme(level: str):
    level_key = normalize_alert_level(level)
    theme = ALERT_THEMES.get(level_key, {"accent": "gray50", "bg": "#1c1c1c"})
    merged = dict(theme)
    merged["level"] = level_key
    return merged


def _trim_line(text: str, max_width: int) -> str:
    if max_width <= 0:
        return ""
    if len(text) <= max_width:
        return text
    return text[: max(0, max_width - 1)] + "…"


def render_alert_bar(level_key: str, theme, frame: int):
    """4-step bar that fills toward the target fraction with a short ramp animation."""
    targets = {"NORMAL": 0.0, "ATTENTION": 0.25, "CAUTION": 0.5, "WARNING": 0.75, "CRISIS": 1.0}
    target_fraction = targets.get(level_key, 0.0)
    segment_len = 16
    total_units = segment_len * 4
    ramp_period = 10  # faster fill; completes then loops back
    ramp = (max(frame, 0) % ramp_period) / ramp_period
    filled_units = int(total_units * target_fraction * ramp + 0.5)

    lines = []
    for _ in range(2):  # thickness: two stacked rows
        bar = Text()
        remaining = filled_units
        for _ in range(4):
            fill_here = max(0, min(segment_len, remaining))
            empty_here = segment_len - fill_here
            if fill_here:
                bar.append("█" * fill_here, style=theme["accent"])
            if empty_here:
                bar.append("░" * empty_here, style="grey23")
            remaining -= fill_here
        lines.append(bar)
    return Align.center(Group(*lines))


def render_alert_banner(level_key: str, theme):
    ascii_lines = BANNER_EN.get(level_key, BANNER_EN["NORMAL"])
    art = Text("\n".join(ascii_lines), style=f"bold {theme['accent']}")
    return Align.center(art)


def make_alert_widget(alert, theme, width: int, frame: int):
    level_key = normalize_alert_level(alert.get("status", ""))
    bar = render_alert_bar(level_key, theme, frame)
    banner = render_alert_banner(level_key, theme)

    date = "ALERT ISSUED : " + _trim_line(alert.get("date", ""), max(0, width - 20)) + " ~"

    body = Table.grid(padding=(0, 1), expand=True)
    body.add_row(Align.center(Text("  ")))
    body.add_row(bar)
    body.add_row(Align.center(Text("  ")))
    body.add_row(banner)
    body.add_row(Align.center(Text("  ")))
    body.add_row(Align.center(Text(date, style="bold white")))
    body.add_row(Align.center(Text("  ")))

    title_text = Text("NCSC Cybercrisis Alert", style=f"bold {theme['accent']}")
    return Panel(body, border_style=theme["accent"], title=title_text, padding=(0, 1))


def make_header(alert, theme, frame: int):
    logo_main = Text("\n".join(LOGO_MAIN), style=f"bold {theme['accent']}")
    logo_sub = Text("\n".join(LOGO_SUB), style="bright_white")

    header_width = console.size.width
    right_width = max(50, min(int(header_width * 0.4), 80))

    left_stack = Group(Align.left(logo_main), Align.left(logo_sub))
    left_panel = Panel(left_stack, border_style="", padding=(0, 2), box=box.MINIMAL)

    right_widget = make_alert_widget(alert, theme, right_width - 4, frame)

    grid = Table.grid(expand=True)
    grid.add_column(ratio=2.2)
    grid.add_column(ratio=2, width=right_width)
    grid.add_row(left_panel, right_widget)

    return Panel(grid, box=box.HEAVY, padding=(1, 1), border_style=theme["accent"], style=f"on {theme['bg']}")


def make_misc_table(theme):
    weather = fetch_weather_sejong()
    current_card = build_weather_card(
        weather.get("desc", "N/A"),
        weather.get("temp", "N/A"),
        weather.get("humidity", "N/A"),
        title=None,
        accent=theme["accent"],
    )

    weather_panel = Panel(current_card, title="Sejong Weather", border_style=theme["accent"])

    news_items = fetch_koreatimes_news()
    news_left = Table.grid(expand=True)

    def news_panel(item, idx, total):
        box = Table.grid(padding=(0, 1), expand=True)
        box.add_row(Align.left(Text(item.get("headline", ""), style=f"bold {theme['accent']}")))
        box.add_row(Align.left(Text("  ")))
        lead = textwrap.shorten(item.get("lead", ""), width=300, placeholder=" ...")
        box.add_row(Text(lead, style="white"))
        return Panel(box, title=f"The Korea Times - Tech·Science NEWS", border_style=theme["accent"])

    if news_items:
        total = len(news_items)
        base = int(time.time() // 60) % total
        first = news_items[base]
        second = news_items[(base + 1) % total] if total > 1 else None
        news_left.add_row(news_panel(first, base + 1, total))
        if second:
            news_left.add_row(news_panel(second, ((base + 1) % total) + 1, total))
    else:
        news_left.add_row(Panel(Text("Failed to load news.", style="bright_black"), title="The Korea Times - Tech·Science", border_style="grey50"))

    grid = Table.grid(expand=True)
    grid.add_column(ratio=3)
    grid.add_column(ratio=1)
    grid.add_row(news_left, weather_panel)

    return Panel(grid, border_style=theme["accent"])


class MarqueeFooter:
    """Static left-aligned footer (no scrolling)."""

    def __init__(self, lines, fps: int = 10):
        self.lines = lines
        self.fps = fps

    def render(self, frame: int, width: int, height: int) -> str:
        if height <= 0:
            return ""
        rendered = []
        visible = min(len(self.lines), height)
        top_pad = max(0, (height - visible) // 2)
        for row in range(height):
            line_idx = row - top_pad
            if line_idx < 0 or line_idx >= visible:
                rendered.append(" " * width)
                continue
            line = self.lines[line_idx]
            rendered.append(line[:width].ljust(width))
        return "\n".join(rendered[:height])


footer_matrix = MarqueeFooter(NOTICE_IT)


def build_layout(alert, frame: int):
    theme = resolve_theme(alert["status"])
    header_size = 20
    min_footer = 6
    fixed_body_height = 16

    layout = Layout()
    layout.split_column(Layout(name="header", size=header_size), Layout(name="body"), Layout(name="footer"))

    layout["header"].size = header_size
    layout["header"].update(make_header(alert, theme, frame))

    body_renderable = make_misc_table(theme)

    layout["body"].size = fixed_body_height
    layout["body"].update(body_renderable)

    total_height = console.size.height
    remaining_height = total_height - header_size - fixed_body_height
    footer_height = max(min_footer, remaining_height)

    width = console.size.width
    footer_frame = footer_matrix.render(frame, width, footer_height)
    layout["footer"].size = footer_height
    # Single-style text keeps the rain subtle; adjust style if higher contrast is needed.
    layout["footer"].update(Text(footer_frame, style=theme["accent"]))
    return layout


def main(poll_interval=60, frame_interval=None):
    last_alert = fetch_alert()
    last_fetch = time.time()
    frame = 0
    if frame_interval is None:
        frame_interval = 1 / footer_matrix.fps
    with Live(console=console, screen=True, auto_refresh=False) as live:
        while True:
            now = time.time()
            if now - last_fetch >= poll_interval:
                last_alert = fetch_alert()
                last_fetch = now

            layout = build_layout(last_alert, frame)
            live.update(layout, refresh=True)
            time.sleep(frame_interval)
            frame += 1


if __name__ == "__main__":
    main(poll_interval=60)
