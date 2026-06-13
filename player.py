import pygame
import math
from constants import SCREEN_W, SCREEN_H, TIER_2_MASS, TIER_3_MASS, TIER_RADII

class Player:
    def __init__(self, x, y, mass=10, radius=20, speed=200):
        self.x = x
        self.y = y
        self.mass = mass
        # self.radius = radius --> overwritten by TIER_RADII[1]
        self.speed = speed

        # Tier and radius are derived from mass; set via the helper
        self.tier   = 1
        self.radius = TIER_RADII[1]

    # ------------------------------------------------------------------
    # Eating & mass increase
    # ------------------------------------------------------------------

    def eat(self, food):
        """
        Add food's mass to the player and update tier and radius.

        Steps:
            1. Increase self.mass by food.mass_value.
            2. Recalculate tier against TIER_2_MASS / TIER_3_MASS thresholds.
            3. If tier changed, update self.radius from TIER_RADII.
        """
        # 1 – gain mass
        self.mass += food.mass_value

        # 2 – recalculate tier
        if self.mass >= TIER_3_MASS:
            new_tier = 3
        elif self.mass >= TIER_2_MASS:
            new_tier = 2
        else:
            new_tier = 1

        # 3 – update radius if tier changed
        if new_tier != self.tier:
            self.tier   = new_tier
            self.radius = TIER_RADII[self.tier]

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def update(self, keys, dt):
        # Reset movement direction
        dx, dy = 0, 0

        # Handle keyboard input
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed

        # Normalize diagonal movement (optional)
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/sqrt(2)
            dy *= 0.7071

        # Update position
        self.x += dx * dt
        self.y += dy * dt

        # Boundary checks
        self.x = max(self.radius, min(self.x, SCREEN_W - self.radius))
        self.y = max(self.radius, min(self.y, SCREEN_H - self.radius))

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, screen, color):
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)