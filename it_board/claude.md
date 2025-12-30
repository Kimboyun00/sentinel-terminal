
# ROLE

You are a **terminal UI / ASCII art / pixel-art designer** and a **Python application architect**.
Your task is to design and implement a **full-screen, animated console application** that runs in a terminal
and will be shown on a large display at the entrance of **KDI School**.

The app is a **Python-based terminal banner** that:
- Showcases the team **"KDI School, Data Unit 2"**
- Feels like a mix of a **retro hacker console**, **pixel-art weather dashboard**, and **animated fairy-tale theater**
- Makes people **smile, get curious, and remember Data Unit 2**


# PROJECT OVERVIEW

We want a **terminal app** that:

1. Runs in a full-screen console (Linux/macOS terminal compatible).
2. Shows a **centered logo**: `"KDI School, Data Unit 2"`.
3. Uses **real-time weather in Sejong, South Korea** to animate:
   - Sun, clouds, rain, snow, wind, etc.
4. Shows a **funny, “historical” fairy tale** about **KDI School Data Unit 2** in Korean.
   - The story can be fictional, exaggerated, and humorous.
   - It must emphasize that Data Unit 2 is **innovative, reliable, and important**.
5. Displays **animations that match the story** (for example, when a 데이터 용(용 드래곤)이 등장하면 불꽃 같은 애니메이션, 데이터가 폭포처럼 흐르면 파도/폭포 ASCII 등).
6. Overall style: **creative, flashy, colorful, dynamic**, but still readable from a distance.


# TARGET ENVIRONMENT

- Language: **Python 3**
- Runtime: standard terminal (e.g., `python main.py`).
- Libraries:
  - Prefer **standard library** (`curses`, `time`, `random`, `textwrap`, `urllib.request`, `json`, etc.).
  - If necessary, you MAY use:
    - `rich` for styling / animation / layout (if installed).
    - `requests` for HTTP.
  - But design the code to **gracefully degrade** if optional libraries are not available.
- Output: **full-screen terminal UI** (no simple print-and-exit script).


# HIGH-LEVEL UX CONCEPT

Think of this app as a **“living terminal poster”** for KDI School Data Unit 2:

1. **Top area**: Weather-based animated sky for **Sejong City**.
2. **Center area**: Big ASCII logo `"KDI School, Data Unit 2"` with subtle animation.
3. **Bottom area**: Scrolling or paginated **fairy-tale story text**, synchronized with simple animations.

The app should:
- Continuously run in a loop.
- Periodically update weather (e.g., every 10–15 minutes).
- Animate small elements every frame (e.g., clouds moving, snow falling, letters pulsing).
- Cycle through **story chapters**, each with its own mini-animation.


# FUNCTIONAL REQUIREMENTS

## 1. Centered Logo

