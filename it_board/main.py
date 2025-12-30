#!/usr/bin/env python3
"""
KDI School, Data Unit 2 - Terminal Banner Application
A full-screen animated console application with professional design
"""

import curses
import time
import random
import textwrap
import json
import urllib.request
import urllib.error
import ssl
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

SEJONG_LAT = 36.4800
SEJONG_LON = 127.2890
WEATHER_UPDATE_INTERVAL = 600
CHAPTER_DURATION = 20
FPS = 15  # Increased for smoother animations


class WeatherState(Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    WIND = "wind"
    THUNDER = "thunder"


# ============================================================================
# PROFESSIONAL ASCII ART LOGO
# ============================================================================

LOGO_MAIN = [
    "██╗  ██╗██████╗ ██╗    ███████╗ ██████╗██╗  ██╗ ██████╗  ██████╗ ██╗     ",
    "██║ ██╔╝██╔══██╗██║    ██╔════╝██╔════╝██║  ██║██╔═══██╗██╔═══██╗██║     ",
    "█████╔╝ ██║  ██║██║    ███████╗██║     ███████║██║   ██║██║   ██║██║     ",
    "██╔═██╗ ██║  ██║██║    ╚════██║██║     ██╔══██║██║   ██║██║   ██║██║     ",
    "██║  ██╗██████╔╝██║    ███████║╚██████╗██║  ██║╚██████╔╝╚██████╔╝███████╗",
    "╚═╝  ╚═╝╚═════╝ ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝",
]

LOGO_SUB = [
    "╔═══════════════════════════════════════════════════════════════════════╗",
    "║     ██████╗  █████╗ ████████╗ █████╗     ██╗   ██╗███╗   ██╗██╗████████╗    ██████╗      ║",
    "║     ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗    ██║   ██║████╗  ██║██║╚══██╔══╝    ╚════██╗     ║",
    "║     ██║  ██║███████║   ██║   ███████║    ██║   ██║██╔██╗ ██║██║   ██║        █████╔╝     ║",
    "║     ██║  ██║██╔══██║   ██║   ██╔══██║    ██║   ██║██║╚██╗██║██║   ██║       ██╔═══╝      ║",
    "║     ██████╔╝██║  ██║   ██║   ██║  ██║    ╚██████╔╝██║ ╚████║██║   ██║       ███████╗     ║",
    "║     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝       ╚══════╝     ║",
    "╚═══════════════════════════════════════════════════════════════════════╝",
]

# Simplified but stylish logo for smaller terminals
LOGO_COMPACT = [
    "╔══════════════════════════════════════════════════════════════╗",
    "║  ▄█   ▄█▀▀▀█▄█    ▄███▄      ▄████████  ▄████████ ▄██   ▄    ║",
    "║  ███ ▄███    ▀    █▀   ▀    ███    ███ ███    ███ ███   ██▄  ║",
    "║  ███ ███    ▄     ██▄▄      ███    █▀  ███    █▀  ███▄▄▄███  ║",
    "║  ███ ▀▀███▀▀▀      ▀▀▀▀▀▀   ▄███▄▄▄    ███        ▀▀▀▀▀▀███  ║",
    "║  ███ ███    ▄            ▀ ▀▀███▀▀▀    ███        ▄██   ███  ║",
    "║  ███ ███    ███  ▀█████▀    ███    █▄  ███    █▄  ███   ███  ║",
    "║  █▀   ▀█████▀              ██████████ ████████▀   ▀█████▀   ║",
    "╠══════════════════════════════════════════════════════════════╣",
    "║           ░█▀▄░█▀█░▀█▀░█▀█░░░█░█░█▀█░▀█▀░▀█▀░░░▀▀█           ║",
    "║           ░█░█░█▀█░░█░░█▀█░░░█░█░█░█░░█░░░█░░░░▄▀░           ║",
    "║           ░▀▀░░▀░▀░░▀░░▀░▀░░░▀▀▀░▀░▀░▀▀▀░░▀░░░░▀▀▀           ║",
    "╚══════════════════════════════════════════════════════════════╝",
]

# Even more stylish compact version
LOGO_STYLISH = [
    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓",
    "┃                                                                           ┃",
    "┃   ██╗  ██╗██████╗ ██╗    ███████╗ ██████╗██╗  ██╗ ██████╗  ██████╗ ██╗     ┃",
    "┃   ██║ ██╔╝██╔══██╗██║    ██╔════╝██╔════╝██║  ██║██╔═══██╗██╔═══██╗██║     ┃",
    "┃   █████╔╝ ██║  ██║██║    ███████╗██║     ███████║██║   ██║██║   ██║██║     ┃",
    "┃   ██╔═██╗ ██║  ██║██║    ╚════██║██║     ██╔══██║██║   ██║██║   ██║██║     ┃",
    "┃   ██║  ██╗██████╔╝██║    ███████║╚██████╗██║  ██║╚██████╔╝╚██████╔╝███████╗┃",
    "┃   ╚═╝  ╚═╝╚═════╝ ╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝┃",
    "┃                                                                           ┃",
    "┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫",
    "┃        ╔╦╗╔═╗╔╦╗╔═╗  ╦ ╦╔╗╔╦╔╦╗  ╔═╗        ┃        SEJONG, KOREA        ┃",
    "┃         ║║╠═╣ ║ ╠═╣  ║ ║║║║║ ║   ╔═╝        ┃    Innovation & Trust       ┃",
    "┃        ═╩╝╚═╝ ╩ ╚═╝  ╚═╝╝╚╝╩ ╩   ╚═╝        ┃                             ┃",
    "┃                                                                           ┃",
    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛",
]


# ============================================================================
# STORY CONTENT
# ============================================================================

STORY_CHAPTERS = [
    """[제1장] 데이터 별이 쏟아지던 날

아주 먼 옛날, 그러나 사실은 몇 년 전, 세종시의 한 언덕 위에
데이터가 별처럼 쏟아지는 마법 같은 대학원이 있었습니다.
그곳의 이름은 바로 KDI School.
그리고 그 한쪽 구석, 서버실 옆 작은 문 뒤에는
아무나 들어갈 수 없는 비밀 공간, Data Unit 2가 있었지요.""",

    """[제2장] 노래하는 엑셀, 춤추는 로그

Data Unit 2에는 전설 같은 소문이 돌았습니다.
"저 방에 들어가면, 엑셀 파일이 갑자기 노래를 부르고,
로그 데이터가 춤을 춘대!"
실제로 문을 살짝 열어보면,
모니터 속 숫자들이 작은 요정처럼 반짝이며
"오늘도 품질 검증 완료!"라고 외치고 있었답니다.""",

    """[제3장] 데이터 폭풍의 습격

어느 날, KDI School에 데이터 폭풍이 밀려왔습니다.
각종 시스템에서 몰려든 로그, 설문, 연구데이터가
거대한 파도처럼 밀려와
"이제 학교는 데이터 바다에 잠기고 말 거야!"
라는 걱정이 캠퍼스를 뒤덮었습니다.""",

    """[제4장] 영웅들의 등장

그때, Data Unit 2의 문이 슥— 하고 열리더니
모니터 빛을 두른 팀원들이 하나둘씩 걸어나왔습니다.
그들의 손에는 반짝이는 도구들이 들려 있었지요.
한 손에는 ETL 마법지팡이,
다른 손에는 품질검사 렌즈,
그리고 머리 위에는 살짝 떠 있는 AI 가드레일 링.""",

    """[제5장] 빛으로 변한 파도

팀원들은 외쳤습니다.
"데이터는 두려움의 파도가 아니라,
정책을 밝히는 빛입니다!"
그러자 바다처럼 넘실대던 데이터들이
하나둘씩 정갈한 표와 그래프로 변하기 시작했습니다.
쓰나미 같던 로그는 차분한 타임라인으로,
뒤엉킨 설문 응답은 깔끔한 인사이트로 정렬되었지요.""",

    """[제6장] 개인정보 드래곤의 출현

하지만 진짜 위기는 따로 있었습니다.
데이터 속에 숨어 있던 개인정보 드래곤이
"으르렁! 이 소중한 개인정보를 아무 데나 흘려보내주마!"
하며 불을 뿜으려는 순간,
Data Unit 2의 AI 가드레일 링이 부드럽게 빛나며 말했습니다.
"여기서는 아무도 다치지 않아요.
우리는 개인정보를 지키는 보이지 않는 방패니까요." """,

    """[제7장] 별가루가 된 불꽃

AI 가드레일 링이 빛을 더하자,
개인정보 드래곤의 불꽃은 가명처리된 별가루로 바뀌었고,
민감한 정보들은 안전한 형식으로 변신했습니다.
연구자들은 안심하고 데이터를 활용할 수 있게 되었고,
학생들의 아이디어는 데이터 위에서
더 멀리, 더 높이 날아오르기 시작했습니다.""",

    """[제8장] 세종시의 데이터 등대

그날 이후로 사람들은 말했습니다.
"무언가 복잡한 데이터 문제가 생기면,
Data Unit 2가 알아서 해결해줄 거야."
Data Unit 2는 마치 세종시의 데이터 등대처럼
조용하지만 밝게, KDI School의 길을 비추었습니다.""",

    """[제9장] 지금 이 순간

그리고 지금, 사무실 입구를 지나가는 당신이
이 터미널 화면을 보고 있다면,
이미 Data Unit 2의 마법은 절반쯤 성공한 셈입니다.
왜냐하면, 이 화면 하나가 말하고 있기 때문이지요.
"여기, 보이지 않는 곳에서
학교의 내일을 준비하는 사람들이 있습니다." """,

    """[제10장] 변하지 않는 약속

자, 이제 이야기의 마지막 장면입니다.
날씨는 매일 바뀌고, 데이터도 매일 쌓이지만,
한 가지는 변하지 않습니다.
KDI School, Data Unit 2는
언제나 조용히, 그러나 가장 혁신적인 방법으로
데이터를 지키고, 활용하고, 미래를 설계하고 있다는 사실입니다.

"데이터가 쌓이는 곳마다, 그 뒤에는 Data Unit 2가 있다." """,
]


# ============================================================================
# PARTICLE SYSTEM FOR FANCY EFFECTS
# ============================================================================

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    char: str
    color: int
    life: float
    max_life: float


class ParticleSystem:
    """Advanced particle system for visual effects."""

    def __init__(self, max_particles: int = 200):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def emit(self, x: float, y: float, count: int, chars: str, color: int,
             vx_range: Tuple[float, float] = (-1, 1),
             vy_range: Tuple[float, float] = (-1, 1),
             life_range: Tuple[float, float] = (20, 50)):
        """Emit new particles."""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            self.particles.append(Particle(
                x=x + random.uniform(-2, 2),
                y=y + random.uniform(-1, 1),
                vx=random.uniform(*vx_range),
                vy=random.uniform(*vy_range),
                char=random.choice(chars),
                color=color,
                life=random.uniform(*life_range),
                max_life=life_range[1]
            ))

    def update(self):
        """Update all particles."""
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            # Add gravity or other effects
            p.vy += 0.02
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]

    def render(self, stdscr, max_y: int, max_x: int):
        """Render all particles."""
        for p in self.particles:
            x, y = int(p.x), int(p.y)
            if 0 <= y < max_y - 1 and 0 <= x < max_x - 1:
                try:
                    # Fade effect based on life
                    attr = curses.A_BOLD if p.life > p.max_life * 0.5 else curses.A_DIM
                    stdscr.addstr(y, x, p.char, curses.color_pair(p.color) | attr)
                except curses.error:
                    pass


