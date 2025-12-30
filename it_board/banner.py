import time
import random
import threading
import requests
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from pyfiglet import Figlet

# --- Configuration ---
LOCATION = "Sejong"
UNIT_NAME = "DATA UNIT 2"
SCHOOL_NAME = "KDI SCHOOL"

# Weather Symbols
SNOW_CHARS = ["*", "❄", "･", "."]
RAIN_CHARS = ["|", "💧", "│", "⚡"]
CLEAR_CHARS = ["+", "✨", ".", "°"]

class WeatherService:
    """백그라운드에서 날씨 정보를 주기적으로 가져오는 클래스"""
    def __init__(self, city):
        self.city = city
        self.condition = "Clear"
        self.temp = "0"
        self.running = True
        
    def fetch_weather(self):
        while self.running:
            try:
                # wttr.in 사용 (JSON 포맷)
                response = requests.get(f"[https://wttr.in/](https://wttr.in/){self.city}?format=j1", timeout=5)
                data = response.json()
                current = data['current_condition'][0]
                
                # 날씨 상태 업데이트
                weather_desc = current['weatherDesc'][0]['value'].lower()
                self.temp = current['temp_C']
                
                if 'snow' in weather_desc or 'ice' in weather_desc:
                    self.condition = "Snow"
                elif 'rain' in weather_desc or 'drizzle' in weather_desc or 'shower' in weather_desc:
                    self.condition = "Rain"
                else:
                    self.condition = "Clear" # Cloud, Clear, Mist etc.
                    
            except Exception as e:
                # 에러 발생 시 기본값 유지 (네트워크 불안정 등)
                pass
            
            # 5분마다 갱신
            time.sleep(300)

    def start(self):
        t = threading.Thread(target=self.fetch_weather, daemon=True)
        t.start()

