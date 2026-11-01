import math
import random

from pygame import Rect


WIDTH = 960
HEIGHT = 540
TITLE = "Guerreiro Vs O Guardião"

GRAVITY = 1450
MOVE_SPEED = 245
JUMP_SPEED = -540
DASH_SPEED = 590
MAX_LIVES = 5

START_BUTTON = Rect(250, 180, 460, 58)
SOUND_BUTTON = Rect(250, 253, 460, 58)
EXIT_BUTTON = Rect(250, 326, 460, 58)


def animation(prefix, frame_count):
    return {
        direction: [
            f"{prefix}_{direction}_{frame}" for frame in range(frame_count)
        ]
        for direction in ("l", "r")
    }


HERO_ANIMATIONS = {
    "idle": animation("hero_idle", 11),
    "run": animation("hero_run", 8),
    "jump": animation("hero_jump", 3),
    "fall": animation("hero_fall", 3),
    "attack": animation("hero_attack", 7),
    "hit": animation("hero_hit", 4),
    "death": animation("hero_death", 11),
}

ENEMY_ANIMATIONS = {
    "spider": {
        "idle": animation("spider_idle", 3),
        "walk": animation("spider_walk", 5),
    },
    "bat": {
        "idle": {
            "l": ["bat_walk_l_0"],
            "r": ["bat_walk_r_0"],
        },
        "walk": {
            "l": ["bat_walk_l_0"],
            "r": ["bat_walk_r_0"],
        },
    },
    "mummy": {
        "idle": animation("mummy_idle", 4),
        "walk": animation("mummy_walk", 4),
        "attack": animation("mummy_attack", 5),
    },
    "guardian": {
        "idle": animation("guardian_idle", 4),
        "walk": animation("guardian_walk", 4),
        "attack": animation("guardian_attack", 5),
    },
}


LEVELS = [
    {
        "name": "O VILAREJO DE ARVEN",
        "sky": (48, 72, 104),
        "horizon": (34, 47, 70),
        "stone": (99, 84, 70),
        "spawn": (54, 500),
        "exit": Rect(888, 430, 46, 70),
        "platforms": [
            (0, 500, 960, 40),
            (145, 420, 190, 22),
            (400, 348, 190, 22),
            (670, 414, 160, 22),
        ],
        "coins": [
            (205, 380), (280, 380), (455, 308), (535, 308),
            (730, 374), (805, 374), (855, 462),
        ],
        "potions": [(350, 465)],
        "enemies": [
            ("spider", 370, 500, 330, 500),
            ("spider", 700, 414, 680, 805),
            ("mummy", 610, 500, 570, 750),
            ("spider", 835, 500, 780, 885),
        ],
    },
    {
        "name": "AS MURALHAS DE ELDORIA",
        "sky": (48, 72, 104),
        "horizon": (34, 47, 70),
        "stone": (78, 81, 91),
        "spawn": (50, 500),
        "exit": Rect(862, 260, 46, 70),
        "platforms": [
            (0, 500, 960, 40),
            (105, 424, 180, 22),
            (350, 350, 170, 22),
            (585, 405, 160, 22),
            (760, 330, 165, 22),
        ],
        "coins": [
            (160, 384), (250, 384), (400, 310), (485, 310),
            (625, 365), (700, 365), (805, 290), (885, 290),
        ],
        "potions": [(555, 465)],
        "enemies": [
            ("spider", 160, 424, 125, 260),
            ("bat", 410, 350, 340, 525),
            ("mummy", 650, 405, 595, 735),
            ("bat", 800, 330, 755, 915),
        ],
    },
    {
        "name": "A CRIPTA DO SELO",
        "sky": (48, 72, 104),
        "horizon": (34, 47, 70),
        "stone": (58, 58, 69),
        "spawn": (50, 500),
        "exit": Rect(888, 430, 46, 70),
        "platforms": [
            (0, 500, 960, 40),
            (130, 410, 155, 22),
            (345, 330, 170, 22),
            (585, 410, 160, 22),
            (760, 330, 145, 22),
        ],
        "coins": [
            (175, 370), (245, 370), (390, 290), (470, 290),
            (625, 370), (700, 370), (800, 290), (870, 290),
            (825, 462),
        ],
        "potions": [(545, 465)],
        "enemies": [
            ("mummy", 300, 500, 260, 440),
            ("spider", 600, 410, 590, 730),
            ("bat", 410, 330, 345, 515),
            ("guardian", 760, 500, 680, 870),
            ("bat", 800, 330, 755, 910),
        ],
    },
]