# ============================================================================
# AURORA WAVE EFFECT
# ============================================================================

class AuroraWave:
    """Beautiful aurora borealis effect with flowing color gradients."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.time = 0
        self.waves: List[dict] = []
        self._init_waves()

    def _init_waves(self):
        """Initialize aurora wave layers."""
        self.waves = []
        # Create multiple wave layers with different properties
        for i in range(5):
            self.waves.append({
                'frequency': random.uniform(0.02, 0.05),
                'amplitude': random.uniform(2, 5),
                'speed': random.uniform(0.02, 0.05),
                'phase': random.uniform(0, math.pi * 2),
                'y_offset': random.uniform(0.1, 0.4),  # Vertical position (0-1)
                'color_base': random.choice([80, 81, 82, 83, 84]),
            })

    def resize(self, width: int, height: int):
        """Handle resize."""
        self.width = width
        self.height = height

    def update(self):
        """Update aurora animation."""
        self.time += 1
        # Slowly shift wave properties for organic movement
        for wave in self.waves:
            wave['phase'] += wave['speed']

    def render(self, stdscr, max_y: int, max_x: int, intensity: float = 0.5):
        """Render aurora waves."""
        # Aurora characters from dim to bright
        aurora_chars = ["░", "▒", "▓", "█", "▓", "▒", "░"]

        for wave in self.waves:
            if random.random() > intensity:
                continue

            base_y = int(max_y * wave['y_offset'])

            for x in range(0, max_x - 1, 2):
                # Calculate wave position using multiple sine waves for organic look
                y_offset = (
                    math.sin(x * wave['frequency'] + wave['phase']) * wave['amplitude'] +
                    math.sin(x * wave['frequency'] * 0.5 + wave['phase'] * 1.3) * wave['amplitude'] * 0.5 +
                    math.sin(self.time * 0.05 + x * 0.01) * 1.5
                )

                y = int(base_y + y_offset)

                # Draw vertical gradient at this x position
                for dy in range(-2, 3):
                    render_y = y + dy
                    if 0 <= render_y < max_y - 1 and 0 <= x < max_x - 1:
                        try:
                            # Fade based on distance from center
                            char_idx = abs(dy) + int(abs(math.sin(x * 0.1 + self.time * 0.1)))
                            char_idx = min(char_idx, len(aurora_chars) - 1)
                            char = aurora_chars[char_idx]

                            # Color variation based on position and time
                            color_shift = int(math.sin(x * 0.05 + self.time * 0.02) * 2)
                            color = wave['color_base'] + color_shift
                            color = max(80, min(84, color))

                            attr = curses.A_BOLD if dy == 0 else curses.A_DIM
                            stdscr.addstr(render_y, x, char, curses.color_pair(color) | attr)
                        except curses.error:
                            pass

        # Add occasional bright sparkles
        if random.random() < 0.3:
            for _ in range(3):
                sx = random.randint(1, max_x - 2)
                sy = random.randint(1, int(max_y * 0.5))
                try:
                    sparkle_char = random.choice(["✦", "✧", "·", "•"])
                    stdscr.addstr(sy, sx, sparkle_char, curses.color_pair(84) | curses.A_BOLD)
                except curses.error:
                    pass


# ============================================================================
# WEATHER CLIENT
# ============================================================================

@dataclass
class WeatherData:
    temperature: float
    state: WeatherState
    description: str


class WeatherClient:
    """Fetches weather data from Open-Meteo API."""

    def __init__(self):
        self.last_update = 0
        self.cached_data: Optional[WeatherData] = None
        # Create SSL context that doesn't verify certificates (for macOS compatibility)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def get_weather(self) -> WeatherData:
        current_time = time.time()
        if self.cached_data and (current_time - self.last_update) < WEATHER_UPDATE_INTERVAL:
            return self.cached_data

        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={SEJONG_LAT}&longitude={SEJONG_LON}"
                f"&current=temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m"
            )
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10, context=self.ssl_context) as response:
                data = json.loads(response.read().decode())

            temp = data["current"]["temperature_2m"]
            weather_code = data["current"]["weather_code"]
            wind_speed = data["current"].get("wind_speed_10m", 0)

            state, desc = self._map_weather_code(weather_code, wind_speed)
            self.cached_data = WeatherData(temp, state, desc)
            self.last_update = current_time
            return self.cached_data

        except Exception as e:
            # Fallback to default weather if API fails
            if not self.cached_data:
                self.cached_data = WeatherData(20.0, WeatherState.SUNNY, "Clear")
            return self.cached_data

    def _map_weather_code(self, code: int, wind_speed: float) -> Tuple[WeatherState, str]:
        if wind_speed > 40:
            return WeatherState.WIND, "Windy"
        if code in [0, 1]:
            return WeatherState.SUNNY, "Clear"
        if code in [2, 3]:
            return WeatherState.CLOUDY, "Cloudy"
        if code in [45, 48]:
            return WeatherState.CLOUDY, "Foggy"
        if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            return WeatherState.RAIN, "Rainy"
        if code in [71, 73, 75, 77, 85, 86]:
            return WeatherState.SNOW, "Snowy"
        if code in [95, 96, 99]:
            return WeatherState.THUNDER, "Thunderstorm"
        return WeatherState.CLOUDY, "Cloudy"


# ============================================================================
# ADVANCED SKY RENDERER
# ============================================================================

class SkyRenderer:
    """Renders animated sky with advanced effects."""

    def __init__(self):
        self.rain_drops: List[List[float]] = []
        self.snow_flakes: List[List[float]] = []
        self.stars: List[List[float]] = []
        self.clouds: List[dict] = []
        self.lightning_flash = 0

    def _init_stars(self, width: int, height: int):
        """Initialize star positions."""
        if not self.stars:
            self.stars = [
                [random.randint(0, width - 1), random.randint(0, height - 1), random.random()]
                for _ in range(50)
            ]

    def _init_rain(self, width: int, height: int):
        """Initialize rain drops."""
        if len(self.rain_drops) < 100:
            self.rain_drops = [
                [random.uniform(0, width), random.uniform(0, height), random.uniform(0.5, 2.0)]
                for _ in range(100)
            ]

    def _init_snow(self, width: int, height: int):
        """Initialize snow flakes."""
        if len(self.snow_flakes) < 60:
            self.snow_flakes = [
                [random.uniform(0, width), random.uniform(0, height), random.uniform(0.2, 0.8)]
                for _ in range(60)
            ]

    def _init_clouds(self, width: int):
        """Initialize clouds."""
        if not self.clouds:
            self.clouds = [
                {'x': random.randint(0, width), 'y': random.randint(1, 4), 'speed': random.uniform(0.1, 0.3), 'type': random.randint(0, 2)}
                for _ in range(5)
            ]

    def render(self, stdscr, weather: WeatherState, width: int, height: int, frame: int):
        """Render sky based on weather."""
        if weather == WeatherState.SUNNY:
            self._render_sunny(stdscr, width, height, frame)
        elif weather == WeatherState.CLOUDY:
            self._render_cloudy(stdscr, width, height, frame)
        elif weather == WeatherState.RAIN:
            self._render_rain(stdscr, width, height, frame)
        elif weather == WeatherState.SNOW:
            self._render_snow(stdscr, width, height, frame)
        elif weather == WeatherState.WIND:
            self._render_wind(stdscr, width, height, frame)
        elif weather == WeatherState.THUNDER:
            self._render_thunder(stdscr, width, height, frame)

    def _safe_addstr(self, stdscr, y: int, x: int, text: str, attr=0):
        try:
            max_y, max_x = stdscr.getmaxyx()
            if 0 <= y < max_y - 1 and 0 <= x < max_x - 1:
                available = max_x - x - 1
                if available > 0:
                    stdscr.addstr(y, x, text[:available], attr)
        except curses.error:
            pass

    def _render_sunny(self, stdscr, width: int, height: int, frame: int):
        """Render bright sunny sky with animated sun."""
        self._init_stars(width, height)

        # Animated sun with rays
        sun_frames = [
            [
                "       \\   |   /       ",
                "         .-'-.         ",
                "    ----( O O )----    ",
                "         `-.-'         ",
                "       /   |   \\       ",
            ],
            [
                "        \\ | /         ",
                "      -.  _  .-        ",
                "    ----(   )----      ",
                "      -'  -  '-        ",
                "        / | \\         ",
            ],
        ]
        sun = sun_frames[(frame // 10) % 2]
        sun_x = width // 2 - 12
        sun_y = 1

        for i, line in enumerate(sun):
            self._safe_addstr(stdscr, sun_y + i, sun_x, line, curses.color_pair(30) | curses.A_BOLD)

        # Twinkling stars in background
        for star in self.stars:
            star[2] += 0.1
            if random.random() < 0.1:
                x, y = int(star[0]), int(star[1])
                brightness = (math.sin(star[2]) + 1) / 2
                char = "+" if brightness > 0.7 else ("*" if brightness > 0.3 else ".")
                attr = curses.A_BOLD if brightness > 0.5 else curses.A_DIM
                self._safe_addstr(stdscr, y, x, char, curses.color_pair(30) | attr)

    def _render_cloudy(self, stdscr, width: int, height: int, frame: int):
        """Render moving clouds."""
        self._init_clouds(width)

        cloud_shapes = [
            ["    .-~~~-.    ", "  .~       ~.  ", " (           ) ", "  `~-------~'  "],
            ["   .---.   ", "  (     )  ", " (       ) ", "  `-----'  "],
            ["      .-.      ", "    (   )     ", "   (     )    ", "    `---'     "],
        ]

        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > width + 20:
                cloud['x'] = -20
            shape = cloud_shapes[cloud['type'] % len(cloud_shapes)]
            for i, line in enumerate(shape):
                self._safe_addstr(stdscr, cloud['y'] + i, int(cloud['x']), line, curses.color_pair(31) | curses.A_BOLD)

    def _render_rain(self, stdscr, width: int, height: int, frame: int):
        """Render heavy rain with splashes."""
        self._init_rain(width, height)
        self._init_clouds(width)

        # Dark clouds first
        for cloud in self.clouds[:2]:
            cloud['x'] += cloud['speed'] * 0.5
            if cloud['x'] > width + 20:
                cloud['x'] = -20
            self._safe_addstr(stdscr, int(cloud['y']), int(cloud['x']), "▓▓▓▒▒▒░░░▒▒▒▓▓▓", curses.color_pair(32))

        # Rain drops
        rain_chars = ["│", "┃", "╽", "|", "¦"]
        for drop in self.rain_drops:
            drop[1] += drop[2]
            drop[0] += random.uniform(-0.1, 0.1)
            if drop[1] > height:
                drop[1] = random.uniform(-5, 0)
                drop[0] = random.uniform(0, width)
            x, y = int(drop[0]), int(drop[1])
            if 0 <= y < height:
                char = random.choice(rain_chars)
                self._safe_addstr(stdscr, y, x, char, curses.color_pair(33))
                # Splash at bottom
                if y == height - 1:
                    splash = random.choice(["*", "~", "°"])
                    self._safe_addstr(stdscr, y, x, splash, curses.color_pair(33) | curses.A_BOLD)

    def _render_snow(self, stdscr, width: int, height: int, frame: int):
        """Render gentle snowfall."""
        self._init_snow(width, height)

        snow_chars = ["❄", "❅", "❆", "*", ".", "°", "•"]
        for flake in self.snow_flakes:
            flake[1] += flake[2]
            flake[0] += math.sin(frame * 0.1 + flake[0]) * 0.3  # Gentle swaying
            if flake[1] > height:
                flake[1] = random.uniform(-3, 0)
                flake[0] = random.uniform(0, width)
            x, y = int(flake[0]) % width, int(flake[1])
            if 0 <= y < height:
                char = random.choice(snow_chars)
                self._safe_addstr(stdscr, y, x, char, curses.color_pair(31) | curses.A_BOLD)

        # Snow accumulation hint at bottom
        if frame % 20 < 10:
            snow_ground = "░" * width
            self._safe_addstr(stdscr, height - 1, 0, snow_ground[:width-1], curses.color_pair(31))

    def _render_wind(self, stdscr, width: int, height: int, frame: int):
        """Render windy animation with particles."""
        wind_chars = ["~", "≈", "∿", "〜", "～", "⌇"]
        data_packets = ["[01]", "{AI}", "<DB>", "[ML]", "◈◈", "▸▸"]

        # Wind streaks
        for i in range(height):
            offset = (frame * 3 + i * 7) % (width + 30) - 15
            streak = "".join(random.choices(wind_chars, k=random.randint(3, 8)))
            self._safe_addstr(stdscr, i, offset, streak, curses.color_pair(34))

        # Flying data packets
        for i, packet in enumerate(data_packets):
            px = (frame * 5 + i * 25) % (width + 30) - 15
            py = 2 + (i * 2) % (height - 4)
            self._safe_addstr(stdscr, py, px, packet, curses.color_pair(35) | curses.A_BOLD)

    def _render_thunder(self, stdscr, width: int, height: int, frame: int):
        """Render thunderstorm with lightning."""
        # Rain base
        self._render_rain(stdscr, width, height, frame)

        # Lightning flash
        if frame % 50 < 3:
            self.lightning_flash = 5
        if self.lightning_flash > 0:
            self.lightning_flash -= 1
            # Draw lightning bolt
            lightning_x = random.randint(10, width - 10)
            bolt = ["  ⚡  ", " ╲│╱ ", "  │  ", " ╱│╲ ", "  ⚡  "]
            for i, line in enumerate(bolt):
                self._safe_addstr(stdscr, i, lightning_x, line, curses.color_pair(30) | curses.A_BOLD)


# ============================================================================
# PROFESSIONAL LOGO RENDERER
# ============================================================================

class LogoRenderer:
    """Renders the KDI School Data Unit 2 logo with professional effects."""

    def __init__(self):
        self.glow_offset = 0

    def render(self, stdscr, center_y: int, width: int, height: int, frame: int):
        """Render the logo with effects."""
        # Choose appropriate logo based on terminal size
        if width >= 80:
            logo = LOGO_STYLISH
        else:
            logo = LOGO_COMPACT

        logo_width = max(len(line) for line in logo)
        logo_height = len(logo)
        start_x = max(0, (width - logo_width) // 2)
        start_y = max(0, center_y - logo_height // 2)

        max_y, max_x = stdscr.getmaxyx()

        # Color cycling effect
        colors = [40, 41, 42, 43, 44]
        main_color = colors[(frame // 20) % len(colors)]

        # Glow effect - draw shadow first
        self.glow_offset = math.sin(frame * 0.1) * 0.5

        for i, line in enumerate(logo):
            y = start_y + i
            if 0 <= y < max_y - 1:
                x = start_x
                # Main logo
                try:
                    # Pulsing brightness
                    pulse = (math.sin(frame * 0.15) + 1) / 2
                    attr = curses.A_BOLD if pulse > 0.5 else curses.A_NORMAL
                    if x + len(line) < max_x:
                        stdscr.addstr(y, x, line, curses.color_pair(main_color) | attr)
                except curses.error:
                    pass

        # Animated underline
        underline_y = start_y + logo_height + 1
        if underline_y < max_y - 1:
            # Animated gradient line
            gradient_chars = "░▒▓█▓▒░"
            line_width = min(logo_width, max_x - start_x - 2)
            underline = ""
            for i in range(line_width):
                idx = (i + frame) % len(gradient_chars)
                underline += gradient_chars[idx]
            try:
                stdscr.addstr(underline_y, start_x, underline, curses.color_pair(45))
            except curses.error:
                pass


# ============================================================================
# STORY ENGINE
# ============================================================================

class StoryEngine:
    def __init__(self):
        self.chapters = STORY_CHAPTERS
        self.current_chapter = 0
        self.chapter_start_time = time.time()

    def update(self) -> int:
        elapsed = time.time() - self.chapter_start_time
        if elapsed >= CHAPTER_DURATION:
            self.current_chapter = (self.current_chapter + 1) % len(self.chapters)
            self.chapter_start_time = time.time()
        return self.current_chapter

    def get_current_text(self, width: int) -> List[str]:
        text = self.chapters[self.current_chapter]
        wrapped_lines = []
        for paragraph in text.split('\n'):
            if paragraph.strip():
                wrapped = textwrap.wrap(paragraph.strip(), width=width - 6)
                wrapped_lines.extend(wrapped)
            else:
                wrapped_lines.append("")
        return wrapped_lines

    def get_progress(self) -> float:
        elapsed = time.time() - self.chapter_start_time
        return min(1.0, elapsed / CHAPTER_DURATION)


# ============================================================================
# ADVANCED STORY ANIMATION RENDERER
# ============================================================================

class StoryAnimationRenderer:
    """Renders spectacular chapter-specific animations."""

    def __init__(self):
        self.particles = ParticleSystem(150)

    def render(self, stdscr, chapter: int, y_start: int, width: int, height: int, frame: int):
        max_y, max_x = stdscr.getmaxyx()

        # Update and render particles
        self.particles.update()
        self.particles.render(stdscr, max_y, max_x)

        # Chapter-specific animations
        if chapter == 0:
            self._render_starfall(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 1:
            self._render_dancing_data(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 2:
            self._render_data_tsunami(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 3:
            self._render_heroes_entrance(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 4:
            self._render_transformation(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 5:
            self._render_dragon_battle(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 6:
            self._render_stardust_shield(stdscr, y_start, width, frame, max_y, max_x)
        elif chapter == 7:
            self._render_lighthouse_beacon(stdscr, y_start, width, frame, max_y, max_x)
        else:
            self._render_finale(stdscr, y_start, width, frame, max_y, max_x)

    def _safe_addstr(self, stdscr, y, x, text, attr, max_y, max_x):
        try:
            if 0 <= y < max_y - 1 and 0 <= x < max_x - 1:
                available = max_x - x - 1
                if available > 0:
                    stdscr.addstr(y, x, text[:available], attr)
        except curses.error:
            pass

    def _render_starfall(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 1: Spectacular starfall effect."""
        # Emit star particles
        if frame % 5 == 0:
            self.particles.emit(
                random.randint(10, width - 10), y_start - 2, 3,
                "★☆✦✧⋆", 50,
                vx_range=(-0.5, 0.5), vy_range=(0.3, 0.8)
            )

        # Constellation pattern
        constellation = [
            "    ★         ☆    ",
            "  ☆   ★   ★       ",
            "      ☆       ★   ",
            "   ★      ☆       ",
        ]
        offset = int(math.sin(frame * 0.05) * 3)
        for i, line in enumerate(constellation):
            x = (width // 2 - 10) + offset
            self._safe_addstr(stdscr, y_start + i, x, line, curses.color_pair(50) | curses.A_BOLD, max_y, max_x)

    def _render_dancing_data(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 2: Dancing data blocks and numbers."""
        blocks = ["[CSV]", "[LOG]", "[JSON]", "[SQL]", "[API]", "{ }"]
        numbers = "0123456789"

        for i, block in enumerate(blocks):
            # Bouncing motion
            bounce_y = int(math.sin(frame * 0.2 + i) * 2)
            bounce_x = int(math.cos(frame * 0.15 + i * 0.5) * 3)
            x = 10 + i * 12 + bounce_x
            y = y_start + 1 + bounce_y
            color = 51 + (i % 3)
            self._safe_addstr(stdscr, y, x, block, curses.color_pair(color) | curses.A_BOLD, max_y, max_x)

        # Floating numbers
        for i in range(8):
            x = (frame * 2 + i * 11) % width
            y = y_start + (i % 3)
            num = numbers[(frame + i) % 10]
            self._safe_addstr(stdscr, y, x, num, curses.color_pair(52) | curses.A_DIM, max_y, max_x)

    def _render_data_tsunami(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 3: Data wave/tsunami effect."""
        # Multiple wave layers
        for layer in range(4):
            wave_chars = "≋≈∿~" if layer < 2 else "░▒▓█"
            phase = frame * 0.3 + layer * 0.5
            for x in range(width - 2):
                wave_height = int(math.sin(x * 0.1 + phase) * 2 + math.sin(x * 0.05 + phase * 0.7) * 1)
                y = y_start + layer + wave_height
                if 0 <= y < max_y - 1:
                    char = wave_chars[int((x + frame) * 0.5) % len(wave_chars)]
                    color = 54 if layer < 2 else 55
                    attr = curses.A_BOLD if layer == 0 else curses.A_DIM
                    self._safe_addstr(stdscr, y, x, char, curses.color_pair(color) | attr, max_y, max_x)

        # Data debris in waves
        debris = ["[err]", "???", "!!!", "log", "data"]
        for i, d in enumerate(debris):
            x = (frame * 3 + i * 17) % (width + 20) - 10
            y = y_start + 1 + (i % 3)
            self._safe_addstr(stdscr, y, x, d, curses.color_pair(56) | curses.A_BOLD, max_y, max_x)

    def _render_heroes_entrance(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 4: Heroes walking in with effects."""
        heroes = [
            ("  ╔═╗  ", "  ║●║  ", "  ╠═╣  ", " ╔╝ ╚╗ "),  # Hero 1
            ("  ┌─┐  ", "  │◉│  ", "  ├─┤  ", " ┌┘ └┐ "),  # Hero 2
            ("  ╭─╮  ", "  │★│  ", "  ╞═╡  ", " ╱   ╲ "),  # Hero 3
        ]

        # Tool icons floating above heroes
        tools = ["⚡ETL", "🔍QA", "🛡️AI"]

        for i, hero in enumerate(heroes):
            # Slide in from left
            target_x = 15 + i * 25
            current_x = min(target_x, (frame * 2 - i * 20))
            if current_x < -10:
                continue

            # Hero body
            for j, line in enumerate(hero):
                self._safe_addstr(stdscr, y_start + j, current_x, line, curses.color_pair(57) | curses.A_BOLD, max_y, max_x)

            # Floating tool above
            if current_x >= target_x - 5:
                tool_y = y_start - 1 + int(math.sin(frame * 0.2 + i) * 0.5)
                self._safe_addstr(stdscr, tool_y, current_x + 1, tools[i], curses.color_pair(58) | curses.A_BOLD, max_y, max_x)

                # Sparkle effect
                if frame % 10 < 3:
                    self.particles.emit(current_x + 3, y_start - 1, 2, "✦✧★", 50)

    def _render_transformation(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 5: Chaos transforming to order."""
        chaos_chars = "@#$%&*!?~^+=<>{}[]|\\/"
        order_elements = ["│DATA│", "│GRAPH│", "│TABLE│", "│CHART│"]

        # Calculate transformation progress
        progress = (frame % 60) / 60.0

        if progress < 0.5:
            # Chaos phase
            for i in range(15):
                x = random.randint(5, width - 15)
                y = y_start + random.randint(0, 3)
                char = random.choice(chaos_chars)
                self._safe_addstr(stdscr, y, x, char, curses.color_pair(59) | curses.A_BOLD, max_y, max_x)
        else:
            # Order phase
            for i, elem in enumerate(order_elements):
                x = 10 + i * 18
                y = y_start + 1
                # Fade in effect
                attr = curses.A_BOLD if progress > 0.7 else curses.A_DIM
                self._safe_addstr(stdscr, y, x, elem, curses.color_pair(60) | attr, max_y, max_x)

                # Connecting lines
                if i < len(order_elements) - 1:
                    self._safe_addstr(stdscr, y, x + len(elem), "──►", curses.color_pair(60), max_y, max_x)

    def _render_dragon_battle(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 6: Dragon battle with fire effects."""
        dragon = [
            "      __    __    ",
            "     /  \\__/  \\   ",
            "    | ◉    ◉ |   ",
            "     \\  口  /    ",
            "   ~~~\\____/~~~  ",
            "      /    \\     ",
        ]

        dragon_x = width // 2 - 20
        for i, line in enumerate(dragon):
            self._safe_addstr(stdscr, y_start + i, dragon_x, line, curses.color_pair(61) | curses.A_BOLD, max_y, max_x)

        # Fire breath
        fire_chars = ["▸", "►", "▶", "◈", "◆", "●"]
        if frame % 3 == 0:
            for i in range(5):
                fire_x = dragon_x + 18 + i * 2
                fire_y = y_start + 3 + random.randint(-1, 1)
                char = random.choice(fire_chars)
                self._safe_addstr(stdscr, fire_y, fire_x, char, curses.color_pair(62) | curses.A_BOLD, max_y, max_x)
                self.particles.emit(fire_x, fire_y, 1, "●◉○", 62, vx_range=(0.5, 1.5), vy_range=(-0.3, 0.3))

        # Shield on the right
        shield = [
            "   ╔═══╗   ",
            "  ╔╝ ◇ ╚╗  ",
            "  ║ AI  ║  ",
            "  ╚╗   ╔╝  ",
            "   ╚═══╝   ",
        ]
        shield_x = width // 2 + 15
        for i, line in enumerate(shield):
            pulse = curses.A_BOLD if (frame // 5) % 2 == 0 else curses.A_NORMAL
            self._safe_addstr(stdscr, y_start + i, shield_x, line, curses.color_pair(63) | pulse, max_y, max_x)

    def _render_stardust_shield(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 7: Stardust and protection effect."""
        # Emit stardust particles
        if frame % 3 == 0:
            self.particles.emit(
                width // 2, y_start + 2, 5,
                "★☆✦✧⋆◇◆", 64,
                vx_range=(-1.5, 1.5), vy_range=(-1, 1)
            )

        # Safe icons appearing
        safe_icons = ["[SAFE]", "[OK]", "[PASS]", "[SECURE]", "[✓]"]
        for i, icon in enumerate(safe_icons):
            angle = (frame * 0.1 + i * 1.2)
            radius = 8 + math.sin(frame * 0.05) * 2
            x = int(width // 2 + math.cos(angle) * radius * 2)
            y = int(y_start + 2 + math.sin(angle) * radius * 0.5)
            self._safe_addstr(stdscr, y, x, icon, curses.color_pair(65) | curses.A_BOLD, max_y, max_x)

    def _render_lighthouse_beacon(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapter 8: Lighthouse with rotating beacon."""
        lighthouse = [
            "       ╔═╗       ",
            "      ╔╝ ╚╗      ",
            "     ╔╝   ╚╗     ",
            "    ╔╝ ◈◈◈ ╚╗    ",
            "   ╔╝       ╚╗   ",
            "  ╔╝░░░░░░░░░╚╗  ",
            " ╔╝░░░░░░░░░░░╚╗ ",
            " ╚═════════════╝ ",
        ]

        lh_x = width // 2 - 9
        for i, line in enumerate(lighthouse):
            self._safe_addstr(stdscr, y_start + i - 3, lh_x, line, curses.color_pair(66) | curses.A_BOLD, max_y, max_x)

        # Rotating light beam
        beam_angle = (frame * 0.15) % (2 * math.pi)
        beam_chars = "═══════════►"
        beam_length = 15

        for i in range(beam_length):
            bx = int(lh_x + 9 + math.cos(beam_angle) * i * 2)
            by = int(y_start + math.sin(beam_angle) * i * 0.5)
            if 0 <= by < max_y - 1 and 0 <= bx < max_x - 1:
                brightness = 1 - (i / beam_length)
                char = "█" if brightness > 0.7 else ("▓" if brightness > 0.4 else "░")
                self._safe_addstr(stdscr, by, bx, char, curses.color_pair(67) | curses.A_BOLD, max_y, max_x)

    def _render_finale(self, stdscr, y_start, width, frame, max_y, max_x):
        """Chapters 9-10: Grand finale with combined effects."""
        # Continuous particle emission
        if frame % 2 == 0:
            self.particles.emit(
                random.randint(10, width - 10), y_start, 2,
                "★☆✦✧⋆●◉○◈◆", random.choice([50, 64, 65, 67]),
                vx_range=(-0.5, 0.5), vy_range=(-0.5, 0.5)
            )

        # Pulsing message
        message = "━━━ DATA UNIT 2: Where Data Becomes Insight ━━━"
        msg_x = (width - len(message)) // 2
        pulse_attr = curses.A_BOLD if (frame // 8) % 2 == 0 else curses.A_DIM
        self._safe_addstr(stdscr, y_start + 2, msg_x, message, curses.color_pair(68) | pulse_attr, max_y, max_x)

        # Animated border
        border_chars = "◆◇◈○●◉"
        for i in range(width // 4):
            x = (i * 4 + frame) % width
            char = border_chars[(i + frame // 3) % len(border_chars)]
            self._safe_addstr(stdscr, y_start, x, char, curses.color_pair(69), max_y, max_x)
            self._safe_addstr(stdscr, y_start + 4, x, char, curses.color_pair(69), max_y, max_x)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class DataUnit2Banner:
    """Main application with professional design."""

    def __init__(self):
        self.weather_client = WeatherClient()
        self.sky_renderer = SkyRenderer()
        self.logo_renderer = LogoRenderer()
        self.story_engine = StoryEngine()
        self.story_animation = StoryAnimationRenderer()
        self.aurora: Optional[AuroraWave] = None
        self.frame = 0
        self.last_size = (0, 0)

    def _init_colors(self):
        """Initialize all color pairs."""
        curses.start_color()
        curses.use_default_colors()

        # Force black background
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Aurora colors (beautiful gradient)
        curses.init_pair(80, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Aurora cyan
        curses.init_pair(81, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Aurora blue
        curses.init_pair(82, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Aurora magenta
        curses.init_pair(83, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Aurora green
        curses.init_pair(84, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Aurora white/sparkle

        # Weather colors
        curses.init_pair(30, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Sun
        curses.init_pair(31, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Clouds/Snow
        curses.init_pair(32, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Dark clouds
        curses.init_pair(33, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Rain
        curses.init_pair(34, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Wind
        curses.init_pair(35, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Wind data

        # Logo colors (cycling)
        curses.init_pair(40, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(41, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(42, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(43, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(44, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(45, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Underline

        # Animation colors
        curses.init_pair(50, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Stars
        curses.init_pair(51, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Data blocks
        curses.init_pair(52, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Numbers
        curses.init_pair(53, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(54, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Waves
        curses.init_pair(55, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Wave details
        curses.init_pair(56, curses.COLOR_RED, curses.COLOR_BLACK)     # Debris
        curses.init_pair(57, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Heroes
        curses.init_pair(58, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Tools
        curses.init_pair(59, curses.COLOR_RED, curses.COLOR_BLACK)     # Chaos
        curses.init_pair(60, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Order
        curses.init_pair(61, curses.COLOR_RED, curses.COLOR_BLACK)     # Dragon
        curses.init_pair(62, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Fire
        curses.init_pair(63, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Shield
        curses.init_pair(64, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Stardust
        curses.init_pair(65, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Safe icons
        curses.init_pair(66, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Lighthouse
        curses.init_pair(67, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Beacon
        curses.init_pair(68, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Finale message
        curses.init_pair(69, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Finale border

        # UI colors
        curses.init_pair(70, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Text
        curses.init_pair(71, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Progress bar
        curses.init_pair(72, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Weather info

    def _draw_frame_border(self, stdscr, height: int, width: int, frame: int):
        """Draw animated frame border."""
        # Corner pieces
        corners = ["╔", "╗", "╚", "╝"]
        h_line = "═"
        v_line = "║"

        # Animated corner characters
        animated_corners = ["◆", "◇", "◈", "○"]
        corner_char = animated_corners[(frame // 10) % len(animated_corners)]

        try:
            # Top border
            stdscr.addstr(0, 0, corners[0], curses.color_pair(45) | curses.A_BOLD)
            stdscr.addstr(0, width - 2, corners[1], curses.color_pair(45) | curses.A_BOLD)
            for x in range(1, width - 2):
                char = corner_char if (x + frame // 5) % 20 == 0 else h_line
                stdscr.addstr(0, x, char, curses.color_pair(45))

            # Bottom border
            stdscr.addstr(height - 2, 0, corners[2], curses.color_pair(45) | curses.A_BOLD)
            for x in range(1, width - 2):
                char = corner_char if (x + frame // 5) % 20 == 0 else h_line
                stdscr.addstr(height - 2, x, char, curses.color_pair(45))

            # Side borders
            for y in range(1, height - 2):
                stdscr.addstr(y, 0, v_line, curses.color_pair(45))
                if width > 2:
                    stdscr.addstr(y, width - 2, v_line, curses.color_pair(45))

        except curses.error:
            pass

    def _draw_status_bar(self, stdscr, height: int, width: int, weather: WeatherData, chapter: int, progress: float):
        """Draw bottom status bar."""
        try:
            # Weather info (left)
            weather_icons = {
                WeatherState.SUNNY: "☀",
                WeatherState.CLOUDY: "☁",
                WeatherState.RAIN: "🌧",
                WeatherState.SNOW: "❄",
                WeatherState.WIND: "💨",
                WeatherState.THUNDER: "⚡",
            }
            icon = weather_icons.get(weather.state, "●")
            weather_str = f" {icon} Sejong: {weather.temperature:.1f}°C {weather.description} "
            stdscr.addstr(height - 3, 2, weather_str, curses.color_pair(72) | curses.A_BOLD)

            # Progress bar (center)
            bar_width = width - 40
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            bar_x = 20
            stdscr.addstr(height - 3, bar_x, f"[{bar}]", curses.color_pair(71))

            # Chapter info (right)
            chapter_str = f" Chapter {chapter + 1}/10 "
            stdscr.addstr(height - 3, width - len(chapter_str) - 3, chapter_str, curses.color_pair(70) | curses.A_BOLD)

            # Quit hint
            quit_str = " Press 'q' to quit "
            stdscr.addstr(height - 4, width - len(quit_str) - 3, quit_str, curses.color_pair(70) | curses.A_DIM)

        except curses.error:
            pass

    def run(self, stdscr):
        """Main application loop."""
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(1000 // FPS)

        if curses.has_colors():
            self._init_colors()

        # Set black background
        stdscr.bkgd(' ', curses.color_pair(1))

        while True:
            try:
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break

                height, width = stdscr.getmaxyx()

                # Handle resize
                if (height, width) != self.last_size:
                    self.last_size = (height, width)
                    if self.aurora:
                        self.aurora.resize(width, height)
                    else:
                        self.aurora = AuroraWave(width, height)
                    stdscr.clear()

                if height < 25 or width < 80:
                    stdscr.clear()
                    msg = "Terminal too small! Need 80x25 minimum."
                    stdscr.addstr(height // 2, max(0, (width - len(msg)) // 2), msg, curses.color_pair(70))
                    stdscr.refresh()
                    time.sleep(0.1)
                    continue

                # Clear screen
                stdscr.erase()

                # Layout zones
                sky_height = height // 5
                logo_center_y = height // 3 + 2
                story_start_y = int(height * 0.65)
                animation_y = story_start_y - 6

                # Get data
                weather_data = self.weather_client.get_weather()
                chapter = self.story_engine.update()
                progress = self.story_engine.get_progress()

                # Render aurora background (subtle)
                if self.aurora:
                    self.aurora.update()
                    self.aurora.render(stdscr, height, width, intensity=0.4)

                # Render frame border
                self._draw_frame_border(stdscr, height, width, self.frame)

                # Render sky
                self.sky_renderer.render(stdscr, weather_data.state, width - 4, sky_height, self.frame)

                # Render logo
                self.logo_renderer.render(stdscr, logo_center_y, width, height, self.frame)

                # Render story animation
                self.story_animation.render(stdscr, chapter, animation_y, width, height, self.frame)

                # Render story text
                story_lines = self.story_engine.get_current_text(width - 8)
                for i, line in enumerate(story_lines):
                    y = story_start_y + i
                    if y < height - 5:
                        try:
                            stdscr.addstr(y, 4, line, curses.color_pair(70))
                        except curses.error:
                            pass

                # Render status bar
                self._draw_status_bar(stdscr, height, width, weather_data, chapter, progress)

                stdscr.refresh()
                self.frame += 1

            except curses.error:
                pass
            except KeyboardInterrupt:
                break


def main():
    try:
        app = DataUnit2Banner()
        curses.wrapper(app.run)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n" + "=" * 60)
        print("  Thank you for visiting KDI School, Data Unit 2!")
        print("  \"Where data becomes insight, and insight becomes policy.\"")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