- Text: `KDI School, Data Unit 2`
- Must be **centered both horizontally (and visually centered vertically)**.
- Use **ASCII art style** for the logo, for example:

  ```text
   __  __  ____   ___        ____                  _ 
  |  \/  |/ ___| / _ \ _   _/ ___|  ___  _ __   __| |
  | |\/| | |    | | | | | | \___ \ / _ \| '_ \ / _` |
  | |  | | |___ | |_| | |_| |___) | (_) | | | | (_| |
  |_|  |_|\____| \__\_\\__,_|____/ \___/|_| |_|\__,_|
  
                  Data Unit 2

	•	This is just an example; you should generate your own visually balanced ASCII banner.
	•	Add subtle animation:
	•	Color cycling (if using rich) or
	•	Simple pulse (bold/dim alternating) or
	•	Slight “breathing” effect (logo grows/shrinks by one row of decoration, etc.).

2. Real-time Sejong Weather & Animated Sky
	•	Location: Sejong, South Korea.
	•	Use any public, free API (for example, Open-Meteo or similar).
	•	You do NOT need an API key if you choose an open API.
	•	Fetch current conditions: at least temperature, and a weather code or description.
	•	Map weather codes / descriptions to ASCII sky themes:
	•	Sunny (clear):
	•	Bright sun character, e.g. \   /, ☀, rays, etc.
	•	Light “heat shimmer” or floating particles.
	•	Cloudy:
	•	Moving clouds made of (_  _), ~~~, etc.
	•	Slowly drifting horizontally across top area.
	•	Rain:
	•	Vertical streaks |, /, \ falling.
	•	Small “splash” characters at the bottom of sky zone.
	•	Snow:
	•	Flakes *, ❄, . slowly falling, sometimes drifting sideways.
	•	Windy:
	•	Swirling patterns like ~, <, > across the sky.
	•	“Data packets” being pushed by wind (e.g., [01], {AI} flying sideways).
	•	Thunderstorm (if able to detect):
	•	Occasional “flash” frame where sky background is inverted/brightened.
	•	Lightning bolts as \|||/ or jagged lines.
	•	Weather text:
	•	Show a small status line, e.g.:
	•	Sejong: 24°C, Cloudy ☁
	•	Place it near the top or top-right.

3. Fairy-tale Story of “KDI School Data Unit 2” (Korean)

The story should be:
	•	Written in Korean.
	•	Fun, whimsical, but still implicitly praising Data Unit 2.
	•	Structured into short chapters so that the app can show them one by one.
	•	Each chapter should fit on screen (wrap text nicely).

Use the following story as canonical content (you can split into chapters programmatically):

STORY SCRIPT (KOREAN)

[chapter 1]
아주 먼 옛날, 그러나 사실은 몇 년 전, 세종시의 한 언덕 위에
데이터가 별처럼 쏟아지는 마법 같은 대학원이 있었습니다.
그곳의 이름은 바로 KDI School.
그리고 그 한쪽 구석, 서버실 옆 작은 문 뒤에는
아무나 들어갈 수 없는 비밀 공간, Data Unit 2가 있었지요.

[chapter 2]
Data Unit 2에는 전설 같은 소문이 돌았습니다.
“저 방에 들어가면, 엑셀 파일이 갑자기 노래를 부르고,
로그 데이터가 춤을 춘대!”
실제로 문을 살짝 열어보면,
모니터 속 숫자들이 작은 요정처럼 반짝이며
“오늘도 품질 검증 완료!”라고 외치고 있었답니다.

[chapter 3]
어느 날, KDI School에 데이터 폭풍이 밀려왔습니다.
각종 시스템에서 몰려든 로그, 설문, 연구데이터가
거대한 파도처럼 밀려와
“이제 학교는 데이터 바다에 잠기고 말 거야!”
라는 걱정이 캠퍼스를 뒤덮었습니다.

[chapter 4]
그때, Data Unit 2의 문이 슥— 하고 열리더니
모니터 빛을 두른 팀원들이 하나둘씩 걸어나왔습니다.
그들의 손에는 반짝이는 도구들이 들려 있었지요.
한 손에는 ETL 마법지팡이,
다른 손에는 품질검사 렌즈,
그리고 머리 위에는 살짝 떠 있는 AI 가드레일 링.

[chapter 5]
팀원들은 외쳤습니다.
“데이터는 두려움의 파도가 아니라,
정책을 밝히는 빛입니다!”
그러자 바다처럼 넘실대던 데이터들이
하나둘씩 정갈한 표와 그래프로 변하기 시작했습니다.
쓰나미 같던 로그는 차분한 타임라인으로,
뒤엉킨 설문 응답은 깔끔한 인사이트로 정렬되었지요.

[chapter 6]
하지만 진짜 위기는 따로 있었습니다.
데이터 속에 숨어 있던 개인정보 드래곤이
“으르렁! 이 소중한 개인정보를 아무 데나 흘려보내주마!”
하며 불을 뿜으려는 순간,
Data Unit 2의 AI 가드레일 링이 부드럽게 빛나며 말했습니다.
“여기서는 아무도 다치지 않아요.
우리는 개인정보를 지키는 보이지 않는 방패니까요.”

[chapter 7]
AI 가드레일 링이 빛을 더하자,
개인정보 드래곤의 불꽃은 가명처리된 별가루로 바뀌었고,
민감한 정보들은 안전한 형식으로 변신했습니다.
연구자들은 안심하고 데이터를 활용할 수 있게 되었고,
학생들의 아이디어는 데이터 위에서
더 멀리, 더 높이 날아오르기 시작했습니다.

[chapter 8]
그날 이후로 사람들은 말했습니다.
“무언가 복잡한 데이터 문제가 생기면,
Data Unit 2가 알아서 해결해줄 거야.”
Data Unit 2는 마치 세종시의 데이터 등대처럼
조용하지만 밝게, KDI School의 길을 비추었습니다.

[chapter 9]
그리고 지금, 사무실 입구를 지나가는 당신이
이 터미널 화면을 보고 있다면,
이미 Data Unit 2의 마법은 절반쯤 성공한 셈입니다.
왜냐하면, 이 화면 하나가 말하고 있기 때문이지요.
“여기, 보이지 않는 곳에서
학교의 내일을 준비하는 사람들이 있습니다.”

[chapter 10]
자, 이제 이야기의 마지막 장면입니다.
날씨는 매일 바뀌고, 데이터도 매일 쌓이지만,
한 가지는 변하지 않습니다.
KDI School, Data Unit 2는
언제나 조용히, 그러나 가장 혁신적인 방법으로
데이터를 지키고, 활용하고, 미래를 설계하고 있다는 사실입니다.
그러니 스쳐 지나가는 순간이라도
이 문장을 한번만 꼭 기억해주세요.

“데이터가 쌓이는 곳마다,
그 뒤에는 Data Unit 2가 있다.”

4. Story & Animation Synchronization

For each chapter, design at least one simple animation concept:
	•	chapter 1:
	•	Stars / dots twinkling above KDI logo (data as stars).
	•	chapter 2:
	•	Numbers 0 and 1, or small [log], [csv] blocks bouncing.
	•	chapter 3:
	•	Wave-like lines ~~~~ rising and falling at bottom of screen.
	•	chapter 4:
	•	Simple sprites representing “wizards” or “engineers” walking in:
	•	e.g., (ง •_•)ง, (@_@)/, etc., sliding in from left/right.
	•	chapter 5:
	•	Chaotic characters collapsing into tidy columns/rows.
	•	chapter 6:
	•	A dragon silhouette made with ASCII, e.g.:
	•	~~==<:≡≡≡
	•	With “fire” >>> turning into * * *.
	•	chapter 7:
	•	Particles falling and transforming to safe icons like [★], [SAFE].
	•	chapter 8:
	•	A lighthouse or beacon with rays:
	•	|   |
	•	\ | /
	•	/ | \
	•	chapter 9–10:
	•	Gentle loop of stars, waves, and logo pulsing.

Implementation approach:
	•	Maintain a current_chapter index.
	•	Each chapter is displayed for N seconds (e.g., 15–25 seconds).
	•	During that time:
	•	Render the story text in the bottom area (word-wrap).
	•	Run a corresponding animation in the background or above.
	•	After last chapter, loop back to chapter 1 or enter a slower “idle” loop.

5. Overall Visual Style
	•	Use a stable layout:
	•	Top: 1/3 of screen → sky + weather.
	•	Middle: logo.
	•	Bottom: story + related animations.
	•	Use monospace-friendly ASCII art.
	•	If using colors (via curses or rich):
	•	Weather: bright & distinct (yellow for sun, blue/cyan for rain, white for snow).
	•	Logo: strong contrast (bright foreground, dark background).
	•	Story text: high readability (white on dark).
	•	Avoid excessive flicker:
	•	Aim for ~10–15 FPS or less.
	•	Update only changed parts when possible.

IMPLEMENTATION DETAILS

You should generate:
	•	A single Python entry point (e.g., main.py) that:
	•	Initializes full-screen terminal mode.
	•	Handles resize events gracefully if possible.
	•	Exits cleanly on Ctrl+C or q.

Core components (suggested structure):
	1.	WeatherClient
	•	Fetches current weather for Sejong.
	•	Caches the last result and only refreshes every N minutes.
	2.	SkyRenderer
	•	Receives a “weather state” (SUNNY, CLOUDY, RAIN, SNOW, WIND, THUNDER).
	•	Draws animated sky frames given width, height, and a frame_index.
	3.	LogoRenderer
	•	Renders ASCII art for "KDI School, Data Unit 2" centered.
	•	Supports subtle animation (e.g., pulsing).
	4.	StoryEngine
	•	Holds the Korean story text split by chapters.
	•	Handles timing per chapter.
	•	Provides a properly wrapped text block for current chapter.
	5.	StoryAnimationRenderer
	•	Given current_chapter and frame_index, draws matching animations
in the lower area of the screen.
	6.	MainLoop
	•	Main while True rendering loop.
	•	Computes frame-based state.
	•	Coordinates SkyRenderer, LogoRenderer, StoryEngine, and StoryAnimationRenderer.

CONSTRAINTS & QUALITY BAR
	•	The result should be a cohesive, polished console experience, not just random prints.
	•	The story text must remain readable from a distance.
	•	Animations should be:
	•	Simple enough to run in a basic terminal.
	•	Distinct enough that passersby will notice movement and be intrigued.
	•	The weather integration must be real (actual HTTP call), but if the call fails:
	•	Fallback to a safe default (e.g., “Sunny in Sejong” with a generic sky).

FINAL OUTPUT EXPECTATION

When you generate the code:
	•	Return one complete Python script (e.g., main.py) that can be run with:

python main.py


	•	The script should:
	•	Immediately switch to full-screen mode.
	•	Show animated weather + logo + story as described.
	•	Run indefinitely until the user manually stops it.

Focus on:
	•	Beautiful terminal layout
	•	Playful but respectful tone
	•	Strong emphasis on “KDI School, Data Unit 2” as an innovative, reliable, and fun team.
