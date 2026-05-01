
import pygame
import random
import json
from pathlib import Path

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

WIDTH, HEIGHT = 400, 600
FPS = 60
LANES = [102, 167, 232, 297]
PLAYER_Y = 500
FINISH_DISTANCE = 1000

BASE = Path(__file__).parent
ASSETS = BASE / "assets"
SETTINGS_FILE = BASE / "settings.json"
LEADERBOARD_FILE = BASE / "leaderboard.json"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS3 Medium Racer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)


def load_image(name, size=None):
    image = pygame.image.load(str(ASSETS / name)).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image


def load_sound(name):
    if pygame.mixer.get_init() is None:
        return None
    try:
        return pygame.mixer.Sound(str(ASSETS / name))
    except pygame.error:
        return None


def draw_text(text, size, x, y, color=(0, 0, 0), center=True):
    f = pygame.font.SysFont("Arial", size)
    image = f.render(text, True, color)
    rect = image.get_rect(center=(x, y)) if center else image.get_rect(topleft=(x, y))
    screen.blit(image, rect)


def draw_button(rect, label):
    if rect.collidepoint(pygame.mouse.get_pos()):
        color = (230, 230, 230)
    else:
        color = (255, 255, 255)

    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=8)
    draw_text(label, 21, rect.centerx, rect.centery)


def clicked(event, rect):
    return event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos)


