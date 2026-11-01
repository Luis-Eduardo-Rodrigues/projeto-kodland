from pygame import Rect


WIDTH = 960
HEIGHT = 540
TITLE = "Guerreiro Vs O Guardião"

GRAVITY = 1450
MOVE_SPEED = 240
JUMP_SPEED = -610
MAX_LIVES = 3

PANEL = (24, 29, 41)
TEXT = (241, 238, 226)
SOFT_TEXT = (171, 182, 191)
ACCENT = (229, 165, 72)

START_BUTTON = Rect(330, 220, 300, 52)
SOUND_BUTTON = Rect(330, 288, 300, 48)
EXIT_BUTTON = Rect(330, 352, 300, 48)


def animation(prefix, count):
    return {
        direction: [f"{prefix}_{direction}_{index}" for index in range(count)]
        for direction in ("l", "r")
    }


HERO_ANIMATIONS = {
    "idle": animation("warrior_idle", 14),
    "run": animation("warrior_run", 8),
    "jump": animation("warrior_jump", 6),
    "attack": animation("warrior_attack", 8),
}

ENEMY_ANIMATIONS = {
    "spider": {
        "idle": animation("spider_idle", 3),
        "walk": animation("spider_walk", 5),
    },
    "bat": {
        "idle": animation("bat_idle", 4),
        "walk": animation("bat_walk", 4),
    },
    "mummy": {
        "idle": animation("mummy_idle", 4),
        "walk": animation("mummy_walk", 4),
    },
    "guardian": {
        "idle": animation("guardian_idle", 4),
        "walk": animation("guardian_walk", 4),
    },
}

LEVELS = [
    {
        "name": "O Vilarejo de Arven",
        "spawn": (55, 500),
        "door": Rect(890, 430, 45, 70),
        "platforms": [
            (0, 500, 960, 40),
            (170, 415, 180, 20),
            (420, 340, 180, 20),
            (675, 415, 175, 20),
        ],
        "coins": [
            (220, 375), (300, 375), (470, 300),
            (550, 300), (730, 375), (810, 375),
        ],
        "enemies": [
            ("spider", 390, 500, 350, 520),
            ("mummy", 620, 500, 570, 750),
            ("spider", 720, 415, 685, 840),
        ],
    },
    {
        "name": "A Cripta do Guardião",
        "spawn": (55, 500),
        "door": Rect(890, 430, 45, 70),
        "platforms": [
            (0, 500, 960, 40),
            (145, 405, 175, 20),
            (385, 330, 180, 20),
            (640, 405, 175, 20),
        ],
        "coins": [
            (195, 365), (275, 365), (435, 290),
            (515, 290), (690, 365), (770, 365),
        ],
        "enemies": [
            ("mummy", 345, 500, 300, 480),
            ("bat", 470, 330, 390, 560),
            ("guardian", 770, 500, 680, 870),
        ],
    },
]


game_state = "menu"
sound_on = True
music_started = False
level_index = 0
level = None
platforms = []
coins = []
enemies = []
hero = None
world_time = 0
mouse_position = (-1, -1)


def play_sound(name):
    if not sound_on:
        return
    try:
        getattr(sounds, name).play()
    except Exception:
        pass


def start_music():
    global music_started
    if sound_on and not music_started:
        try:
            music.play("old_tower_inn")
            music.set_volume(0.25)
            music_started = True
        except Exception:
            pass


class AnimatedCharacter:
    def __init__(self, animations, first_image):
        self.animations = animations
        self.actor = Actor(first_image, anchor=("center", "bottom"))
        self.direction = "r"
        self.state = "idle"
        self.frame = 0
        self.frame_time = 0

    def animate(self, state, dt, speed=9):
        if state != self.state:
            self.state = state
            self.frame = 0
            self.frame_time = 0
        frames = self.animations[state][self.direction]
        self.frame_time += dt
        if self.frame_time >= 1 / speed:
            self.frame_time = 0
            self.frame = (self.frame + 1) % len(frames)
        self.actor.image = frames[self.frame]


