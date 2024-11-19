import RPi.GPIO as GPIO
import random
import time

# 버튼, LED, 부저를 위한 GPIO 핀 번호 설정
BUTTONS = {"button1": 25, "button2": 5, "button3": 12, "button4": 20}
GREEN_LED = 24
RED_LED = 18
BUZZER = 14

# 그리드 및 게임 설정 변수
GRID_WIDTH = 20
GRID_HEIGHT = 10
START = (0, 0)
END = (9, 19)
BONUS_MOVE_INCREMENT = 5

# 난이도 설정에 따른 이동 횟수와 장애물 수
DIFFICULTY_SETTINGS = {
    "easy": {"move_limit": 30, "obstacle_count": 5},
    "normal": {"move_limit": 20, "obstacle_count": 10},
    "hard": {"move_limit": 15, "obstacle_count": 15},
}

current_mode = "difficulty_selection"  # 게임의 현재 모드 설정
selected_difficulty = None
game_records = []  # 게임 기록 저장 리스트

# GPIO 모드 및 경고 설정 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 버튼, LED, 부저의 GPIO 핀 설정
for pin in BUTTONS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

# 부저를 위한 PWM 설정
buzzer_pwm = GPIO.PWM(BUZZER, 100)
buzzer_pwm.start(0)

def play_success():
    """성공 시 부저로 멜로디 재생"""
    frequencies = [261, 294, 329, 349]
    buzzer_pwm.start(50)
    for freq in frequencies:
        buzzer_pwm.ChangeFrequency(freq)
        time.sleep(0.3)
    buzzer_pwm.stop()

def play_warning():
    """실패 시 부저로 경고음 재생"""
    buzzer_pwm.start(50)
    buzzer_pwm.ChangeFrequency(1000)
    time.sleep(1)
    buzzer_pwm.stop()

def generate_positions(exclude_positions, count, width, height):
    """장애물 및 보너스 위치 생성"""
    positions = set()
    while len(positions) < count:
        pos = (random.randint(0, height - 1), random.randint(0, width - 1))
        if pos not in exclude_positions:
            positions.add(pos)
    return positions

def display_grid(position, obstacles, points, end, move_count, show_player=True):
    """그리드 상태를 콘솔에 출력"""
    grid = [["*" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for x, y in obstacles:
        grid[x][y] = "X"
    for x, y in points:
        grid[x][y] = "#"
    sx, sy = START
    ex, ey = END
    grid[sx][sy] = "S"
    grid[ex][ey] = "$"
    if show_player:
        px, py = position
        grid[px][py] = "@"
    for row in grid:
        print("".join(row))
    print(f"남은 이동 횟수: {move_count}")

def select_difficulty():
    """난이도 선택 로직"""
    global current_mode, selected_difficulty
    print("난이도를 선택하려면 버튼을 누르세요: 1 (Easy), 2 (Normal), 3 (Hard), 4 (Records 보기)")
    while True:
        if GPIO.input(BUTTONS["button1"]) == GPIO.LOW:
            selected_difficulty = "easy"
            break
        elif GPIO.input(BUTTONS["button2"]) == GPIO.LOW:
            selected_difficulty = "normal"
            break
        elif GPIO.input(BUTTONS["button3"]) == GPIO.LOW:
            selected_difficulty = "hard"
            break
        elif GPIO.input(BUTTONS["button4"]) == GPIO.LOW:
            show_records_once()
            return False
        time.sleep(0.1)
    print(f"선택된 난이도: {selected_difficulty.capitalize()}")
    current_mode = "game_play"

def show_records_once():
    """게임 기록 출력"""
    print("게임 기록:")
    if not game_records:
        print("기록이 없습니다.")
    else:
        sorted_records = sorted(game_records, key=lambda x: (x["time"], -x["bonus"]))
        for i, record in enumerate(sorted_records, start=1):
            print(f"{i}. Time: {record['time']}s, Bonus: {record['bonus']} points, Difficulty: {record['difficulty'].capitalize()}")

    while GPIO.input(BUTTONS["button4"]) == GPIO.LOW:
        time.sleep(0.1)

def play_game():
    """게임 플레이 주요 로직"""
    global current_mode
    settings = DIFFICULTY_SETTINGS[selected_difficulty]
    move_limit = settings["move_limit"]
    obstacle_count = settings["obstacle_count"]

    current_position = START
    move_count = move_limit
    points_collected = 0
    start_time = time.time()

    exclude_positions = {START, END}
    obstacles = generate_positions(exclude_positions, obstacle_count, GRID_WIDTH, GRID_HEIGHT)
    points = generate_positions(exclude_positions | obstacles, 3, GRID_WIDTH, GRID_HEIGHT)

    while move_count > 0:
        elapsed_time = time.time() - start_time
        display_grid(current_position, obstacles, points, END, move_count)

        button_pressed = None
        while button_pressed is None:
            for name, pin in BUTTONS.items():
                if GPIO.input(pin) == GPIO.LOW:
                    button_pressed = name
                    break
            time.sleep(0.1)

        if button_pressed in ["button1", "button2", "button3", "button4"]:
            direction = {"button1": "up", "button2": "down", "button3": "left", "button4": "right"}[button_pressed]
            dx, dy = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[direction]
            new_position = (current_position[0] + dx, current_position[1] + dy)

            if 0 <= new_position[0] < GRID_HEIGHT and 0 <= new_position[1] < GRID_WIDTH:
                if new_position in obstacles:
                    print("장애물을 만났습니다. 이동할 수 없습니다.")
                else:
                    current_position = new_position
                    move_count -= 1

                    if current_position in points:
                        print("보너스를 획득했습니다! 추가 이동 횟수가 부여됩니다.")
                        points.remove(current_position)
                        points_collected += 1
                        move_count += BONUS_MOVE_INCREMENT

                    if current_position == END:
                        GPIO.output(GREEN_LED, GPIO.HIGH)
                        play_success()
                        GPIO.output(GREEN_LED, GPIO.LOW)
                        game_time = round(time.time() - start_time, 2)
                        game_records.append({
                            "time": game_time,
                            "bonus": points_collected,
                            "difficulty": selected_difficulty
                        })
                        print(f"게임 완료: {game_time}초, 보너스 {points_collected}점")
                        current_mode = "difficulty_selection"
                        return

    print("이동 횟수를 모두 사용했습니다. 게임 오버.")
    GPIO.output(RED_LED, GPIO.HIGH)
    play_warning()
    GPIO.output(RED_LED, GPIO.LOW)
    current_mode = "difficulty_selection"

try:
    while True:
        if current_mode == "difficulty_selection":
            if not select_difficulty():
                continue
        elif current_mode == "game_play":
            play_game()

except KeyboardInterrupt:
    print("사용자에 의해 게임이 종료되었습니다.")

finally:
    GPIO.cleanup()