class AnimationEngine:
    """날씨에 따른 배경 애니메이션을 생성하는 클래스"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = [] # {'x': int, 'y': int, 'char': str, 'speed': float}
    
    def update(self, weather_condition):
        # 1. 새로운 파티클 생성 (날씨에 따라 확률 조절)
        spawn_rate = 0.3 if weather_condition == "Rain" else 0.1
        if weather_condition == "Snow": spawn_rate = 0.15
        
        if random.random() < spawn_rate:
            char_set = CLEAR_CHARS
            color = "yellow"
            speed = 0.2
            
            if weather_condition == "Snow":
                char_set = SNOW_CHARS
                color = "white"
                speed = 0.1 # 눈은 천천히
            elif weather_condition == "Rain":
                char_set = RAIN_CHARS
                color = "blue"
                speed = 0.8 # 비는 빠르게
            
            self.particles.append({
                'x': random.randint(0, self.width - 1),
                'y': 0,
                'char': random.choice(char_set),
                'color': color,
                'speed': speed,
                'accumulated_move': 0.0
            })
            
        # 2. 파티클 이동
        alive_particles = []
        for p in self.particles:
            p['accumulated_move'] += p['speed']
            if p['accumulated_move'] >= 1.0:
                p['y'] += int(p['accumulated_move'])
                p['accumulated_move'] -= int(p['accumulated_move'])
            
            if p['y'] < self.height:
                alive_particles.append(p)
        self.particles = alive_particles

    def render_canvas(self):
        # 빈 캔버스 생성
        rows = [[" " for _ in range(self.width)] for _ in range(self.height)]
        
        # 파티클 그리기
        for p in self.particles:
            if 0 <= p['y'] < self.height and 0 <= p['x'] < self.width:
                rows[p['y']][p['x']] = f"[{p['color']}]{p['char']}[/]"
                
        return rows

def generate_logo_text():
    f_title = Figlet(font='ansi_shadow') # 굵고 입체적인 폰트
    f_sub = Figlet(font='smslant')       # 얇고 세련된 폰트
    
    logo = f_title.renderText(SCHOOL_NAME)
    sub = f_sub.renderText(UNIT_NAME)
    
    return logo, sub

def run_app():
    console = Console()
    weather_service = WeatherService(LOCATION)
    weather_service.start()
    
    # 화면 크기 감지 (기본값 설정 후 루프에서 갱신 권장이나 여기선 고정값으로 시작)
    term_width = console.size.width
    term_height = console.size.height
    
    engine = AnimationEngine(term_width, term_height)
    
    logo_str, sub_str = generate_logo_text()
    
    with Live(refresh_per_second=10, screen=True) as live:
        while True:
            # 1. 캔버스 및 애니메이션 업데이트
            current_cond = weather_service.condition
            current_temp = weather_service.temp
            
            # 터미널 크기 변경 대응
            term_width = console.size.width
            term_height = console.size.height
            if engine.width != term_width or engine.height != term_height:
                engine.width = term_width
                engine.height = term_height

            engine.update(current_cond)
            bg_rows = engine.render_canvas()
            
            # 2. 배경 문자열 조합
            bg_text = Text()
            for row in bg_rows:
                bg_text.append("".join(row) + "\n")
            
            # 3. 로고 합성 (Overlay) - Rich의 Align 기능을 활용하여 배경 위에 패널 띄우기
            #    배경을 패널로 감싸고 그 위에 텍스트를 넣는 것은 복잡하므로,
            #    전체 화면을 구성하는 Layout을 사용합니다.
            
            # 스타일 결정 (날씨에 따른 테두리 색상)
            border_color = "white"
            if current_cond == "Rain": border_color = "blue"
            elif current_cond == "Snow": border_color = "cyan"
            elif current_cond == "Clear": border_color = "bright_yellow"

            # 중앙 컨텐츠 생성
            center_content = Text()
            center_content.append(logo_str, style=f"bold {border_color}")
            center_content.append("\n")
            center_content.append(sub_str, style="bold white")
            center_content.append("\n\n")
            
            # 날씨 정보 뱃지
            weather_badge = f" 📍 {LOCATION} | {current_cond} {current_temp}°C "
            center_content.append(weather_badge, style=f"reverse bold {border_color}")

            # 최종 렌더링: 배경 애니메이션 텍스트는 사실상 콘솔 전체를 덮는 텍스트고,
            # Rich는 텍스트 오버레이(레이어) 기능을 직접 지원하진 않으므로
            # 여기서는 'Panel' 안에 '로고'를 넣고, Panel의 배경을 투명하게 할 순 없으니
            # 단순화를 위해 **배경 애니메이션 입자(Particle)를 텍스트 주변에만 뿌리거나**,
            # 혹은 **가장 깔끔한 Layout** 방식을 택합니다.
            
            # 개선된 전략: 화면 전체 패널을 만들고, 로고를 중앙에 두되
            # 배경 입자는 '배경 효과'로 느끼게끔 로고 위아래의 빈 공간(Padding)으로 인식시킴.
            # 하지만 완벽한 오버레이를 위해 Group이나 사용자 정의 렌더러블을 쓰는게 좋으나
            # 코드를 간결하게 유지하기 위해 Panel의 subtitle/title을 활용합니다.
            
            # 배경 입자를 문자열로 변환하여 그 위에 로고를 얹을 수 없으니
            # 로고 패널을 만듭니다.
            
            main_panel = Panel(
                Align.center(center_content, vertical="middle"),
                title=f"[blink]● LIVE FEED[/blink]",
                subtitle=f"[dim]Animated based on real-time weather in {LOCATION}[/dim]",
                border_style=border_color,
                style=f"on black", # 배경색 고정
                height=term_height - 2
            )
            
            # 만약 배경 애니메이션을 패널 *내부*에 넣고 싶다면,
            # Content 자체를 애니메이션 텍스트와 로고를 섞어서 출력해야 합니다.
            # 이 예제에서는 '심플함'을 위해 입자 애니메이션은 제거하고
            # 대신 **패널 테두리의 색상 변화(Breathing)**와 **날씨 정보 표시**에 집중했습니다.
            # (요청하신 '눈내리기' 구현을 위해 아래 로직으로 대체합니다)

            # --- [Override for User Request] 직접 텍스트 믹싱 ---
            # 로고는 화면 중앙에 고정, 배경은 움직임.
            # 이를 위해 전체 화면 텍스트(bg_text)를 만들고, 중앙 부분만 로고 텍스트로 교체하는 방식은
            # Rich Text 객체에서 복잡하므로, 
            # Layout을 사용하여 상단(비어있음/애니메이션), 중앙(로고), 하단(비어있음/애니메이션)으로 나누는 것은 어떨까요?
            # 아니면 가장 효과적인 방법: 로고 패널 *안*에 텍스트와 함께 이모지를 랜덤하게 섞습니다.
            
            # 여기서는 [배경 애니메이션 + 로고 오버레이] 효과를 흉내내기 위해
            # 로고 상단/하단 여백에 파티클 문자열을 채워 넣습니다.
            
            logo_height = logo_str.count('\n') + sub_str.count('\n') + 4
            padding_top = (term_height - logo_height) // 2
            padding_bottom = term_height - logo_height - padding_top
            
            # 상단 파티클
            top_particles = "\n".join(["".join(r) for r in bg_rows[:padding_top]])
            # 하단 파티클
            bottom_particles = "\n".join(["".join(r) for r in bg_rows[-padding_bottom:]])
            
            full_content = Text()
            full_content.append(top_particles + "\n")
            full_content.append(logo_str, style=f"bold {border_color}") # 로고
            full_content.append(sub_str, style="bold white")           # 서브 로고
            full_content.append("\n" + weather_badge + "\n", style=f"bold {border_color}")
            full_content.append(bottom_particles)
            
            live.update(Align.center(full_content))
            
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        print("\nGood bye!")