class Hero(AnimatedCharacter):
    def __init__(self, spawn):
        super().__init__(HERO_ANIMATIONS, "warrior_idle_r_0")
        self.spawn = spawn
        self.rect = Rect(0, 0, 34, 58)
        self.velocity_y = 0
        self.on_ground = False
        self.attack_time = 0
        self.attack_id = 0
        self.invulnerable = 0
        self.jump_buffer = 0
        self.coyote_time = 0
        self.lives = MAX_LIVES
        self.respawn()

    def respawn(self):
        self.rect.midbottom = self.spawn
        self.velocity_y = 0
        self.on_ground = True
        self.jump_buffer = 0
        self.coyote_time = 0.12
        self.actor.midbottom = self.rect.midbottom

    def move_horizontal(self, distance):
        old_rect = self.rect.copy()
        self.rect.x += round(distance)
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
        for platform in platforms:
            if not self.rect.colliderect(platform):
                continue
            if distance > 0 and old_rect.right <= platform.left:
                self.rect.right = platform.left
            elif distance < 0 and old_rect.left >= platform.right:
                self.rect.left = platform.right

    def move_vertical(self, dt):
        old_rect = self.rect.copy()
        self.velocity_y += GRAVITY * dt
        self.rect.y += round(self.velocity_y * dt)
        self.on_ground = False
        for platform in platforms:
            horizontal_overlap = (
                self.rect.right > platform.left + 4
                and self.rect.left < platform.right - 4
            )
            landing = (
                horizontal_overlap
                and self.velocity_y >= 0
                and old_rect.bottom <= platform.top + 4
                and self.rect.bottom >= platform.top
            )
            hit_ceiling = (
                horizontal_overlap
                and self.velocity_y < 0
                and old_rect.top >= platform.bottom - 4
                and self.rect.top <= platform.bottom
            )
            if landing:
                self.rect.bottom = platform.top
                self.velocity_y = 0
                self.on_ground = True
                break
            if hit_ceiling:
                self.rect.top = platform.bottom
                self.velocity_y = 0
                break

    def jump(self):
        self.jump_buffer = 0.15

    def try_jump(self):
        if self.jump_buffer > 0 and self.coyote_time > 0:
            self.velocity_y = JUMP_SPEED
            self.on_ground = False
            self.jump_buffer = 0
            self.coyote_time = 0
            play_sound("jump")

    def attack(self):
        if self.attack_time <= 0:
            self.attack_time = 0.42
            self.attack_id += 1
            play_sound("sword")

    def attack_box(self):
        if self.direction == "r":
            return Rect(self.rect.right, self.rect.y + 8, 55, 42)
        return Rect(self.rect.left - 55, self.rect.y + 8, 55, 42)

    def take_damage(self):
        global game_state
        if self.invulnerable > 0:
            return
        self.lives -= 1
        play_sound("hit")
        if self.lives <= 0:
            game_state = "game_over"
        else:
            self.invulnerable = 1
            self.respawn()

    def update(self, dt):
        direction_value = (keyboard.right or keyboard.d) - (
            keyboard.left or keyboard.a
        )
        moving = direction_value != 0
        if direction_value:
            self.direction = "r" if direction_value > 0 else "l"
        self.jump_buffer = max(0, self.jump_buffer - dt)
        if self.on_ground:
            self.coyote_time = 0.12
        else:
            self.coyote_time = max(0, self.coyote_time - dt)
        self.try_jump()
        self.move_horizontal(direction_value * MOVE_SPEED * dt)
        self.move_vertical(dt)
        if self.on_ground:
            self.coyote_time = 0.12
            self.try_jump()
        self.attack_time = max(0, self.attack_time - dt)
        self.invulnerable = max(0, self.invulnerable - dt)

        if self.attack_time > 0:
            state = "attack"
        elif not self.on_ground:
            state = "jump"
        elif moving:
            state = "run"
        else:
            state = "idle"
        self.animate(state, dt, 12 if state == "attack" else 9)
        self.actor.midbottom = self.rect.midbottom

    def draw(self):
        if self.invulnerable <= 0 or int(self.invulnerable * 12) % 2:
            self.actor.draw()


