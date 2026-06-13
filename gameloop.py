import pygame
import math
import random
from constants import ( FPS, 
                       SCREEN_W, SCREEN_H, 
                       OCEAN_BG, 
                       PLAYER_COLOR, WHITE, 
                       BUBBLE_COUNT, BUBBLE_COLOR, BUBBLE_RADIUS, BUBBLE_SPEED )
from player import Player
from spawner import Spawner
from hud import HUD


def _show_title_screen(screen):
    """
    Display the title screen before the first game starts.
    'Press SPACE to start' launches the game.
    Closing the window returns False so main.py can quit cleanly.
    """
    font_title   = pygame.font.SysFont("arial", 72, bold=True)
    font_sub     = pygame.font.SysFont("arial", 28)
    font_controls = pygame.font.SysFont("arial", 20)

    title_surf   = font_title.render("OCEAN EVOLUTION", True, (0, 200, 180))
    sub_surf     = font_sub.render("Press  SPACE  to start", True, WHITE)
    ctrl_surf    = font_controls.render("Move: WASD or Arrow Keys", True, (150, 200, 200))
    tagline_surf = font_sub.render("Eat. Grow. Become the Monster.", True, (100, 180, 160))

    cx, cy = SCREEN_W // 2, SCREEN_H // 2
    clock  = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True

        # Background gradient (reuse the same helper used in run_game)
        _draw_background(screen)

        screen.blit(title_surf,   title_surf.get_rect(center=(cx, cy - 100)))
        screen.blit(tagline_surf, tagline_surf.get_rect(center=(cx, cy - 20)))
        screen.blit(sub_surf,     sub_surf.get_rect(center=(cx, cy + 60)))
        screen.blit(ctrl_surf,    ctrl_surf.get_rect(center=(cx, cy + 100)))

        pygame.display.flip()
        clock.tick(30)


def _draw_background(screen):
    """Fill the screen with a single dark navy colour — deep ocean look."""
    screen.fill(OCEAN_BG)


def _make_bubbles():
    """
    Create the initial pool of bubble particle dicts.
    Each bubble is a plain dict — no class needed for something this simple.
    Fields: x, y, radius, speed (pixels/second upward).
    """
    bubbles = []
    for _ in range(BUBBLE_COUNT):
        bubbles.append({
            "x":      random.uniform(10, SCREEN_W - 10),
            "y":      random.uniform(0, SCREEN_H),       # spread across screen at start
            "radius": random.randint(2, BUBBLE_RADIUS + 1),
            "speed":  random.uniform(BUBBLE_SPEED * 0.6, BUBBLE_SPEED * 1.4),
        })
    return bubbles


def _update_bubbles(bubbles, dt):
    """
    Move each bubble upward. When it drifts off the top edge, wrap it
    back to the bottom at a new random x so the screen always has bubbles.
    """
    for b in bubbles:
        b["y"] -= b["speed"] * dt
        if b["y"] < -b["radius"]:          # drifted off the top
            b["y"] = SCREEN_H + b["radius"]
            b["x"] = random.uniform(10, SCREEN_W - 10)


def _draw_bubbles(screen, bubbles):
    """Draw each bubble as a small hollow circle (outline only looks more water-like)."""
    for b in bubbles:
        pygame.draw.circle(screen, BUBBLE_COLOR,
                           (int(b["x"]), int(b["y"])), b["radius"], 1)


