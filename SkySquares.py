import pygame
import random
import sys
from dataclasses import dataclass


# CONFIGURACIÓN BÁSICA

WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "Sky Squares: ¡evita los malos y recoge estrellas!"

COLORS = {
    "bg": (18, 18, 28),
    "player": (120, 200, 255),
    "enemy": (255, 105, 97),
    "coin": (255, 221, 121),
    "text": (235, 235, 245),
    "panel": (30, 30, 45),
    "accent": (160, 140, 255),
}

# ESTADOS DEL JUEGO

MENU, PLAYING, PAUSED, GAMEOVER = "MENU", "PLAYING", "PAUSED", "GAMEOVER"

# ENTIDADES

@dataclass
class Player:
    x: float
    y: float
    w: int = 40
    h: int = 40
    speed: float = 320.0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

@dataclass
class Enemy:
    x: float
    y: float
    vx: float
    vy: float
    size: int

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

@dataclass
class Coin:
    x: float
    y: float
    size: int = 20
    vy: float = 140.0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)


# FUNCIONES DE UTILIDAD

def draw_text(surf, text, x, y, font, color=COLORS["text"], center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surf.blit(img, rect)

def spawn_enemy(level_speed: float) -> Enemy:
    size = random.randint(28, 48)
    x = random.randint(0, WIDTH - size)
    y = -size
    # velocidad aumenta con nivel
    vy = random.uniform(120, 200) + level_speed
    vx = random.uniform(-40, 40)
    return Enemy(x, y, vx, vy, size)

def spawn_coin() -> Coin:
    x = random.randint(0, WIDTH - 20)
    y = -20
    return Coin(x, y)

def clamp(val, lo, hi):
    return max(lo, min(val, hi))

def reset_game():
    player = Player(WIDTH // 2 - 20, HEIGHT - 80)
    enemies = []
    coins = []
    score = 0
    lives = 3
    level_timer = 0.0
    level_speed = 0.0  # sube poco a poco para aumentar dificultad
    return player, enemies, coins, score, lives, level_timer, level_speed

# PANTALLAS

def draw_menu(screen, big, small, blink):
    screen.fill(COLORS["bg"])
    title = "Sky Squares"
    subtitle = "Flechas o A/D para moverte • ENTER para jugar"
    help1 = "P para pausar • ESC para salir"
    draw_text(screen, title, WIDTH // 2, HEIGHT // 2 - 80, big, COLORS["accent"], center=True)
    draw_text(screen, subtitle, WIDTH // 2, HEIGHT // 2 + 10, small, center=True)
    if blink:
        draw_text(screen, "Presiona ENTER", WIDTH // 2, HEIGHT // 2 + 60, small, COLORS["coin"], center=True)
    draw_text(screen, help1, WIDTH // 2, HEIGHT - 40, small, center=True)

def draw_pause(screen, big, small):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    draw_text(screen, "PAUSA", WIDTH // 2, HEIGHT // 2 - 20, big, COLORS["coin"], center=True)
    draw_text(screen, "ENTER: continuar • R: reiniciar • ESC: menú", WIDTH // 2, HEIGHT // 2 + 30, small, center=True)

def draw_gameover(screen, big, small, score):
    screen.fill(COLORS["bg"])
    draw_text(screen, "¡GAME OVER!", WIDTH // 2, HEIGHT // 2 - 20, big, COLORS["enemy"], center=True)
    draw_text(screen, f"Puntaje: {score}", WIDTH // 2, HEIGHT // 2 + 25, small, center=True)
    draw_text(screen, "ENTER: jugar de nuevo • ESC: menú", WIDTH // 2, HEIGHT // 2 + 55, small, center=True)


# BUCLE PRINCIPAL

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font_small = pygame.font.SysFont("consolas,menlo,dejavusansmono", 22)
    font_big = pygame.font.SysFont("consolas,menlo,dejavusansmono", 48, bold=True)

    state = MENU
    blink_timer = 0.0

    player, enemies, coins, score, lives, level_timer, level_speed = reset_game()
    enemy_spawn = 0.0
    coin_spawn = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # segundos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # ********* ESTADO: MENU *********
        if state == MENU:
            if keys[pygame.K_RETURN]:
                state = PLAYING
                player, enemies, coins, score, lives, level_timer, level_speed = reset_game()
                enemy_spawn = coin_spawn = 0.0

            if keys[pygame.K_ESCAPE]:
                running = False

            # Render menú
            blink_timer += dt
            draw_menu(screen, font_big, font_small, int(blink_timer * 2) % 2 == 0)
            pygame.display.flip()
            continue

        # ********* ESTADO: PAUSA *********
        if state == PAUSED:
            if keys[pygame.K_RETURN]:
                state = PLAYING
            elif keys[pygame.K_r]:
                state = PLAYING
                player, enemies, coins, score, lives, level_timer, level_speed = reset_game()
                enemy_spawn = coin_spawn = 0.0
            elif keys[pygame.K_ESCAPE]:
                state = MENU

            # Render pausa (overlay)
            draw_pause(screen, font_big, font_small)
            pygame.display.flip()
            continue

        # ********* ESTADO: GAME OVER *********
        if state == GAMEOVER:
            if keys[pygame.K_RETURN]:
                state = PLAYING
                player, enemies, coins, score, lives, level_timer, level_speed = reset_game()
                enemy_spawn = coin_spawn = 0.0
            elif keys[pygame.K_ESCAPE]:
                state = MENU

            draw_gameover(screen, font_big, font_small, score)
            pygame.display.flip()
            continue

        # ********* ESTADO: PLAYING *********
        if keys[pygame.K_p]:
            state = PAUSED

        # Movimiento del jugador
        move_x = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        player.x += move_x * player.speed * dt
        player.x = clamp(player.x, 0, WIDTH - player.w)

        # Spawns temporizados
        enemy_spawn += dt
        coin_spawn += dt
        level_timer += dt
        if enemy_spawn >= max(0.25, 0.9 - level_speed / 400.0):
            enemies.append(spawn_enemy(level_speed))
            enemy_spawn = 0.0
        if coin_spawn >= 0.8:
            coins.append(spawn_coin())
            coin_spawn = 0.0

        # Aumenta dificultad suave cada 10 s
        if level_timer >= 10.0:
            level_speed += 35.0
            level_timer = 0.0

        # Actualizar enemigos
        for e in enemies:
            e.x += e.vx * dt
            e.y += e.vy * dt
        enemies = [e for e in enemies if e.y < HEIGHT + e.size]

        # Actualizar monedas
        for c in coins:
            c.y += c.vy * dt
        coins = [c for c in coins if c.y < HEIGHT + c.size]

        # Colisiones
        preg = player.rect()
        hit_enemy = None
        for e in enemies:
            if preg.colliderect(e.rect()):
                hit_enemy = e
                break
        if hit_enemy:
            lives -= 1
            enemies.remove(hit_enemy)
            if lives <= 0:
                state = GAMEOVER

        got_coin = []
        for c in coins:
            if preg.colliderect(c.rect()):
                got_coin.append(c)
        if got_coin:
            for c in got_coin:
                coins.remove(c)
            score += 10 * len(got_coin)

        # DIBUJO
        screen.fill(COLORS["bg"])

        # HUD panel
        pygame.draw.rect(screen, COLORS["panel"], (0, 0, WIDTH, 46))
        draw_text(screen, f"Puntos: {score}", 12, 10, font_small)
        draw_text(screen, f"Vidas: {lives}", 240, 10, font_small)
        draw_text(screen, "P: Pausa", WIDTH - 130, 10, font_small)

        # Player
        pygame.draw.rect(screen, COLORS["player"], player.rect(), border_radius=8)

        # Enemigos
        for e in enemies:
            pygame.draw.rect(screen, COLORS["enemy"], e.rect(), border_radius=6)

        # Monedas
        for c in coins:
            pygame.draw.rect(screen, COLORS["coin"], c.rect(), border_radius=10)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