class Enemy(AnimatedCharacter):
    SIZES = {
        "spider": (42, 30),
        "bat": (48, 32),
        "mummy": (38, 62),
        "guardian": (54, 88),
    }
    HEALTH = {"spider": 1, "bat": 1, "mummy": 2, "guardian": 3}

    def __init__(self, kind, x, floor_y, left, right):
        super().__init__(ENEMY_ANIMATIONS[kind], f"{kind}_idle_r_0")
        self.kind = kind
        self.rect = Rect(0, 0, *self.SIZES[kind])
        self.rect.midbottom = (x, floor_y)
        if kind == "bat":
            self.rect.y -= 42
        self.left = left
        self.right = right
        self.speed = 55 if kind in ("mummy", "guardian") else 70
        self.movement = 1
        self.pause = 0 if kind == "bat" else 0.3
        self.health = self.HEALTH[kind]
        self.last_attack = -1
        self.alive = True
        if kind == "bat":
            self.actor.center = self.rect.center
        else:
            self.actor.midbottom = self.rect.midbottom

    def update(self, dt):
        if self.pause > 0 and self.kind != "bat":
            self.pause -= dt
            state = "idle"
        else:
            state = "walk"
            self.rect.x += round(self.speed * self.movement * dt)
            if self.rect.left <= self.left:
                self.rect.left = self.left
                self.movement = 1
                self.pause = 0 if self.kind == "bat" else 0.35
            elif self.rect.right >= self.right:
                self.rect.right = self.right
                self.movement = -1
                self.pause = 0 if self.kind == "bat" else 0.35
        self.direction = "r" if self.movement > 0 else "l"
        if self.kind == "bat":
            self.actor.center = self.rect.center
        else:
            self.actor.midbottom = self.rect.midbottom
        self.animate(state, dt)

    def take_hit(self, attack_id):
        if attack_id == self.last_attack:
            return
        self.last_attack = attack_id
        self.health -= 1
        play_sound("hit")
        if self.health <= 0:
            self.alive = False

    def draw(self):
        self.actor.draw()


def load_level(index, lives=MAX_LIVES):
    global level, platforms, coins, enemies, hero
    level = LEVELS[index]
    platforms = [Rect(*values) for values in level["platforms"]]
    coins = [
        {"position": position, "taken": False}
        for position in level["coins"]
    ]
    enemies = [Enemy(*values) for values in level["enemies"]]
    hero = Hero(level["spawn"])
    hero.lives = lives


def start_game():
    global game_state, level_index
    level_index = 0
    game_state = "playing"
    load_level(level_index)
    play_sound("select")
    start_music()


def door_is_open():
    return all(coin["taken"] for coin in coins) and not any(
        enemy.alive for enemy in enemies
    )


def update(dt):
    global world_time, game_state, level_index
    world_time += dt
    start_music()
    if game_state != "playing":
        return

    hero.update(dt)
    for enemy in enemies:
        if not enemy.alive:
            continue
        enemy.update(dt)
        if hero.attack_time > 0 and hero.attack_box().colliderect(enemy.rect):
            enemy.take_hit(hero.attack_id)
        if enemy.alive and hero.rect.colliderect(enemy.rect):
            hero.take_damage()
            if game_state == "game_over":
                return

    for coin in coins:
        if not coin["taken"] and hero.rect.collidepoint(coin["position"]):
            coin["taken"] = True
            play_sound("coin")

    if hero.rect.colliderect(level["door"]) and door_is_open():
        level_index += 1
        if level_index == len(LEVELS):
            game_state = "victory"
        else:
            load_level(level_index, hero.lives)


