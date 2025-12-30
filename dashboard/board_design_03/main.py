import math
import random
import threading
import time
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
    "╔══════════════════════════════════════════════════════════════════════════════════════════╗",
    "║     ██████╗  █████╗ ████████╗ █████╗     ██╗   ██╗███╗   ██╗██╗████████╗    ██████╗      ║",
    "║     ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ██║   ██║████╗  ██║██║╚══██╔══╝    ╚════██╗     ║",
    "║     ██║  ██║███████║   ██║   ███████║    ██║   ██║██╔██╗ ██║██║   ██║        █████╔╝     ║",
    "║     ██║  ██║██╔══██║   ██║   ██╔══██║    ██║   ██║██║╚██╗██║██║   ██║       ██╔═══╝      ║",
    "║     ██████╔╝██║  ██║   ██║   ██║  ██║    ╚██████╔╝██║ ╚████║██║   ██║       ███████╗     ║",
    "║     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝       ╚══════╝     ║",
    "╚══════════════════════════════════════════════════════════════════════════════════════════╝",
]


class WeatherService:
    """Background updater for weather."""

    def __init__(self, city: str, interval: int = 120):
        self.city = city
        self.interval = interval
        self.condition = "Clear"
        self.temp = "N/A"
        self.desc = "대기중"
        self.humidity = "N/A"
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.running = True
        self._thread = None
        self.forecast = []  # 다음 시간대 예보
        self.forecast_offsets = [3, 6, 9]  # 3, 6, 9시간 후 예보

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
        future = []
        for offset in self.forecast_offsets:
            target = now + timedelta(hours=offset)
            slot = self._closest_hourly(hourly, target.hour)
            if not slot:
                continue
            raw_time = str(slot.get("time", "0")).zfill(4)
            hh = int(raw_time[:2])
            desc = slot.get("weatherDesc", [{"value": "N/A"}])[0].get("value", "N/A")
            temp = slot.get("tempC", "N/A")
            rain = slot.get("chanceofrain", "0")
            humidity = slot.get("humidity", "N/A")
            future.append(
                {
                    "time": f"{hh:02d}:00",
                    "label": f"{offset}시간 후 ({target.strftime('%H:00')})",
                    "temp": temp,
                    "desc": desc,
                    "rain": rain,
                    "humidity": humidity,
                }
            )
        return future

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

        status = level_el.get_text(strip=True) if level_el else "단계 확인 실패"
        desc = title_el.get_text(strip=True) if title_el else "게시글 제목 확인 실패"
        posted = date_el.get_text(strip=True) if date_el else "발령일 확인 실패"
        updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {"status": status, "desc": desc, "date": posted, "updated": updated, "ok": True}
    except Exception as e:
        return {
            "status": "확인 실패",
            "desc": str(e),
            "date": "발령일 확인 실패",
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
                title=f"세종시 {slot.get('label', '')}",
            )
        )
    while len(cards) < 3:
        cards.append(Panel(Text("데이터 없음", style="bright_black"), border_style="white"))

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    for card in cards:
        grid.add_row(card)

    return grid

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


def build_weather_card(desc: str, temp: str, humidity: str, title: str):
    """Weather card with ASCII art on top and 상태/기온/습도 below."""
    art = "\n".join(pick_weather_ascii(desc))

    body = Table.grid(expand=True)
    body.add_row(Align.center(Text(art)))

    details = Table.grid(padding=(0, 1))
    details.add_column(style="cyan", no_wrap=True)
    details.add_column(style="white")
    details.add_row("상태", desc)
    details.add_row("기온", temp)
    details.add_row("습도", humidity)
    body.add_row(details)

    return Panel(body, title=title, border_style="white")


def resolve_theme(level: str):
    for key, theme in THEMES.items():
        if key in level:
            return theme | {"level": key}
    return {"accent": "gray50", "bg": "#1c1c1c", "level": "알 수 없음"}


def _trim_line(text: str, max_width: int) -> str:
    if max_width <= 0:
        return ""
    if len(text) <= max_width:
        return text
    return text[: max(0, max_width - 1)] + "…"


