import math
import random

from pygame import Rect


WIDTH = 960
HEIGHT = 540
TITLE = "O Cavaleiro de Valedouro"

GRAVITY = 1450
MOVE_SPEED = 245
JUMP_SPEED = -540

START_BUTTON = Rect(300, 250, 360, 56)
SOUND_BUTTON = Rect(300, 326, 360, 56)
EXIT_BUTTON = Rect(300, 402, 360, 56)


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
        "idle": animation("bat_idle", 5),
        "walk": animation("bat_walk", 5),
    },
    "mummy": {
        "idle": animation("mummy_idle", 4),
        "walk": animation("mummy_walk", 4),
        "attack": animation("mummy_attack", 5),
    },
}


LEVELS = [
    {
        "name": "A VILA DE VALEDOURO",
        "sky": (70, 126, 152),
        "horizon": (45, 76, 86),
        "stone": (99, 84, 70),
        "spawn": (54, 500),
        "exit": Rect(888, 430, 46, 70),
        "platforms": [
            (0, 500, 960, 40),
            (145, 420, 190, 22),
            (400, 348, 190, 22),
            (670, 414, 160, 22),
        ],
        "coins": [(205, 380), (280, 380), (455, 308), (535, 308),
                  (730, 374), (805, 374), (855, 462)],
        "enemies": [
            ("spider", 370, 500, 330, 500),
            ("spider", 700, 414, 680, 805),
            ("mummy", 610, 500, 570, 750),
        ],
    },
    {
        "name": "AS MURALHAS DO NORTE",
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
        "coins": [(160, 384), (250, 384), (400, 310), (485, 310),
                  (625, 365), (700, 365), (805, 290), (885, 290)],
        "enemies": [
            ("spider", 160, 424, 125, 260),
            ("bat", 410, 350, 340, 525),
            ("mummy", 650, 405, 595, 735),
            ("bat", 800, 330, 755, 915),
        ],
    },
    {
        "name": "A MASMORRA ESQUECIDA",
        "sky": (22, 25, 38),
        "horizon": (33, 34, 48),
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
        "coins": [(175, 370), (245, 370), (390, 290), (470, 290),
                  (625, 370), (700, 370), (800, 290), (870, 290),
                  (825, 462)],
        "enemies": [
            ("mummy", 300, 500, 260, 440),
            ("spider", 600, 410, 590, 730),
            ("bat", 410, 330, 345, 515),
            ("mummy", 760, 500, 710, 870),
            ("bat", 800, 330, 755, 910),
        ],
    },
]


random.seed(17)
STARS = [(random.randint(20, 940), random.randint(30, 225))
         for _ in range(36)]

game_state = "menu"
sound_enabled = True
music_started = False
level_index = 0
level = None
platforms = []
coins = []
enemies = []
hero = None
world_time = 0
banner_timer = 0
message = ""
message_timer = 0


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
        self.frame_clock += dt
        if self.frame_clock >= 1 / frames_per_second:
            self.frame_clock = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
        self.actor.image = frames[self.frame_index]