random.seed(17)
game_state = "menu"
sound_enabled = True
music_started = False
level_index = 0
level = None
platforms = []
coins = []
potions = []
enemies = []
hero = None
score = 0
world_time = 0
banner_timer = 0
message = ""
message_timer = 0
mouse_position = (-1, -1)


def play_sound(name):
    if not sound_enabled:
        return
    try:
        getattr(sounds, name).play()
    except Exception:
        pass


def start_music():
    global music_started
    if sound_enabled and not music_started:
        try:
            music.play("old_tower_inn")
            music.set_volume(0.28)
            music_started = True
        except Exception:
            pass


class AnimatedCharacter:
    def __init__(self, animations, first_image):
        self.animations = animations
        self.actor = Actor(first_image, anchor=("center", "bottom"))
        self.direction = "r"
        self.animation_state = "idle"
        self.frame_index = 0
        self.frame_clock = 0

    def animate(self, state, dt, frames_per_second=10):
        if state != self.animation_state:
            self.animation_state = state
            self.frame_index = 0
            self.frame_clock = 0
        frames = self.animations[state][self.direction]
        frame_duration = 1 / frames_per_second
        self.frame_clock += dt
        while self.frame_clock >= frame_duration:
            self.frame_clock -= frame_duration
            self.frame_index = (self.frame_index + 1) % len(frames)
        self.actor.image = frames[self.frame_index]