def run_game(screen):
    """
    Contains the game loop. Called by main.py after pygame is set up.
    Returns when the player quits the window (not on death — death
    triggers the game-over screen, which then either restarts the loop
    or returns here to exit).
    """

    # Show the title screen once before the first game starts.
    if not _show_title_screen(screen):
        return   # player closed the window on the title screen

    while True:   # outer restart loop — re-runs a fresh game on 'Play Again'

        # ── Fresh game state ──────────────────────────────────────────
        # Create the player at the center of the screen
        player = Player(x=SCREEN_W // 2, y=SCREEN_H // 2)

        # Create the spawner (seeds 30 zooplankton immediately)
        spawner = Spawner()

        # Create the HUD renderer
        hud = HUD()

        clock = pygame.time.Clock()
        running = True
        prev_tier = 1
        evolution_flash_timer = 0.0   # seconds remaining for the white flash overlay
        bubbles = _make_bubbles()     # background bubble particles

        # ── Main game loop ──────────────────────────────────────────

        while running:

            # --- Events (closing the window) ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False # exit run_game entirely → main.py calls pygame.quit()

            # --- Delta time ---
            dt = clock.tick(FPS) / 1000.0   # seconds since last frame, e.g. 0.0167

            # --- Update ---
            keys = pygame.key.get_pressed()
            player.update(keys, dt)
            spawner.update(dt, player)

            # ── Tier change detection → activate/deactivate shark ─────
            if player.tier != prev_tier:
                if player.tier == 2:
                    spawner.activate_shark()
                if player.tier == 3:
                    spawner.deactivate_shark_chase()
                evolution_flash_timer = 0.3   # trigger the white flash on any tier-up
                prev_tier = player.tier

            # ── Collision detection + eating / dying ──────────────────────────────
            dead, won = _check_eating(player, spawner)
            if dead or won:
                running = False # break inner loop → show game-over screen

            # --- Draw ---
            #screen.fill(OCEAN_BG)           # paint ocean background first (repaints the whole background each frame. Without this, the circle leaves a trail as it moves.)
            _draw_background(screen)        # ocean depth gradient (top: dark navy, bottom: lighter blue)
            _update_bubbles(bubbles, dt)
            _draw_bubbles(screen, bubbles)
            spawner.draw(screen)
            player.draw(screen, PLAYER_COLOR)
            hud.draw(screen, player)


            # ── Evolution flash overlay ───────────────────────────────
            # Drawn last so it appears on top of everything else.
            # Alpha fades from ~200 → 0 as the timer counts down to 0,
            # giving a smooth fade-out rather than a hard cut.
            if evolution_flash_timer > 0:
                evolution_flash_timer -= dt
                # Map remaining time (0.3 → 0) to alpha (200 → 0)
                alpha = int(200 * (evolution_flash_timer / 0.3))
                flash_surf = pygame.Surface((SCREEN_W, SCREEN_H))
                flash_surf.set_alpha(max(0, alpha))
                flash_surf.fill(WHITE)
                screen.blit(flash_surf, (0, 0))
                # "EVOLVED!" text — centred, large, dark so it reads against white
                evolved_font = pygame.font.SysFont("arial", 64, bold=True)
                evolved_surf = evolved_font.render("EVOLVED!", True, (0, 80, 0))
                screen.blit(evolved_surf, evolved_surf.get_rect(
                    center=(SCREEN_W // 2, SCREEN_H // 2)))

            pygame.display.flip() # swap back-buffer to screen (prevents flicker)


        # ── End screen ────────────────────────────────────────────────
        # won=True  → victory screen; won=False → game-over screen.
        # Both return True (restart) or False (quit).
        if won:
            restart = _show_victory(screen, player.mass)
        else:
            restart = _show_game_over(screen, player.mass)
        if not restart:
            return   # exit run_game → main.py calls pygame.quit()


# ── Collision & eating logic ───────────────────────────────────────────

def _check_eating(player, spawner):
    """
    Check all collisions between the player and every entity this frame.
    Returns (dead, won): two booleans.
      dead=True  → player touched a lethal entity → caller triggers game over.
      won=True   → player (Tier 3) ate the shark  → caller triggers victory.
    Uses circle-circle overlap: distance(A,B) < A.radius + B.radius.
    """

    # ── 1. Zooplankton — always edible ───────────────────────────────
    eaten_zp = []
    for zp in list(spawner.zooplankton):
        '''
        dx = player.x - zp.x
        dy = player.y - zp.y
        distance = math.hypot(dx, dy)           # sqrt(dx² + dy²)
        '''
        '''
        if distance < player.radius + zp.radius:
            eaten.append(zp)
        '''
        if math.hypot(player.x - zp.x, player.y - zp.y) < player.radius + zp.radius:
            eaten_zp.append(zp)

            

    for zp in eaten_zp:
        player.eat(zp)
        spawner.notify_eaten(zp)

    # ── 2. SmallFish — depends on tier ───────────────────────────────
    for fish in list(spawner.fish):
        dist = math.hypot(player.x - fish.x, player.y - fish.y)
        if dist >= player.radius + fish.radius:
            continue   # no overlap — skip

        if player.tier == 1:
            # DANGER: fish kills player → signal game over immediately (Tier 1)
            return True, False    # dead, not won
        else:
            # PREY: Tier 2+ player eats the fish
            player.eat(fish)
            spawner.notify_fish_eaten(fish)


    # ── 3. Shark — depends on tier ───────────────────────────────────
    if spawner.shark:
        dist = math.hypot(player.x - spawner.shark.x, player.y - spawner.shark.y)
        if dist < player.radius + spawner.shark.radius:
            if player.tier < 3:
                return True, False   # dead, not won
            else:
                return False, True   # alive — player ate the shark, WIN

    return False, False   # survived this frame, game continues


# ── Game-over screen ───────────────────────────────────────────────────

def _show_game_over(screen, final_mass):
    """
    Show the game-over screen and wait for player input.
    Returns True if the player presses R to restart, False if they close the window.
    Draws a semi-transparent overlay over whatever is currently on screen.
    """
    font_big   = pygame.font.SysFont("arial", 56, bold=True)
    font_small = pygame.font.SysFont("arial", 28)

    title_surf  = font_big.render("YOU WERE EATEN", True, (220, 50, 50))
    mass_surf   = font_small.render(f"Final mass: {int(final_mass)}", True, WHITE)
    restart_surf = font_small.render("Press  R  to play again", True, (180, 230, 180))
    quit_surf   = font_small.render("Close the window to quit", True, (150, 150, 150))

    # Centre everything on screen
    cx, cy = SCREEN_W // 2, SCREEN_H // 2

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True

        # Semi-transparent dark overlay (draw a rect with alpha manually)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(180)          # 0 = fully transparent, 255 = opaque
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Blit each text surface, centred horizontally
        screen.blit(title_surf,   title_surf.get_rect(center=(cx, cy - 80)))
        screen.blit(mass_surf,    mass_surf.get_rect(center=(cx, cy)))
        screen.blit(restart_surf, restart_surf.get_rect(center=(cx, cy + 60)))
        screen.blit(quit_surf,    quit_surf.get_rect(center=(cx, cy + 100)))

        pygame.display.flip()
        clock.tick(30)


# ── Victory screen ─────────────────────────────────────────────────────

def _show_victory(screen, final_mass):
    """
    Render a victory overlay when the player eats the shark as a Tier 3 Monster.

    Structure mirrors _show_game_over exactly so the two screens behave
    consistently. Returns True (restart) or False (quit).

    WHY separate from _show_game_over?
    The copy is intentional: the two screens have different colours,
    titles, and flavour text. Merging them into one function with a flag
    would make both harder to read and modify independently.
    """
    font_big   = pygame.font.SysFont("arial", 52, bold=True)
    font_small = pygame.font.SysFont("arial", 28)

    title_surf   = font_big.render("YOU ARE THE MONSTER", True, (255, 210, 0))
    mass_surf    = font_small.render(f"Final mass: {int(final_mass)}", True, WHITE)
    restart_surf = font_small.render("Press  R  to play again", True, (180, 230, 180))
    quit_surf    = font_small.render("Close the window to quit", True, (150, 150, 150))

    cx, cy = SCREEN_W // 2, SCREEN_H // 2
    clock  = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True

        # Deep teal overlay — distinct from the black game-over overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H))
        overlay.set_alpha(200)
        overlay.fill((0, 40, 30))
        screen.blit(overlay, (0, 0))

        screen.blit(title_surf,   title_surf.get_rect(center=(cx, cy - 80)))
        screen.blit(mass_surf,    mass_surf.get_rect(center=(cx, cy)))
        screen.blit(restart_surf, restart_surf.get_rect(center=(cx, cy + 60)))
        screen.blit(quit_surf,    quit_surf.get_rect(center=(cx, cy + 100)))

        pygame.display.flip()
        clock.tick(30)