class Hero(AnimatedCharacter):
    def __init__(self, spawn):
        super().__init__(HERO_ANIMATIONS, "hero_idle_r_0")
        self.rect = Rect(0, 0, 34, 58)
        self.spawn = spawn
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.attack_timer = 0
        self.attack_number = 0
        self.invulnerable = 0
        self.lives = 3
        self.respawn()

    def respawn(self):
        self.rect.midbottom = self.spawn
        self.velocity_x = 0
        self.velocity_y = 0
        self.actor.midbottom = self.rect.midbottom

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False
            play_sound("jump")

    def attack(self):
        if self.attack_timer <= 0:
            self.attack_timer = 0.42
            self.attack_number += 1
            play_sound("sword")

    def attack_box(self):
        if self.direction == "r":
            return Rect(self.rect.right - 3, self.rect.y + 8, 55, 42)
        return Rect(self.rect.left - 52, self.rect.y + 8, 55, 42)

    def take_damage(self):
        global game_state
        if self.invulnerable > 0:
            return
        self.lives -= 1
        self.invulnerable = 1.4
        play_sound("hit")
        if self.lives <= 0:
            game_state = "game_over"
        else:
            self.respawn()

    def update(self, dt):
        moving_left = keyboard.left or keyboard.a
        moving_right = keyboard.right or keyboard.d
        self.velocity_x = MOVE_SPEED * (moving_right - moving_left)
        if self.velocity_x:
            self.direction = "r" if self.velocity_x > 0 else "l"

        self.rect.x += round(self.velocity_x * dt)
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        previous_bottom = self.rect.bottom
        self.velocity_y += GRAVITY * dt
        self.rect.y += round(self.velocity_y * dt)
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
                self.velocity_y = 0
                self.on_ground = True
                break

        self.attack_timer = max(0, self.attack_timer - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        if self.rect.top > HEIGHT:
            self.take_damage()

        if self.attack_timer > 0:
            state = "attack"
        elif not self.on_ground:
            state = "jump" if self.velocity_y < 0 else "fall"
        elif self.velocity_x:
            state = "run"
        else:
            state = "idle"
        self.animate(state, dt, 12 if state == "attack" else 10)
        self.actor.midbottom = self.rect.midbottom

    def draw(self):
        if self.invulnerable <= 0 or int(self.invulnerable * 12) % 2:
            self.actor.draw()


class Enemy(AnimatedCharacter):
    def __init__(self, kind, x, floor_y, patrol_left, patrol_right):
        animations = ENEMY_ANIMATIONS[kind]
        super().__init__(animations, f"{kind}_idle_r_0")
        self.kind = kind
        width, height = (42, 30) if kind != "mummy" else (38, 62)
        self.rect = Rect(0, 0, width, height)
        self.rect.midbottom = (x, floor_y)
        if kind == "bat":
            self.rect.y -= 82
        self.base_y = self.rect.y
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.speed = {"spider": 68, "bat": 82, "mummy": 55}[kind]
        self.direction_value = 1
        self.pause_timer = random.uniform(0.15, 0.55)
        self.phase = random.random() * math.tau
        self.health = 2 if kind == "mummy" else 1
        self.last_attack = -1
        self.alive = True
        if kind == "bat":
            self.actor.center = self.rect.center
        else:
            self.actor.midbottom = self.rect.midbottom

    def take_hit(self, attack_number):
        if attack_number == self.last_attack:
            return
        self.last_attack = attack_number
        self.health -= 1
        play_sound("hit")
        if self.health <= 0:
            self.alive = False

    def update(self, dt):
        if self.pause_timer > 0:
            self.pause_timer -= dt
            state = "idle"
        elif self.kind == "mummy" and abs(
                self.rect.centerx - hero.rect.centerx) < 58:
            state = "attack"
        else:
            state = "walk"
            self.rect.x += round(self.speed * self.direction_value * dt)
            if self.rect.left <= self.patrol_left:
                self.rect.left = self.patrol_left
                self.direction_value = 1
                self.pause_timer = 0.5
            elif self.rect.right >= self.patrol_right:
                self.rect.right = self.patrol_right
                self.direction_value = -1
                self.pause_timer = 0.5

        self.direction = "r" if self.direction_value > 0 else "l"
        if self.kind == "bat":
            self.rect.y = self.base_y + math.sin(world_time * 4 + self.phase) * 8
            self.actor.center = self.rect.center
        else:
            self.actor.midbottom = self.rect.midbottom
        self.animate(state, dt, 9)

    def draw(self):
        self.actor.draw()


def load_level(index):
    global level, platforms, coins, enemies, hero, banner_timer
    level = LEVELS[index]
    platforms = [Rect(*values) for values in level["platforms"]]
    coins = [{"position": position, "taken": False}
             for position in level["coins"]]
    enemies = [Enemy(*values) for values in level["enemies"]]
    lives = hero.lives if hero else 3
    hero = Hero(level["spawn"])
    hero.lives = lives
    banner_timer = 1.8


def start_game():
    global game_state, level_index
    level_index = 0
    game_state = "playing"
    load_level(level_index)
    play_sound("select")
    start_music()


def next_level():
    global level_index, game_state
    play_sound("level_up")
    level_index += 1
    if level_index >= len(LEVELS):
        game_state = "victory"
    else:
        load_level(level_index)


def remaining_coins():
    return sum(not coin["taken"] for coin in coins)


def update(dt):
    global world_time, banner_timer, message_timer, message
    world_time += dt
    start_music()
    banner_timer = max(0, banner_timer - dt)
    message_timer = max(0, message_timer - dt)

    if game_state != "playing":
        return

    hero.update(dt)
    for enemy in enemies:
        if enemy.alive:
            enemy.update(dt)
            if (hero.attack_timer > 0
                    and hero.attack_box().colliderect(enemy.rect)):
                enemy.take_hit(hero.attack_number)
            if enemy.alive and enemy.rect.colliderect(hero.rect):
                hero.take_damage()

    for coin in coins:
        x, y = coin["position"]
        if not coin["taken"] and hero.rect.collidepoint(x, y):
            coin["taken"] = True
            play_sound("coin")

    if hero.rect.colliderect(level["exit"]):
        if remaining_coins() == 0:
            next_level()
        else:
            message = "COLETE TODAS AS MOEDAS!"
            message_timer = 1.0


def draw_background():
    data = level if level else LEVELS[0]
    screen.fill(data["sky"])
    if data is LEVELS[2]:
        for x, y in STARS:
            screen.draw.filled_circle((x, y), 1, (148, 160, 181))
        screen.draw.filled_circle((790, 105), 44, (188, 195, 194))
    else:
        screen.draw.filled_circle((790, 105), 38, (242, 218, 145))

    horizon = data["horizon"]
    for index, height in enumerate((150, 205, 175, 240, 190, 225)):
        x = index * 180 - 35
        screen.draw.filled_rect(Rect(x, 500 - height, 150, height), horizon)
        screen.draw.filled_rect(Rect(x + 38, 500 - height - 34, 74, 34), horizon)
    for x in (90, 815):
        screen.draw.filled_rect(Rect(x, 265, 60, 235), horizon)
        screen.draw.filled_rect(Rect(x - 12, 245, 84, 25), horizon)


def draw_platforms():
    for platform in platforms:
        screen.draw.filled_rect(platform, level["stone"])
        screen.draw.filled_rect(
            Rect(platform.x, platform.y, platform.width, 5), (167, 145, 99)
        )
        for x in range(platform.left + 12, platform.right, 34):
            screen.draw.line(
                (x, platform.top + 7),
                (x, min(platform.bottom - 2, platform.top + 18)),
                (55, 49, 49),
            )


def draw_exit():
    door = level["exit"]
    color = (91, 54, 38) if remaining_coins() else (146, 101, 43)
    screen.draw.filled_rect(door, color)
    screen.draw.rect(door, (220, 180, 100))
    screen.draw.filled_circle(
        (door.right - 10, door.centery), 3, (236, 206, 105)
    )


def draw_coins():
    for coin in coins:
        if coin["taken"]:
            continue
        x, y = coin["position"]
        radius = 9 + round(math.sin(world_time * 6 + x) * 2)
        screen.draw.filled_circle((x, y), radius, (246, 188, 45))
        screen.draw.circle((x, y), radius, (255, 230, 122))
        screen.draw.line((x, y - 5), (x, y + 5), (184, 118, 28))


def draw_interface():
    collected = len(coins) - remaining_coins()
    screen.draw.filled_rect(Rect(14, 14, 326, 55), (20, 23, 34))
    screen.draw.text(
        f"FASE {level_index + 1}/3   VIDAS: {hero.lives}   "
        f"MOEDAS: {collected}/{len(coins)}",
        (28, 30), fontsize=24, color=(245, 232, 190)
    )

    if banner_timer > 0:
        screen.draw.filled_rect(Rect(220, 90, 520, 58), (20, 23, 34))
        screen.draw.text(
            level["name"], center=(480, 119), fontsize=32,
            color=(246, 208, 103)
        )
    if message_timer > 0:
        screen.draw.text(
            message, center=(480, 185), fontsize=28,
            color=(255, 220, 105), owidth=1, ocolor=(30, 25, 25)
        )


def draw_button(rect, text, active=False):
    color = (150, 98, 45) if active else (88, 61, 51)
    screen.draw.filled_rect(rect, color)
    screen.draw.rect(rect, (226, 190, 111))
    screen.draw.text(
        text, center=rect.center, fontsize=29, color=(255, 239, 196)
    )


def draw_menu():
    draw_background()
    screen.draw.filled_rect(Rect(245, 62, 470, 410), (25, 28, 39))
    screen.draw.rect(Rect(245, 62, 470, 410), (214, 173, 91))
    screen.draw.text(
        "O CAVALEIRO", center=(480, 120), fontsize=52,
        color=(246, 208, 103)
    )
    screen.draw.text(
        "DE VALEDOURO", center=(480, 166), fontsize=42,
        color=(232, 232, 222)
    )
    screen.draw.text(
        "Uma aventura medieval", center=(480, 207), fontsize=22,
        color=(169, 181, 190)
    )
    draw_button(START_BUTTON, "COMECAR O JOGO", True)
    sound_text = (
        "MUSICA E SONS: LIGADOS"
        if sound_enabled
        else "MUSICA E SONS: DESLIGADOS"
    )
    draw_button(SOUND_BUTTON, sound_text)
    draw_button(EXIT_BUTTON, "SAIR")


def draw_end_screen(title, subtitle):
    draw_background()
    screen.draw.filled_rect(Rect(220, 140, 520, 260), (25, 28, 39))
    screen.draw.rect(Rect(220, 140, 520, 260), (214, 173, 91))
    screen.draw.text(
        title, center=(480, 210), fontsize=52, color=(246, 208, 103)
    )
    screen.draw.text(
        subtitle, center=(480, 280), fontsize=26, color=(232, 232, 222)
    )
    screen.draw.text(
        "R - jogar novamente     ESC - menu",
        center=(480, 345), fontsize=23, color=(169, 181, 190)
    )


def draw():
    if game_state == "menu":
        draw_menu()
        return
    if game_state in ("victory", "game_over"):
        title = "VITORIA!" if game_state == "victory" else "FIM DE JOGO"
        subtitle = (
            "Valedouro esta a salvo!"
            if game_state == "victory"
            else "O cavaleiro precisa tentar outra vez."
        )
        draw_end_screen(title, subtitle)
        return

    draw_background()
    draw_platforms()
    draw_exit()
    draw_coins()
    for enemy in enemies:
        if enemy.alive:
            enemy.draw()
    hero.draw()
    draw_interface()


def on_key_down(key):
    global game_state
    if game_state == "playing":
        if key in (keys.SPACE, keys.W, keys.UP):
            hero.jump()
        elif key in (keys.Z, keys.X):
            hero.attack()
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