class Hero(AnimatedCharacter):
    def __init__(self, spawn):
        super().__init__(HERO_ANIMATIONS, "hero_idle_r_0")
        self.rect = Rect(0, 0, 34, 58)
        self.spawn = spawn
        self.position_x = 0.0
        self.position_y = 0.0
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.attack_timer = 0
        self.attack_number = 0
        self.hit_timer = 0
        self.invulnerable = 0
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.lives = MAX_LIVES
        self.respawn()

    def sync_position(self):
        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)

    def respawn(self):
        self.rect.midbottom = self.spawn
        self.sync_position()
        self.velocity_x = 0
        self.velocity_y = 0
        self.actor.midbottom = self.rect.midbottom

    def jump(self):
        if self.on_ground and self.dash_timer <= 0:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False
            play_sound("jump")

    def attack(self):
        if self.attack_timer <= 0 and self.dash_timer <= 0:
            self.attack_timer = 0.5
            self.attack_number += 1
            play_sound("sword")

    def dash(self):
        if self.dash_cooldown <= 0 and self.attack_timer <= 0:
            self.dash_timer = 0.18
            self.dash_cooldown = 1.15
            self.velocity_y = 0
            play_sound("dash")

    def attack_box(self):
        if self.direction == "r":
            return Rect(self.rect.right - 3, self.rect.y + 7, 61, 44)
        return Rect(self.rect.left - 58, self.rect.y + 7, 61, 44)

    def take_damage(self):
        global game_state
        if self.invulnerable > 0 or self.dash_timer > 0:
            return
        self.lives -= 1
        self.hit_timer = 0.3
        self.invulnerable = 1.35
        play_sound("hit")
        if self.lives <= 0:
            game_state = "game_over"
        else:
            self.respawn()

    def heal(self):
        self.lives = min(MAX_LIVES, self.lives + 1)

    def move_horizontal(self, dt):
        if self.dash_timer > 0:
            direction_value = 1 if self.direction == "r" else -1
            self.velocity_x = DASH_SPEED * direction_value
        else:
            moving_left = keyboard.left or keyboard.a
            moving_right = keyboard.right or keyboard.d
            self.velocity_x = MOVE_SPEED * (moving_right - moving_left)
            if self.velocity_x:
                self.direction = "r" if self.velocity_x > 0 else "l"

        self.position_x += self.velocity_x * dt
        self.rect.x = round(self.position_x)
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        self.position_x = float(self.rect.x)

    def move_vertical(self, dt):
        previous_bottom = self.rect.bottom
        if self.dash_timer <= 0:
            self.velocity_y += GRAVITY * dt
        self.position_y += self.velocity_y * dt
        self.rect.y = round(self.position_y)
        self.on_ground = False

        for platform in platforms:
            landing = (
                self.velocity_y >= 0
                and previous_bottom <= platform.top + 4
                and self.rect.bottom >= platform.top
                and self.rect.right > platform.left + 5
                and self.rect.left < platform.right - 5
            )
            if landing:
                self.rect.bottom = platform.top
                self.position_y = float(self.rect.y)
                self.velocity_y = 0
                self.on_ground = True
                break

    def update(self, dt):
        self.move_horizontal(dt)
        self.move_vertical(dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.hit_timer = max(0, self.hit_timer - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        self.dash_timer = max(0, self.dash_timer - dt)
        self.dash_cooldown = max(0, self.dash_cooldown - dt)

        if self.rect.top > HEIGHT:
            self.take_damage()

        if self.hit_timer > 0:
            state = "hit"
        elif self.attack_timer > 0:
            state = "attack"
        elif not self.on_ground:
            state = "jump" if self.velocity_y < 0 else "fall"
        elif self.velocity_x:
            state = "run"
        else:
            state = "idle"

        animation_speed = 16 if self.dash_timer > 0 else 11
        if state == "attack":
            animation_speed = 14
        self.animate(state, dt, animation_speed)
        self.actor.midbottom = self.rect.midbottom

    def draw(self):
        if self.dash_timer > 0:
            offset = 35 if self.direction == "r" else -35
            trail_x = self.rect.centerx - offset
            screen.draw.line(
                (trail_x, self.rect.centery),
                (trail_x - offset, self.rect.centery),
                (164, 205, 224),
            )
        if self.invulnerable <= 0 or int(self.invulnerable * 12) % 2:
            self.actor.draw()


class Enemy(AnimatedCharacter):
    def __init__(self, kind, x, floor_y, patrol_left, patrol_right):
        animations = ENEMY_ANIMATIONS[kind]
        super().__init__(animations, f"{kind}_idle_r_0")
        self.kind = kind
        sizes = {
            "spider": (42, 30),
            "bat": (48, 32),
            "mummy": (38, 62),
            "guardian": (54, 88),
        }
        self.rect = Rect(0, 0, *sizes[kind])
        self.rect.midbottom = (x, floor_y)
        if kind == "bat":
            self.rect.y -= 38
        self.position_x = float(self.rect.x)
        self.base_y = float(self.rect.y)
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.speed = {
            "spider": 72,
            "bat": 62,
            "mummy": 58,
            "guardian": 48,
        }[kind]
        self.direction_value = 1
        self.pause_timer = random.uniform(0.15, 0.55)
        self.phase = random.random() * math.tau
        self.max_health = {
            "spider": 1,
            "bat": 1,
            "mummy": 2,
            "guardian": 7,
        }[kind]
        self.health = self.max_health
        self.points = {
            "spider": 40,
            "bat": 50,
            "mummy": 80,
            "guardian": 350,
        }[kind]
        self.last_attack = -1
        self.alive = True
        self.place_actor()

    def place_actor(self):
        if self.kind == "bat":
            self.actor.center = self.rect.center
        else:
            self.actor.midbottom = self.rect.midbottom

    def take_hit(self, attack_number):
        if attack_number == self.last_attack:
            return 0
        self.last_attack = attack_number
        self.health -= 1
        self.pause_timer = 0.18
        play_sound("hit")
        if self.health <= 0:
            self.alive = False
            return self.points
        return 0

    def patrol(self, dt):
        self.position_x += self.speed * self.direction_value * dt
        self.rect.x = round(self.position_x)

        if self.rect.left <= self.patrol_left:
            self.rect.left = self.patrol_left
            self.position_x = float(self.rect.x)
            self.direction_value = 1
            self.pause_timer = 0.45
        elif self.rect.right >= self.patrol_right:
            self.rect.right = self.patrol_right
            self.position_x = float(self.rect.x)
            self.direction_value = -1
            self.pause_timer = 0.45

    def update(self, dt):
        close_to_hero = abs(self.rect.centerx - hero.rect.centerx) < 65
        can_attack = self.kind in ("mummy", "guardian")
        if self.pause_timer > 0:
            self.pause_timer -= dt
            state = "idle"
        elif can_attack and close_to_hero:
            state = "attack"
        else:
            state = "walk"
            self.patrol(dt)

        self.direction = "r" if self.direction_value > 0 else "l"
        if self.kind == "bat":
            self.rect.y = round(
                self.base_y + math.sin(world_time * 4 + self.phase) * 9
            )
        self.animate(state, dt, 9)
        self.place_actor()

    def draw(self):
        self.actor.draw()
        if self.max_health > 2 or self.health < self.max_health:
            bar_width = 58 if self.kind == "guardian" else 42
            x = self.rect.centerx - bar_width // 2
            y = self.rect.top - 10
            screen.draw.filled_rect(Rect(x, y, bar_width, 5), (45, 28, 38))
            health_width = round(bar_width * self.health / self.max_health)
            screen.draw.filled_rect(
                Rect(x, y, health_width, 5), (180, 61, 78)
            )


def load_level(index):
    global level, platforms, coins, potions, enemies, hero, banner_timer
    level = LEVELS[index]
    platforms = [Rect(*values) for values in level["platforms"]]
    coins = [
        {"position": position, "taken": False} for position in level["coins"]
    ]
    potions = [
        {"position": position, "taken": False}
        for position in level["potions"]
    ]
    enemies = [Enemy(*values) for values in level["enemies"]]
    lives = hero.lives if hero else MAX_LIVES
    hero = Hero(level["spawn"])
    hero.lives = lives
    banner_timer = 1.8


def start_game():
    global game_state, level_index, score, hero
    level_index = 0
    score = 0
    hero = None
    game_state = "playing"
    load_level(level_index)
    play_sound("select")
    start_music()


def next_level():
    global level_index, game_state, score
    play_sound("level_up")
    score += 100
    level_index += 1
    if level_index >= len(LEVELS):
        game_state = "victory"
    else:
        load_level(level_index)


def remaining_coins():
    return sum(not coin["taken"] for coin in coins)


def remaining_enemies():
    return sum(enemy.alive for enemy in enemies)


def exit_is_open():
    return remaining_coins() == 0 and remaining_enemies() == 0


def objective_message():
    missing_coins = remaining_coins()
    missing_enemies = remaining_enemies()
    parts = []
    if missing_coins:
        parts.append(f"{missing_coins} MOEDA(S)")
    if missing_enemies:
        parts.append(f"{missing_enemies} INIMIGO(S)")
    return "FALTA: " + " E ".join(parts)


def update_collectibles():
    global score
    for coin in coins:
        x, y = coin["position"]
        if not coin["taken"] and hero.rect.collidepoint(x, y):
            coin["taken"] = True
            score += 10
            play_sound("coin")

    for potion in potions:
        x, y = potion["position"]
        if not potion["taken"] and hero.rect.collidepoint(x, y):
            potion["taken"] = True
            hero.heal()
            score += 25
            play_sound("level_up")


def update(dt):
    global world_time, banner_timer, message_timer, message, score
    world_time += dt
    start_music()
    banner_timer = max(0, banner_timer - dt)
    message_timer = max(0, message_timer - dt)

    if game_state != "playing":
        return

    hero.update(dt)
    for enemy in enemies:
        if not enemy.alive:
            continue
        enemy.update(dt)
        if (
            hero.attack_timer > 0
            and hero.attack_box().colliderect(enemy.rect)
        ):
            score += enemy.take_hit(hero.attack_number)
        if enemy.alive and enemy.rect.colliderect(hero.rect):
            hero.take_damage()

    update_collectibles()
    if hero.rect.colliderect(level["exit"]):
        if exit_is_open():
            next_level()
        else:
            message = objective_message()
            message_timer = 1.0


def draw_background():
    data = level if level else LEVELS[0]
    screen.fill(data["sky"])
    screen.draw.filled_circle((790, 105), 38, (242, 218, 145))

    horizon = data["horizon"]
    for index, height in enumerate((150, 205, 175, 240, 190, 225)):
        x = index * 180 - 35
        screen.draw.filled_rect(Rect(x, 500 - height, 150, height), horizon)
        screen.draw.filled_rect(
            Rect(x + 38, 500 - height - 34, 74, 34), horizon
        )
    for x in (90, 815):
        screen.draw.filled_rect(Rect(x, 265, 60, 235), horizon)
        screen.draw.filled_rect(Rect(x - 12, 245, 84, 25), horizon)


def draw_platforms():
    for platform in platforms:
        screen.draw.filled_rect(platform, level["stone"])
        screen.draw.filled_rect(
            Rect(platform.x, platform.y, platform.width, 5),
            (167, 145, 99),
        )
        for x in range(platform.left + 12, platform.right, 34):
            screen.draw.line(
                (x, platform.top + 7),
                (x, min(platform.bottom - 2, platform.top + 18)),
                (55, 49, 49),
            )


def draw_exit():
    door = level["exit"]
    color = (146, 101, 43) if exit_is_open() else (73, 48, 43)
    screen.draw.filled_rect(door, color)
    screen.draw.rect(door, (220, 180, 100))
    screen.draw.filled_circle(
        (door.right - 10, door.centery), 3, (236, 206, 105)
    )
    if not exit_is_open():
        screen.draw.line(
            (door.left + 8, door.centery - 8),
            (door.right - 8, door.centery + 8),
            (44, 32, 32),
        )


def draw_coins_and_potions():
    for coin in coins:
        if coin["taken"]:
            continue
        x, y = coin["position"]
        radius = 9 + round(math.sin(world_time * 6 + x) * 2)
        screen.draw.filled_circle((x, y), radius, (246, 188, 45))
        screen.draw.circle((x, y), radius, (255, 230, 122))
        screen.draw.line((x, y - 5), (x, y + 5), (184, 118, 28))

    for potion in potions:
        if potion["taken"]:
            continue
        x, y = potion["position"]
        screen.draw.filled_rect(Rect(x - 7, y - 9, 14, 18), (176, 45, 76))
        screen.draw.rect(Rect(x - 7, y - 9, 14, 18), (245, 190, 190))
        screen.draw.filled_rect(Rect(x - 4, y - 14, 8, 5), (213, 191, 139))
        screen.draw.line((x - 3, y), (x + 3, y), (255, 225, 225))


def draw_interface():
    collected = len(coins) - remaining_coins()
    screen.draw.filled_rect(Rect(14, 14, 475, 58), (20, 23, 34))
    screen.draw.text(
        f"FASE {level_index + 1}/3   VIDAS: {hero.lives}/{MAX_LIVES}   "
        f"MOEDAS: {collected}/{len(coins)}   PONTOS: {score}",
        (26, 31),
        fontsize=21,
        color=(245, 232, 190),
    )

    cooldown_width = 92
    dash_ready = 1 - min(1, hero.dash_cooldown / 1.15)
    screen.draw.text("DASH", (505, 24), fontsize=18, color=(199, 214, 224))
    screen.draw.filled_rect(Rect(505, 48, cooldown_width, 8), (38, 45, 56))
    screen.draw.filled_rect(
        Rect(505, 48, round(cooldown_width * dash_ready), 8),
        (100, 185, 215),
    )

    guardian = next(
        (enemy for enemy in enemies if enemy.kind == "guardian" and enemy.alive),
        None,
    )
    if guardian:
        screen.draw.text(
            "O GUARDIÃO",
            center=(760, 27),
            fontsize=18,
            color=(231, 190, 241),
        )
        screen.draw.filled_rect(Rect(655, 45, 210, 10), (44, 25, 48))
        boss_width = round(210 * guardian.health / guardian.max_health)
        screen.draw.filled_rect(Rect(655, 45, boss_width, 10), (153, 67, 177))

    if banner_timer > 0:
        screen.draw.filled_rect(Rect(220, 90, 520, 58), (20, 23, 34))
        screen.draw.text(
            level["name"],
            center=(480, 119),
            fontsize=32,
            color=(246, 208, 103),
        )
    if message_timer > 0:
        screen.draw.text(
            message,
            center=(480, 185),
            fontsize=26,
            color=(255, 220, 105),
            owidth=1,
            ocolor=(30, 25, 25),
        )


def draw_menu_button(rect, text, style):
    hovered = rect.collidepoint(mouse_position)
    colors = {
        "start": ((151, 96, 37), (187, 127, 48)),
        "sound": ((51, 61, 76), (67, 80, 99)),
        "exit": ((77, 48, 48), (104, 57, 57)),
    }
    color = colors[style][hovered]
    border = (255, 219, 132) if hovered else (199, 160, 88)
    shadow = Rect(rect.x + 5, rect.y + 6, rect.width, rect.height)
    screen.draw.filled_rect(shadow, (12, 14, 21))
    screen.draw.filled_rect(rect, color)
    screen.draw.filled_rect(Rect(rect.x, rect.y, 7, rect.height), border)
    screen.draw.rect(rect, border)

    if style == "sound":
        status_color = (100, 205, 139) if sound_enabled else (207, 91, 91)
        screen.draw.filled_circle(
            (rect.left + 31, rect.centery), 7, status_color
        )
    else:
        marker = ">" if style == "start" else "X"
        screen.draw.text(
            marker,
            center=(rect.left + 31, rect.centery),
            fontsize=24,
            color=border,
        )

    screen.draw.text(
        text,
        center=(rect.centerx + 12, rect.centery),
        fontsize=25,
        color=(255, 242, 207),
    )


def draw_keycap(x, y, width, text):
    key = Rect(x, y, width, 27)
    screen.draw.filled_rect(
        Rect(key.x + 2, key.y + 3, key.width, key.height),
        (13, 15, 23),
    )
    screen.draw.filled_rect(key, (52, 59, 72))
    screen.draw.rect(key, (150, 158, 169))
    screen.draw.text(
        text,
        center=key.center,
        fontsize=16,
        color=(244, 235, 211),
    )


def draw_control_hint(x, y, key_text, key_width, description):
    draw_keycap(x, y, key_width, key_text)
    screen.draw.text(
        description,
        midleft=(x + key_width + 8, y + 13),
        fontsize=16,
        color=(222, 225, 223),
    )


def draw_menu():
    draw_background()
    screen.draw.filled_rect(Rect(180, 28, 600, 484), (21, 24, 34))
    screen.draw.rect(Rect(180, 28, 600, 484), (198, 158, 85))
    screen.draw.filled_rect(Rect(181, 29, 598, 5), (224, 180, 91))
    screen.draw.text(
        "GUERREIRO",
        center=(480, 70),
        fontsize=52,
        color=(246, 208, 103),
    )
    screen.draw.text(
        "VS O GUARDIÃO",
        center=(480, 111),
        fontsize=30,
        color=(232, 232, 222),
    )
    screen.draw.text(
        "Colete as moedas, derrote os inimigos e abra a porta.",
        center=(480, 148),
        fontsize=18,
        color=(169, 181, 190),
    )
    draw_menu_button(START_BUTTON, "INICIAR AVENTURA", "start")
    sound_text = (
        "AUDIO: LIGADO"
        if sound_enabled
        else "AUDIO: DESLIGADO"
    )
    draw_menu_button(SOUND_BUTTON, sound_text, "sound")
    draw_menu_button(EXIT_BUTTON, "SAIR DO JOGO", "exit")

    screen.draw.line((216, 408), (744, 408), (76, 82, 96))
    screen.draw.text(
        "CONTROLES",
        center=(480, 424),
        fontsize=16,
        color=(219, 181, 100),
    )
    draw_control_hint(218, 438, "A/D", 48, "MOVER")
    draw_control_hint(365, 438, "ESPACO", 88, "PULAR")
    draw_control_hint(550, 438, "Z", 30, "ATACAR")
    draw_control_hint(245, 474, "SHIFT", 68, "DASH")
    draw_control_hint(410, 474, "P", 30, "PAUSAR")
    draw_control_hint(575, 474, "ESC", 52, "MENU")


def on_mouse_move(pos):
    global mouse_position
    mouse_position = pos


def draw_end_screen(title, subtitle):
    draw_background()
    screen.draw.filled_rect(Rect(220, 140, 520, 260), (25, 28, 39))
    screen.draw.rect(Rect(220, 140, 520, 260), (214, 173, 91))
    screen.draw.text(
        title, center=(480, 205), fontsize=52, color=(246, 208, 103)
    )
    screen.draw.text(
        subtitle, center=(480, 267), fontsize=25, color=(232, 232, 222)
    )
    screen.draw.text(
        f"PONTUACAO FINAL: {score}",
        center=(480, 310),
        fontsize=25,
        color=(246, 208, 103),
    )
    screen.draw.text(
        "R - jogar novamente     ESC - menu",
        center=(480, 355),
        fontsize=21,
        color=(169, 181, 190),
    )


def draw_world():
    draw_background()
    draw_platforms()
    draw_exit()
    draw_coins_and_potions()
    for enemy in enemies:
        if enemy.alive:
            enemy.draw()
    hero.draw()
    draw_interface()


def draw_pause():
    screen.draw.filled_rect(Rect(260, 175, 440, 190), (20, 23, 34))
    screen.draw.rect(Rect(260, 175, 440, 190), (214, 173, 91))
    screen.draw.text(
        "JOGO PAUSADO",
        center=(480, 225),
        fontsize=43,
        color=(246, 208, 103),
    )
    screen.draw.text(
        "P - continuar     ESC - menu",
        center=(480, 295),
        fontsize=25,
        color=(232, 232, 222),
    )


def draw():
    if game_state == "menu":
        draw_menu()
        return
    if game_state in ("victory", "game_over"):
        title = "SELO RESTAURADO!" if game_state == "victory" else "FIM DE JOGO"
        subtitle = (
            "As sombras deixaram Eldoria."
            if game_state == "victory"
            else "O guardiao ainda protege a cripta."
        )
        draw_end_screen(title, subtitle)
        return

    draw_world()
    if game_state == "paused":
        draw_pause()


def on_key_down(key):
    global game_state
    if game_state == "playing":
        if key in (keys.SPACE, keys.W, keys.UP):
            hero.jump()
        elif key in (keys.Z, keys.X):
            hero.attack()
        elif key in (keys.LSHIFT, keys.RSHIFT, keys.C):
            hero.dash()
        elif key == keys.P:
            game_state = "paused"
        elif key == keys.ESCAPE:
            game_state = "menu"
    elif game_state == "paused":
        if key == keys.P:
            game_state = "playing"
        elif key == keys.ESCAPE:
            game_state = "menu"
    elif game_state in ("victory", "game_over"):
        if key == keys.R:
            start_game()
        elif key == keys.ESCAPE:
            game_state = "menu"
    elif game_state == "menu" and key in (keys.RETURN, keys.SPACE):
        start_game()


def on_mouse_down(pos):
    global game_state, sound_enabled, music_started
    if game_state != "menu":
        return
    if START_BUTTON.collidepoint(pos):
        start_game()
    elif SOUND_BUTTON.collidepoint(pos):
        sound_enabled = not sound_enabled
        play_sound("select")
        if sound_enabled:
            start_music()
        else:
            music.stop()
            music_started = False
    elif EXIT_BUTTON.collidepoint(pos):
        raise SystemExit