def draw_background():
    screen.fill((48, 72, 104))
    screen.draw.filled_circle((800, 100), 42, (244, 216, 142))
    screen.draw.filled_rect(Rect(0, 360, WIDTH, 180), (32, 48, 70))
    for x, height in ((0, 55), (85, 90), (190, 65), (690, 60), (805, 100)):
        building = Rect(x, 360 - height, 90, height)
        screen.draw.filled_rect(building, (35, 51, 73))


def draw_platforms():
    for platform in platforms:
        screen.draw.filled_rect(platform, (82, 79, 78))
        screen.draw.filled_rect(
            Rect(platform.x, platform.y, platform.width, 5),
            (172, 149, 100),
        )


def draw_objects():
    for coin in coins:
        if coin["taken"]:
            continue
        x, y = coin["position"]
        screen.draw.filled_circle((x, y), 9, (245, 187, 45))
        screen.draw.circle((x, y), 9, (255, 229, 120))

    door = level["door"]
    color = (160, 110, 46) if door_is_open() else (76, 48, 43)
    screen.draw.filled_rect(door, color)
    screen.draw.rect(door, (225, 185, 100))


def draw_hud():
    collected = sum(coin["taken"] for coin in coins)
    screen.draw.filled_rect(Rect(15, 15, 460, 46), PANEL)
    text = (
        f"Fase {level_index + 1}/2    Vidas {hero.lives}/{MAX_LIVES}    "
        f"Moedas {collected}/{len(coins)}"
    )
    screen.draw.text(text, midleft=(30, 38), fontsize=20, color=TEXT)
    if not door_is_open():
        screen.draw.text(
            "Pegue as moedas e derrote os inimigos.",
            midright=(940, 38),
            fontsize=17,
            color=TEXT,
        )


def draw_button(rect, text):
    color = ACCENT if rect.collidepoint(mouse_position) else (45, 55, 73)
    screen.draw.filled_rect(rect, color)
    screen.draw.rect(rect, (242, 193, 113))
    screen.draw.text(text, center=rect.center, fontsize=23, color=TEXT)


def draw_menu():
    draw_background()
    screen.draw.filled_rect(Rect(265, 35, 430, 445), PANEL)
    screen.draw.text("Guerreiro", center=(480, 88), fontsize=48, color=ACCENT)
    screen.draw.text(
        "vs. o Guardião",
        center=(480, 130),
        fontsize=29,
        color=TEXT,
    )
    screen.draw.text(
        "Uma pequena aventura medieval",
        center=(480, 172),
        fontsize=18,
        color=SOFT_TEXT,
    )
    draw_button(START_BUTTON, "Jogar")
    draw_button(SOUND_BUTTON, "Som ligado" if sound_on else "Som desligado")
    draw_button(EXIT_BUTTON, "Sair")
    screen.draw.text(
        "A/D mover   ESPAÇO pular   Z atacar",
        center=(480, 438),
        fontsize=17,
        color=SOFT_TEXT,
    )


def draw_end_screen():
    draw_background()
    title = "Você venceu!" if game_state == "victory" else "Tente novamente"
    screen.draw.filled_rect(Rect(270, 145, 420, 230), PANEL)
    screen.draw.text(title, center=(480, 215), fontsize=42, color=ACCENT)
    screen.draw.text(
        "R para recomeçar   ESC para o menu",
        center=(480, 300),
        fontsize=20,
        color=TEXT,
    )


def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state in ("victory", "game_over"):
        draw_end_screen()
    else:
        draw_background()
        draw_platforms()
        draw_objects()
        for enemy in enemies:
            if enemy.alive:
                enemy.draw()
        hero.draw()
        draw_hud()


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


def on_mouse_move(pos):
    global mouse_position
    mouse_position = pos


def on_mouse_down(pos):
    global sound_on, music_started
    if game_state != "menu":
        return
    if START_BUTTON.collidepoint(pos):
        start_game()
    elif SOUND_BUTTON.collidepoint(pos):
        sound_on = not sound_on
        if sound_on:
            start_music()
            play_sound("select")
        else:
            music.stop()
            music_started = False
    elif EXIT_BUTTON.collidepoint(pos):
        raise SystemExit