def render_spinner_circle(level_text: str, theme, frame: int, diameter: int = 11):
    accent = theme["accent"]
    diameter = max(9, min(13, diameter | 1))  # enforce odd for centering
    radius = (diameter - 1) / 2
    aspect = 1.3  # squash vertical distance so circle looks round in text cells
    bright_angle = (frame % max(12, diameter * 2)) / (diameter * 2) * math.tau
    highlight_width = 0.6
    grid = []
    for y in range(diameter):
        row = []
        for x in range(diameter):
            dx = x - radius
            dy = (y - radius) * aspect
            dist = math.hypot(dx, dy)
            if dist > radius + 0.6:
                row.append((" ", ""))
                continue
            if dist >= radius - 0.6:
                ang = math.atan2(dy, dx) % math.tau
                diff = min((ang - bright_angle) % math.tau, (bright_angle - ang) % math.tau)
                if diff < highlight_width:
                    row.append(("█", f"bold {accent}"))
                else:
                    row.append(("░", accent))
            else:
                row.append(("░", "grey58"))
        grid.append(row)

    center_row = diameter // 2
    text_line = _trim_line(f"{level_text}", diameter)
    start = max(0, (diameter - len(text_line)) // 2)
    for i, ch in enumerate(text_line):
        idx = start + i
        if 0 <= idx < len(grid[center_row]):
            grid[center_row][idx] = (ch, f"bold {accent}")

    lines = []
    for row in grid:
        t = Text()
        for ch, style in row:
            t.append(ch, style=style)
        lines.append(t)
    return lines


def render_spinner_circle_ellipse(
    level_text: str,
    theme,
    frame: int,
    diameter: int = 11,
    diameter_x: Optional[int] = None,
    diameter_y: Optional[int] = None,
):
    """
    Elliptical variant with independent x/y sizing.
    """
    accent = theme["accent"]
    base_d = max(9, min(13, diameter | 1))  # keep legacy clamp
    dx_len = max(9, min(17, (diameter_x if diameter_x else base_d) | 1))
    dy_len = max(9, min(9, (diameter_y if diameter_y else base_d) | 1))
    if dx_len > dy_len + 2:
        dx_len = dy_len + 2  # limit horizontal stretch to keep edges from protruding
    radius_x = (dx_len - 1) / 2
    radius_y = (dy_len - 1) / 2
    spin_speed = 3  # increase to spin faster
    bright_angle = ((frame * spin_speed) % max(12, base_d * 2)) / (base_d * 2) * math.tau
    highlight_width = 0.6
    margin = 0.6 / max(radius_x, radius_y, 1e-6)

    grid = []
    for y in range(dy_len):
        row = []
        for x in range(dx_len):
            dxn = (x - radius_x) / max(radius_x, 1e-6)
            dyn = (y - radius_y) / max(radius_y, 1e-6)
            dist = math.hypot(dxn, dyn)
            if dist > 1.0 + margin:
                row.append((" ", ""))
                continue
            if dist >= 1.0 - margin:
                ang = math.atan2(dyn, dxn) % math.tau
                diff = min((ang - bright_angle) % math.tau, (bright_angle - ang) % math.tau)
                if diff < highlight_width:
                    row.append(("█", f"bold {accent}"))
                else:
                    row.append(("░", accent))
            else:
                row.append((" ", "grey58"))
        grid.append(row)

    center_row = dy_len // 2
    text_line = _trim_line(f"{level_text}", dx_len)
    start = max(0, (dx_len - len(text_line)) // 2)
    for i, ch in enumerate(text_line):
        idx = start + i
        if 0 <= idx < len(grid[center_row]):
            grid[center_row][idx] = (ch, f"bold {accent}")
    # Remove exactly two cells immediately after the text on the center row,
    # without touching other rows or the left side. Pad spaces at the end to keep width.
    after = start + len(text_line)
    for _ in range(2):
        if 0 <= after < len(grid[center_row]):
            del grid[center_row][after]
    while len(grid[center_row]) < dx_len:
        grid[center_row].append((" ", ""))

    lines = []
    for row in grid:
        t = Text()
        for ch, style in row:
            t.append(ch, style=style)
        lines.append(t)
    return lines


def make_alert_spinner_widget(alert, theme, frame: int, width: int):
    # Make badge wider by using more of the available width.
    badge_diameter = max(11, min(25, width - 2))
    spinner_lines = render_spinner_circle_ellipse(
        theme["level"], theme, frame, badge_diameter, diameter_x=badge_diameter, diameter_y=badge_diameter
    )
    spinner_lines = [Text("")] + spinner_lines + [Text("")]
    spinner = Align.center(Group(*spinner_lines))

    body = Table.grid(padding=(0, 1), expand=True)
    body.add_row(spinner)

    info_width = max(10, width - 2)
    title = _trim_line(f"게시글 제목: {alert.get('desc', '')}", info_width)
    date = _trim_line(f"발령일: {alert.get('date', '')}", info_width)
    updated = alert.get("updated", "")

    body.add_row(Text(title, style="white"))
    body.add_row(Text(date, style="bright_black"))
    if updated:
        body.add_row(Text(_trim_line(f"업데이트: {updated}", info_width), style="bright_black"))

    title_text = Text("NCSC 사이버 위기경보", style=f"bold {theme['accent']}")
    return Panel(body, border_style=theme["accent"], title=title_text, padding=(0, 1))


def make_header(alert, theme, frame: int):
    logo_main = Text("\n".join(LOGO_MAIN), style=f"bold {theme['accent']}")
    logo_sub = Text("\n".join(LOGO_SUB), style="bright_white")

    header_width = console.size.width
    right_width = max(35, min(int(header_width * 0.33), 55))

    left_stack = Group(Align.left(logo_main), Align.left(logo_sub))
    left_panel = Panel(left_stack, border_style=theme["accent"], padding=(0, 2), box=box.ROUNDED)

    right_widget = make_alert_spinner_widget(alert, theme, frame, right_width - 4)

    grid = Table.grid(expand=True)
    grid.add_column(ratio=3)
    grid.add_column(ratio=2, width=right_width)
    grid.add_row(left_panel, right_widget)

    return Panel(grid, box=box.HEAVY, padding=(1, 1), border_style=theme["accent"], style=f"on {theme['bg']}")


def make_misc_table(theme):
    weather = fetch_weather_sejong()
    forecast = weather.get("forecast") or []

    slots = [
        {
            "title": "세종시 현재",
            "desc": weather.get("desc", "N/A"),
            "temp": weather.get("temp", "N/A"),
            "humidity": weather.get("humidity", "N/A"),
        }
    ]
    for slot in forecast[:3]:
        slots.append(
            {
                "title": f"세종시 {slot.get('label', '')}",
                "desc": slot.get("desc", "N/A"),
                "temp": f"{slot.get('temp', 'N/A')}°C",
                "humidity": f"{slot.get('humidity', 'N/A')}%",
            }
        )
    while len(slots) < 4:
        slots.append({"title": "데이터 없음", "desc": "N/A", "temp": "N/A", "humidity": "N/A"})

    cards = [
        build_weather_card(s["desc"], s["temp"], s["humidity"], title=s["title"])
        for s in slots[:4]
    ]

    row_weather = Table.grid(expand=True)
    row_weather.add_column(ratio=1)
    row_weather.add_column(ratio=1)
    row_weather.add_column(ratio=1)
    row_weather.add_column(ratio=1)
    row_weather.add_row(cards[0], cards[1], cards[2], cards[3])

    notices = fetch_notices_top3()
    notice_table = Table(box=box.SIMPLE, show_header=True, expand=True, padding=(0, 1))
    notice_table.add_column("제목", ratio=3, style="white")
    notice_table.add_column("작성자", ratio=1, style="cyan", no_wrap=True)
    notice_table.add_column("등록일", ratio=1, style="white", no_wrap=True)
    if notices:
        for n in notices:
            notice_table.add_row(n["title"], n["name"], n["date"])
    else:
        notice_table.add_row("불러오기 실패", "-", "-")
    notice_panel = Panel(notice_table, title="Notice", border_style="white")

    stack = Table.grid(expand=True)
    stack.add_column()
    stack.add_row(row_weather)
    stack.add_row(notice_panel)

    return Panel(stack, border_style=theme["accent"])


class FooterMatrix:
    """Matrix-style digital rain footer with seamless looping."""

    def __init__(self, console_ref: Console, fps: int = 18):
        self.console = console_ref
        self.fps = fps
        self.seed_base = 4242
        self.width = 0
        self.height = 0
        self.columns = []
        self.head_chars = list("89bf")
        self.body_chars = list("0123456789abcdef")
        self.fade_chars = [".", " "]
        self.symbol_chars = list(":/|.")

    def _init_columns(self, width: int, height: int):
        rng = random.Random(self.seed_base + width * 17 + height * 31)
        columns = []
        for x in range(width):
            speed = rng.choice([2, 2, 3, 3, 4])
            trail_len = rng.randint(6, 18)
            # Tune speed/trail_len/glitch to balance density and drift depth.
            head_y = -rng.randint(0, height)
            glitch = rng.uniform(0.01, 0.05)
            pause = rng.randint(0, 6)
            stream_seed = rng.randint(0, 1_000_000)
            columns.append(
                {
                    "x": x,
                    "speed": speed,
                    "trail_len": trail_len,
                    "head_y": head_y,
                    "pause": pause,
                    "glitch": glitch,
                    "seed": stream_seed,
                }
            )
        return columns

    def _ensure_state(self, width: int, height: int):
        if width != self.width or height != self.height or not self.columns:
            self.width = width
            self.height = height
            self.columns = self._init_columns(width, height)

    def _pick_char(self, col, depth: int, frame: int):
        key = col["seed"] + frame * 131 + depth * 17
        r = random.Random(key)
        if depth == 0:
            pool = self.head_chars
        elif depth < 4:
            pool = self.body_chars
        elif depth < col["trail_len"] - 2:
            pool = self.body_chars + self.symbol_chars
        else:
            pool = self.fade_chars + self.body_chars[:2]
        ch = r.choice(pool)
        if r.random() < col["glitch"]:
            ch = r.choice(self.symbol_chars + self.body_chars)
        return ch

    def render(self, frame: int, width: int, height: int) -> str:
        self._ensure_state(width, height)
        grid = [[" " for _ in range(width)] for _ in range(height)]
        for idx, col in enumerate(self.columns):
            r = random.Random(col["seed"] + frame * 29 + idx * 7)
            if col["pause"] > 0:
                col["pause"] -= 1
            else:
                col["head_y"] += col["speed"]
                if r.random() < 0.05:
                    col["pause"] = r.randint(1, 6)
            head_y = col["head_y"]
            if head_y - col["trail_len"] > height + 4:
                col["head_y"] = -r.randint(0, height // 2 + 4)
                col["speed"] = r.choice([1, 2, 3])
                col["trail_len"] = r.randint(6, 18)
                head_y = col["head_y"]
            for depth in range(col["trail_len"]):
                y = int(head_y) - depth
                if y < 0 or y >= height:
                    continue
                ch = self._pick_char(col, depth, frame)
                strength = 1.0 - (depth / max(1, col["trail_len"]))
                gate = r.random()
                if y < 4:
                    strength *= 0.6
                elif y >= 14:
                    strength *= 1.05
                if gate > strength:
                    continue
                grid[y][col["x"]] = ch
        bus_rng = random.Random(self.seed_base + frame * 3 + width * 5)
        bus_line = height - 1
        for x in range(width):
            if bus_rng.random() < 0.08:
                grid[bus_line][x] = bus_rng.choice(["-", "/", "|", "."])
        lines = ["".join(row).ljust(width)[:width] for row in grid]
        return "\n".join(lines)


footer_matrix = FooterMatrix(console)


def build_layout(alert, frame: int):
    theme = resolve_theme(alert["status"])
    header_size = 20
    min_footer = 1

    layout = Layout()
    layout.split_column(Layout(name="header", size=header_size), Layout(name="body"), Layout(name="footer"))

    layout["header"].size = header_size
    layout["header"].update(make_header(alert, theme, frame))

    body_renderable = make_misc_table(theme)
    # Capture body render height at current width so the footer can claim remaining space.
    with Console(width=console.size.width, record=True) as temp_console:
        with temp_console.capture() as cap:
            temp_console.print(body_renderable)
        body_lines = cap.get().splitlines()
    body_height = len(body_lines) + 1

    total_height = console.size.height
    remaining_height = total_height - header_size - body_height
    if remaining_height < min_footer:
        deficit = min_footer - remaining_height
        body_height = max(1, body_height - deficit)
        remaining_height = total_height - header_size - body_height
    if remaining_height < 0:
        body_height = max(1, total_height - header_size - min_footer)
        remaining_height = total_height - header_size - body_height
    footer_height = max(min_footer, remaining_height)

    layout["body"].size = body_height
    layout["body"].update(body_renderable)

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