def load_json(path, default):
    if not path.exists():
        save_json(path, default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_settings():
    default = {
        "sound_enabled": True,
        "car_color": "blue",
        "difficulty": "normal"
    }

    settings = load_json(SETTINGS_FILE, default.copy())

    for key in default:
        if key not in settings:
            settings[key] = default[key]

    return settings


def save_score(username, score, distance, coins):
    leaderboard = load_json(LEADERBOARD_FILE, [])

    leaderboard.append({
        "name": username,
        "score": score,
        "distance": distance,
        "coins": coins
    })

    leaderboard.sort(key=lambda row: row["score"], reverse=True)
    save_json(LEADERBOARD_FILE, leaderboard[:10])


class Sounds:
    def __init__(self, enabled):
        self.enabled = enabled
        self.coin = load_sound("coin.wav")
        self.power = load_sound("powerup.wav")
        self.crash = load_sound("crash.wav")

    def start_music(self):
        if not self.enabled or pygame.mixer.get_init() is None:
            return

        try:
            pygame.mixer.music.load(str(ASSETS / "background.wav"))
            pygame.mixer.music.set_volume(0.35)
            pygame.mixer.music.play(-1)
        except pygame.error:
            pass

    def stop_music(self):
        if pygame.mixer.get_init() is not None:
            pygame.mixer.music.stop()

    def play(self, sound):
        if self.enabled and sound is not None:
            sound.play()


def username_screen():
    username = ""

    while True:
        screen.fill((235, 235, 235))
        draw_text("Enter username", 34, WIDTH // 2, 180)
        draw_text("Press ENTER to start", 20, WIDTH // 2, 230, (70, 70, 70))

        box = pygame.Rect(70, 285, 260, 50)
        pygame.draw.rect(screen, (255, 255, 255), box)
        pygame.draw.rect(screen, (0, 0, 0), box, 2)
        screen.blit(font.render(username + "|", True, (0, 0, 0)), (box.x + 12, box.y + 14))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return username.strip() or "Player"

                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]

                elif len(username) < 12:
                    if event.unicode.isalnum() or event.unicode in "_-":
                        username += event.unicode

        pygame.display.flip()
        clock.tick(FPS)


def menu_screen(username):
    buttons = [
        ("Play", "play"),
        ("Leaderboard", "leaderboard"),
        ("Settings", "settings"),
        ("Quit", "quit")
    ]

    while True:
        screen.fill((75, 150, 235))
        draw_text("RACER", 52, WIDTH // 2, 90, (255, 255, 255))
        draw_text("Player: " + username, 21, WIDTH // 2, 140, (255, 255, 255))

        rects = []

        for i, item in enumerate(buttons):
            label, action = item
            rect = pygame.Rect(110, 195 + i * 65, 180, 45)
            rects.append((rect, action))
            draw_button(rect, label)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            for rect, action in rects:
                if clicked(event, rect):
                    return action

        pygame.display.flip()
        clock.tick(FPS)


def settings_screen(settings):
    colors = ["blue", "red", "green", "yellow", "purple"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        screen.fill((240, 240, 240))
        draw_text("Settings", 38, WIDTH // 2, 80)

        sound_button = pygame.Rect(85, 160, 230, 45)
        color_button = pygame.Rect(85, 230, 230, 45)
        difficulty_button = pygame.Rect(85, 300, 230, 45)
        back_button = pygame.Rect(115, 470, 170, 45)

        draw_button(sound_button, "Sound: " + ("On" if settings["sound_enabled"] else "Off"))
        draw_button(color_button, "Car: " + settings["car_color"])
        draw_button(difficulty_button, "Difficulty: " + settings["difficulty"])
        draw_button(back_button, "Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings

            if clicked(event, sound_button):
                settings["sound_enabled"] = not settings["sound_enabled"]

            if clicked(event, color_button):
                index = colors.index(settings["car_color"])
                settings["car_color"] = colors[(index + 1) % len(colors)]

            if clicked(event, difficulty_button):
                index = difficulties.index(settings["difficulty"])
                settings["difficulty"] = difficulties[(index + 1) % len(difficulties)]

            if clicked(event, back_button):
                save_json(SETTINGS_FILE, settings)
                return settings

        pygame.display.flip()
        clock.tick(FPS)


def leaderboard_screen():
    leaderboard = load_json(LEADERBOARD_FILE, [])
    back_button = pygame.Rect(115, 525, 170, 45)

    while True:
        screen.fill((245, 245, 245))
        draw_text("Top 10", 38, WIDTH // 2, 50)

        draw_text("Rank", 17, 20, 100, center=False)
        draw_text("Name", 17, 80, 100, center=False)
        draw_text("Score", 17, 205, 100, center=False)
        draw_text("Dist", 17, 300, 100, center=False)

        if not leaderboard:
            draw_text("No scores yet", 24, WIDTH // 2, 280)

        y = 135

        for i, row in enumerate(leaderboard):
            draw_text(str(i + 1), 17, 30, y, center=False)
            draw_text(row["name"], 17, 80, y, center=False)
            draw_text(str(row["score"]), 17, 210, y, center=False)
            draw_text(str(row["distance"]), 17, 310, y, center=False)
            y += 35

        draw_button(back_button, "Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if clicked(event, back_button):
                return

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(result):
    retry_button = pygame.Rect(55, 430, 125, 45)
    menu_button = pygame.Rect(220, 430, 125, 45)

    while True:
        screen.fill((35, 35, 35))

        if result["finished"]:
            title = "FINISHED!"
            color = (50, 220, 80)
        else:
            title = "GAME OVER"
            color = (230, 60, 60)

        draw_text(title, 42, WIDTH // 2, 100, color)
        draw_text("Score: " + str(result["score"]), 24, WIDTH // 2, 190, (255, 255, 255))
        draw_text("Distance: " + str(result["distance"]), 24, WIDTH // 2, 235, (255, 255, 255))
        draw_text("Coins: " + str(result["coins"]), 24, WIDTH // 2, 280, (255, 255, 255))

        draw_button(retry_button, "Retry")
        draw_button(menu_button, "Menu")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"

            if clicked(event, retry_button):
                return "retry"

            if clicked(event, menu_button):
                return "menu"

        pygame.display.flip()
        clock.tick(FPS)


def start_speed(difficulty):
    if difficulty == "easy":
        return 4

    if difficulty == "hard":
        return 7

    return 5


def play_game(username, settings):
    background = load_image("road_background.png", (WIDTH, HEIGHT))

    player_image = load_image("player_" + settings["car_color"] + ".png", (50, 85))
    enemy_image = load_image("enemy.png", (50, 85))
    coin_image = load_image("coin.png", (32, 32))

    obstacle_images = {
        "barrier": load_image("barrier.png", (44, 44)),
        "oil": load_image("oil.png", (44, 44)),
        "pothole": load_image("pothole.png", (44, 44)),
        "speed_bump": load_image("speed_bump.png", (44, 44)),
        "boost_strip": load_image("boost_strip.png", (58, 32)),
        "slow_zone": load_image("slow_zone.png", (58, 32))
    }

    power_images = {
        "Nitro": load_image("nitro.png", (38, 38)),
        "Shield": load_image("shield.png", (38, 38)),
        "Repair": load_image("repair.png", (38, 38))
    }

    sounds = Sounds(settings["sound_enabled"])
    sounds.start_music()

    lane = 1
    player = player_image.get_rect(center=(LANES[lane], PLAYER_Y))

    speed = start_speed(settings["difficulty"])
    distance = 0
    coins = 0
    bonus = 0
    bg_y = 0

    enemies = []
    obstacles = []
    coin_list = []
    powers = []

    timers = {
        "enemy": 0,
        "obstacle": 0,
        "coin": 0,
        "power": 0
    }

    active_power = None
    power_time = 0
    shield = False
    repair_ready = False

    running = True
    finished = False

    def make_rect(lane_number, y, width, height):
        rect = pygame.Rect(0, y, width, height)
        rect.centerx = LANES[lane_number]
        return rect

    def safe_lane():
        choices = [0, 1, 2, 3]

        if lane in choices and random.random() < 0.70:
            choices.remove(lane)

        return random.choice(choices)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_a] and lane > 0:
                    lane -= 1

                if event.key in [pygame.K_RIGHT, pygame.K_d] and lane < 3:
                    lane += 1

                if event.key == pygame.K_ESCAPE:
                    running = False

        player.centerx = LANES[lane]

        if active_power == "Nitro":
            power_time -= 1

            if power_time <= 0:
                active_power = None

        game_speed = speed + int(distance // 250)

        if active_power == "Nitro":
            game_speed += 4

        distance += game_speed * 0.08

        if distance >= FINISH_DISTANCE:
            finished = True
            running = False

        bg_y = (bg_y + game_speed) % HEIGHT

        for key in timers:
            timers[key] += 1

        progress = int(distance // 200)
        enemy_delay = max(35, 100 - progress * 8)
        obstacle_delay = max(45, 125 - progress * 8)

        if timers["enemy"] >= enemy_delay:
            new_lane = safe_lane()
            enemies.append({
                "rect": make_rect(new_lane, -90, 50, 85),
                "speed": game_speed + random.randint(1, 3)
            })
            timers["enemy"] = 0

        if timers["obstacle"] >= obstacle_delay:
            new_lane = safe_lane()
            obstacle_type = random.choice([
                "barrier",
                "oil",
                "pothole",
                "speed_bump",
                "boost_strip",
                "slow_zone"
            ])

            obstacles.append({
                "rect": make_rect(new_lane, -50, 55, 38),
                "type": obstacle_type,
                "direction": random.choice([-1, 1])
            })

            timers["obstacle"] = 0

        if timers["coin"] >= 45:
            new_lane = random.randint(0, 3)
            value = random.choices([1, 2, 5], weights=[70, 25, 5])[0]

            coin_list.append({
                "rect": make_rect(new_lane, -30, 32, 32),
                "value": value
            })

            timers["coin"] = 0

        if timers["power"] >= 330:
            new_lane = safe_lane()
            power_type = random.choice(["Nitro", "Shield", "Repair"])

            powers.append({
                "rect": make_rect(new_lane, -40, 38, 38),
                "type": power_type,
                "life": FPS * 5
            })

            timers["power"] = 0

        for enemy in enemies[:]:
            enemy["rect"].y += enemy["speed"]

            if enemy["rect"].top > HEIGHT:
                enemies.remove(enemy)

            elif player.colliderect(enemy["rect"]):
                if shield:
                    shield = False
                    active_power = None
                    enemies.remove(enemy)

                elif repair_ready:
                    repair_ready = False
                    enemies.remove(enemy)

                else:
                    sounds.play(sounds.crash)
                    pygame.time.wait(250)
                    running = False

        for obstacle in obstacles[:]:
            obstacle["rect"].y += game_speed

            if obstacle["type"] == "barrier":
                obstacle["rect"].x += obstacle["direction"] * 2

                if obstacle["rect"].left < 70 or obstacle["rect"].right > 330:
                    obstacle["direction"] *= -1

            if obstacle["rect"].top > HEIGHT:
                obstacles.remove(obstacle)
                continue

            if player.colliderect(obstacle["rect"]):
                kind = obstacle["type"]

                if kind == "oil":
                    distance = max(0, distance - 15)
                    obstacles.remove(obstacle)

                elif kind in ["speed_bump", "slow_zone"]:
                    distance = max(0, distance - 25)
                    obstacles.remove(obstacle)

                elif kind == "boost_strip":
                    active_power = "Nitro"
                    power_time = FPS * 3
                    bonus += 20
                    obstacles.remove(obstacle)

                elif shield:
                    shield = False
                    active_power = None
                    obstacles.remove(obstacle)

                elif repair_ready:
                    repair_ready = False
                    obstacles.remove(obstacle)

                else:
                    sounds.play(sounds.crash)
                    pygame.time.wait(250)
                    running = False

        for coin in coin_list[:]:
            coin["rect"].y += game_speed

            if coin["rect"].top > HEIGHT:
                coin_list.remove(coin)

            elif player.colliderect(coin["rect"]):
                coins += 1
                bonus += coin["value"] * 10
                sounds.play(sounds.coin)
                coin_list.remove(coin)

        for power in powers[:]:
            power["rect"].y += game_speed
            power["life"] -= 1

            if power["rect"].top > HEIGHT or power["life"] <= 0:
                powers.remove(power)
                continue

            if player.colliderect(power["rect"]):
                if power["type"] == "Nitro" and active_power is None:
                    active_power = "Nitro"
                    power_time = FPS * 4
                    bonus += 30
                    sounds.play(sounds.power)

                elif power["type"] == "Shield" and active_power is None:
                    active_power = "Shield"
                    shield = True
                    bonus += 20
                    sounds.play(sounds.power)

                elif power["type"] == "Repair":
                    repair_ready = True
                    bonus += 15
                    sounds.play(sounds.power)

                powers.remove(power)

        score = int(distance) + bonus

        screen.blit(background, (0, bg_y))
        screen.blit(background, (0, bg_y - HEIGHT))

        for coin in coin_list:
            screen.blit(coin_image, coin["rect"])

        for obstacle in obstacles:
            screen.blit(obstacle_images[obstacle["type"]], obstacle["rect"])

        for power in powers:
            screen.blit(power_images[power["type"]], power["rect"])

        for enemy in enemies:
            screen.blit(enemy_image, enemy["rect"])

        screen.blit(player_image, player)

        if shield:
            pygame.draw.circle(screen, (40, 230, 100), player.center, 50, 3)

        hud_lines = [
            "Name: " + username,
            "Score: " + str(score),
            "Coins: " + str(coins),
            "Distance: " + str(int(distance)),
            "Remaining: " + str(max(0, FINISH_DISTANCE - int(distance)))
        ]

        y = 5

        for line in hud_lines:
            screen.blit(font.render(line, True, (0, 0, 0)), (5, y))
            y += 22

        if active_power == "Nitro":
            power_text = "Power: Nitro " + str(power_time // FPS) + "s"
        elif active_power == "Shield":
            power_text = "Power: Shield"
        elif repair_ready:
            power_text = "Power: Repair ready"
        else:
            power_text = "Power: None"

        screen.blit(font.render(power_text, True, (0, 0, 0)), (5, y + 3))
        screen.blit(font.render("A/D or arrows", True, (0, 0, 0)), (245, 575))

        pygame.display.flip()

    sounds.stop_music()

    return {
        "score": int(distance) + bonus,
        "distance": int(distance),
        "coins": coins,
        "finished": finished
    }


def main():
    settings = load_settings()
    username = username_screen()

    if username == "":
        pygame.quit()
        return

    while True:
        action = menu_screen(username)

        if action == "play":
            result = play_game(username, settings)
            save_score(username, result["score"], result["distance"], result["coins"])

            while game_over_screen(result) == "retry":
                result = play_game(username, settings)
                save_score(username, result["score"], result["distance"], result["coins"])

        elif action == "leaderboard":
            leaderboard_screen()

        elif action == "settings":
            settings = settings_screen(settings)

        elif action == "quit":
            break

    pygame.quit()


main()
