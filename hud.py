"""
hud.py – Heads-Up Display

Draws three things in the top-left corner every frame:
  1. Mass counter  – plain text: "Mass: 47"
  2. Evolution bar – a progress bar showing % toward the next tier threshold
  3. Tier name     – current form + threat status below the bar
"""

import pygame
from constants import (
    WHITE, BLACK,
    TIER_2_MASS, TIER_3_MASS,
    COLORS, HUD_X, MASS_Y, BAR_Y, BAR_W, BAR_H, BAR_BG_COLOR, BAR_FILL_COLOR, BAR_BORDER, FONT_SIZE )


# Vertical position for the tier-name line (below the progress bar)
TIER_NAME_Y = BAR_Y + BAR_H + 6


class HUD:
    """
    Stateless renderer – receives the player object and draws HUD elements.
    No game logic lives here; it only reads player data.
    """

    def __init__(self):
        """
        Initialise the font once and reuse it every frame.
        pygame.font.SysFont("arial", size) picks a clean system font.
        If Arial is missing, pygame falls back to its built-in font.
        Creted in __init__ instead of draw() to save resources - so it does not 
        run every FPS.
        """
        pygame.font.init()      # safe to call multiple times
        self.font = pygame.font.SysFont("arial", FONT_SIZE, bold=True)

    # ------------------------------------------------------------------
    # Public draw call – invoke inside game.py after all world drawing
    # ------------------------------------------------------------------

    def draw(self, screen, player):
        """
        Render mass counter + evolution bar.

        Parameters:
            screen – the pygame Surface to draw onto
            player – the Player instance; we read player.mass and player.tier
        """
        self._draw_mass_text(screen, player.mass)
        self._draw_progress_bar(screen, player.mass, player.tier)
        self._draw_tier_name(screen, player.tier)


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _draw_mass_text(self, screen, mass):
        """
        Render 'Mass: <value>' in white with a 1-pixel black shadow 
        for readability against any background.
        """
        text = f"Mass: {int(mass)}"

        # Shadow (drawn first, underneath)
        shadow_surf = self.font.render(text, True, BLACK)
        screen.blit(shadow_surf, (HUD_X + 1, MASS_Y + 1))

        # Main text
        text_surf = self.font.render(text, True, WHITE)
        screen.blit(text_surf, (HUD_X, MASS_Y))

    def _draw_progress_bar(self, screen, mass, tier):
        """
        Draw a bar that fills from 0 % to 100 % toward the next tier.

        How it works:
        1. Decide the current tier's floor and the next tier's threshold.
        2. Calculate progress = (mass - floor) / (threshold - floor),
           clamped to [0.0, 1.0] so it never overflows.
        3. Draw the background rectangle first, then overlay the filled
           portion scaled by progress.
        4. Draw a white border on top for definition.

        Tier logic (matches constants.py thresholds):
          Tier 1 → 0 .. TIER_2_MASS - 1   bar fills toward TIER_2_MASS
          Tier 2 → TIER_2_MASS .. TIER_3_MASS - 1
          Tier 3 → already maxed out; bar shows full
        """
        # ── Determine progress ────────────────────────────────────────
        if tier == 1:
            floor     = 0
            threshold = TIER_2_MASS
            label     = "→ Tier 2"
        elif tier == 2:
            floor     = TIER_2_MASS
            threshold = TIER_3_MASS
            label     = "→ Tier 3"
        else:
            # Tier 3 – maximum evolution, bar always full
            floor     = TIER_3_MASS
            threshold = TIER_3_MASS   # avoid division by zero below
            label     = "MAX"

        # Avoid divide-by-zero if floor == threshold (Tier 3 case)
        span = threshold - floor
        if span > 0:
            progress = max(0.0, min(1.0, (mass - floor) / span))
        else:
            progress = 1.0      # Tier 3: fully filled

        fill_w = int(BAR_W * progress)  # how many pixels to colour in

        # ── Draw background ───────────────────────────────────────────
        bg_rect = pygame.Rect(HUD_X, BAR_Y, BAR_W, BAR_H)
        pygame.draw.rect(screen, BAR_BG_COLOR, bg_rect, border_radius=4)

        # ── Draw filled portion ───────────────────────────────────────
        if fill_w > 0:
            fill_rect = pygame.Rect(HUD_X, BAR_Y, fill_w, BAR_H)
            pygame.draw.rect(screen, BAR_FILL_COLOR, fill_rect, border_radius=4)

        # ── Border ────────────────────────────────────────────────────
        pygame.draw.rect(screen, BAR_BORDER, bg_rect, width=1, border_radius=4)

        # ── Label to the right of the bar ────────────────────────────
        label_surf = pygame.font.SysFont("arial", 14).render(label, True, WHITE)
        screen.blit(label_surf, (HUD_X + BAR_W + 6, BAR_Y))

    def _draw_tier_name(self, screen, tier):
        """
        Draw the player's current form and threat status below the progress bar.

        Three fixed strings, one per tier:
          Tier 1  → "Larva"                          (neutral white)
          Tier 2  → "Small Fish — SHARK HUNTING YOU" (warning orange)
          Tier 3  → "Monster — HUNT THE SHARK"       (action green)
        """
        if tier == 1:
            text  = "Larva"
            color = WHITE
        elif tier == 2:
            text  = "Small Fish  —  SHARK HUNTING YOU"
            color = (255, 160, 40)   # warm orange — danger signal
        else:
            text  = "Monster  —  HUNT THE SHARK"
            color = (80, 255, 140)   # bright green — action signal

        small_font  = pygame.font.SysFont("arial", 14, bold=True)
        # Shadow
        shadow_surf = small_font.render(text, True, BLACK)
        screen.blit(shadow_surf, (HUD_X + 1, TIER_NAME_Y + 1))
        # Main text
        name_surf = small_font.render(text, True, color)
        screen.blit(name_surf, (HUD_X, TIER_NAME_Y))
