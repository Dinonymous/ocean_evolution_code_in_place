import pygame # game engine library module
import random # random number module. Used to scatter zooplankton, random entries for fish and speed wobble for entities.
import math   # gives access to trigonometry functions needed for direction and distance calculations
from constants import ( SCREEN_W, SCREEN_H, 
                      ZP_RADIUS, ZP_MASS_VALUE, ZP_MAX_DRIFT, ZP_COLOR,
                      SF_RADIUS, SF_MASS_VALUE, SF_SPEED, SF_COLOR, 
                      SHARK_RADIUS, SHARK_MASS_VALUE, SHARK_SPEED, SHARK_COLOR, )


# ──────────────────────────────────────────────────────────────────────────────
# Zooplankton
# ──────────────────────────────────────────────────────────────────────────────

class Zooplankton:
    """
    A tiny food particle that drifts slowly around the screen.
    Safe to eat at any tier.
    Attributes:
        x, y        – current position (float for smooth sub-pixel drift)
        radius      – drawn size in pixels (4px, very small)
        mass_value  – how much mass the player gains on eating it
        color       – pale cyan so it reads against the dark ocean
        dx, dy      – current drift velocity (pixels per second)
        drift_timer – countdown until the next random direction change
    """

    RADIUS     = ZP_RADIUS     # size in px – a tiny dot
    MASS_VALUE = ZP_MASS_VALUE # mass added to player when eaten
    MAX_DRIFT  = ZP_MAX_DRIFT  # in px/s – gentle, almost imperceptible movement
    COLOR      = ZP_COLOR      # color of ZPs

    def __init__(self, x=None, y=None):
        # Place at a random screen position unless a specific spot is given. If x and/or y not rovided choose random value.
        self.x = x if x is not None else random.uniform(self.RADIUS, SCREEN_W - self.RADIUS) # random.uniform(a, b) returns a float
        self.y = y if y is not None else random.uniform(self.RADIUS, SCREEN_H - self.RADIUS) # both x and y are offset of edge by radius of ZP

        self.radius     = self.RADIUS
        self.mass_value = self.MASS_VALUE

        # Give each zooplankton its own random starting drift direction
        self._new_drift() # underscore prefix means that the method is only for internal use and not external callers. A convention. 

        # Seconds until the next direction change (0.5 – 2 s)
        self.drift_timer = random.uniform(0.5, 2.0) # random. otherwise all ZPs would change direction at the same time. 


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _new_drift(self):
        """
        Pick a fresh random velocity vector within MAX_DRIFT speed.
        Picking a random angle first and then multiplying by a single speed value 
        guarantees every drift is exactly the same pace regardless of direction.
        Otherwise, diagonal movement would be faster than axis-aligned movement.
        cos(angle) gives the horizontal component, 
        sin(angle) the vertical — standard polar-to-Cartesian conversion.
        """
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(5, self.MAX_DRIFT)
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, dt):
        """
        Move the zooplankton and occasionally change direction.
        dt – delta time in seconds (same value passed around the game loop)

        Step-by-step:
        1. Subtract elapsed time from the direction-change countdown.
        2. If the timer hits zero, pick a new random drift and reset.
        3. Move by velocity × dt  (same physics as the player).
        4. Bounce off screen edges so dots stay visible.
        """
        # 1 & 2 – random direction change
        self.drift_timer -= dt # delta time — the number of seconds since the last frame.
        if self.drift_timer <= 0:
            self._new_drift()
            self.drift_timer = random.uniform(0.5, 2.0) # when it runs out, a new random direction is chosen

        # 3 – move
        # multiplying velocity by dt ensures that ZPs travel the same px whatever frame rate game runs at.
        self.x += self.dx * dt
        self.y += self.dy * dt

        # 4 – bounce off edges (flip velocity component on hit)
        if self.x < self.radius:
            self.x = self.radius
            self.dx = abs(self.dx)          # force rightward
        elif self.x > SCREEN_W - self.radius:
            self.x = SCREEN_W - self.radius
            self.dx = -abs(self.dx)         # force leftward
        # abs() function in Python returns the absolute value of a number - in case a direction change happened at some frame
        if self.y < self.radius:
            self.y = self.radius
            self.dy = abs(self.dy)          # force downward
        elif self.y > SCREEN_H - self.radius:
            self.y = SCREEN_H - self.radius
            self.dy = -abs(self.dy)         # force upward

    def draw(self, screen):
        """
        Draw the zooplankton as a small filled circle.
        int is used because coordinates must be whole numbers, 
        and self.x and y (positions) is stored as float to ensure smooth movement
        """
        pygame.draw.circle(screen, self.COLOR, (int(self.x), int(self.y)), self.radius)


# ──────────────────────────────────────────────────────────────────────────────
# SmallFish
# ──────────────────────────────────────────────────────────────────────────────

class SmallFish:
    """
    A small NPC fish that swims in a straight line across the screen.

    Behaviour
    ---------
    • Spawns just OUTSIDE one of the four screen edges, aimed loosely
      toward the opposite side — like a real fish passing through.
    • Swims at a constant speed in that direction, with a small random
      vertical or horizontal wobble to look natural.
    • Once it drifts far enough off the opposite edge it is considered
      'done' and the Spawner will replace it.  There is NO bouncing;
      this is the open ocean, not a fish tank.

    Danger logic (read by game.py, not enforced here)
    --------------------------------------------------
    • At Tier 1 the player is tiny — every SmallFish is a threat.
    • At Tier 2+ the player is bigger than a SmallFish, so the fish
      becomes prey instead.  That switch is handled in game.py.

    Attributes
    ----------
    x, y        – position (float)
    radius      – drawn size in pixels
    mass_value  – mass the player gains when eating this fish
    dx, dy      – velocity vector (pixels/second)
    done        – True once the fish has left the far edge; signals
                  the Spawner to remove and replace it
    """

    RADIUS     = SF_RADIUS
    MASS_VALUE = SF_MASS_VALUE
    SPEED      = SF_SPEED
    COLOR      = SF_COLOR

    # How many pixels past the opposite edge before we mark done=True
    _OFF_SCREEN_MARGIN = 20 # so it doesn't flick off as soon as it touches the edge

    def __init__(self): 
        self.radius     = self.RADIUS
        self.mass_value = self.MASS_VALUE
        self.done       = False # when true it singnals it needs to be replaced

        # Pick a random entry edge and set position + velocity
        self._spawn_from_edge()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _spawn_from_edge(self):
        """
        Place the fish just outside a random edge and give it a velocity
        that takes it across the screen toward the opposite side.

        The perpendicular component (wobble) is at most 20 % of the main
        speed so the fish still clearly crosses the screen but doesn't
        travel in a perfectly rigid straight line.
        """
        edge = random.choice(("left", "right", "top", "bottom"))

        # Main travel speed; wobble adds a slight diagonal movement
        main  = self.SPEED
        wobble = random.uniform(-main * 0.2, main * 0.2)

        if edge == "left":
            self.x  = -self.radius # so it swims in from 'beyond' and doesn't seem to 'pop-in'. 
            self.y  = random.uniform(0, SCREEN_H)
            self.dx =  main      # travels rightward
            self.dy =  wobble

        elif edge == "right":
            self.x  = SCREEN_W + self.radius
            self.y  = random.uniform(0, SCREEN_H)
            self.dx = -main      # travels leftward
            self.dy =  wobble

        elif edge == "top":
            self.x  = random.uniform(0, SCREEN_W)
            self.y  = -self.radius
            self.dx =  wobble
            self.dy =  main      # travels downward

        else:  # bottom
            self.x  = random.uniform(0, SCREEN_W)
            self.y  = SCREEN_H + self.radius
            self.dx =  wobble
            self.dy = -main      # travels upward

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def update(self, dt):
        """
        Advance position and check whether the fish has left the screen.

        Once x/y is far enough past the opposite edge, self.done is set
        to True.  The Spawner polls this flag each frame and replaces
        the fish when it fires.
        """
        self.x += self.dx * dt
        self.y += self.dy * dt

        m = self._OFF_SCREEN_MARGIN # abriviation to make the lover code more readable
        if (self.x < -m or self.x > SCREEN_W + m or
                self.y < -m or self.y > SCREEN_H + m):
            self.done = True

    def draw(self, screen):
        """
        Draw the fish as a filled circle with a small triangular tail
        so it reads as a fish and not just another dot.

        The tail triangle is built from three points relative to the
        fish's current position and travel direction (angle of dx/dy).
        """
        cx, cy = int(self.x), int(self.y)

        # Body
        pygame.draw.circle(screen, self.COLOR, (cx, cy), self.radius)

        # Tail — a small triangle pointing AWAY from the travel direction
        angle = math.atan2(self.dy, self.dx)          # direction of travel
        '''
        math.atan2(dy, dx) converts a velocity vector into an angle in radians. 
        It's the inverse of what _new_drift does. 
        argument order: atan2(y, x) — y comes first, IMPORTANT (cause of bug if not y first)
        '''
        tail_angle = angle + math.pi                  # opposite = tail side

        tail_len  = self.radius * 1.4
        wing_dist = self.radius * 0.7
        wing_spread = math.pi / 4                     # 45° spread for the wings

        tip = (
            cx + tail_len * math.cos(tail_angle),
            cy + tail_len * math.sin(tail_angle),
        )
        wing_a = (
            cx + wing_dist * math.cos(tail_angle - wing_spread),
            cy + wing_dist * math.sin(tail_angle - wing_spread),
        )
        wing_b = (
            cx + wing_dist * math.cos(tail_angle + wing_spread),
            cy + wing_dist * math.sin(tail_angle + wing_spread),
        )

        pygame.draw.polygon(screen, self.COLOR, [tip, wing_a, wing_b])


# ──────────────────────────────────────────────────────────────────────────────
# Shark
# ──────────────────────────────────────────────────────────────────────────────

class Shark:

    RADIUS             = SHARK_RADIUS
    MASS_VALUE         = SHARK_MASS_VALUE
    SPEED              = SHARK_SPEED
    COLOR              = SHARK_COLOR
    _OFF_SCREEN_MARGIN = 20

    def __init__(self):
        self.radius     = self.RADIUS
        self.mass_value = self.MASS_VALUE
        self.speed      = self.SPEED
        self.chasing    = True   # True at Tier 2 (hunts player); False at Tier 3 (crosses screen)
        self.done       = False
        self.dx         = 0 # used for Tier 3
        self.dy         = 0 # used for Tier 3
        self._spawn_from_edge()


    def _spawn_from_edge(self):
        """Place the shark just outside a random edge, aimed across the screen."""
        edge = random.choice(("left", "right", "top", "bottom"))
        main   = self.SPEED
        wobble = random.uniform(-main * 0.2, main * 0.2)

        if edge == "left":
            self.x  = -self.radius
            self.y  = random.uniform(0, SCREEN_H)
            self.dx =  main
            self.dy =  wobble
        elif edge == "right":
            self.x  = SCREEN_W + self.radius
            self.y  = random.uniform(0, SCREEN_H)
            self.dx = -main
            self.dy =  wobble
        elif edge == "top":
            self.x  = random.uniform(0, SCREEN_W)
            self.y  = -self.radius
            self.dx =  wobble
            self.dy =  main
        else:  # bottom
            self.x  = random.uniform(0, SCREEN_W)
            self.y  = SCREEN_H + self.radius
            self.dx =  wobble
            self.dy = -main


    def update(self, dt, player=None):
        if self.chasing and player is not None:
            dx = player.x - self.x # vector pointing at player
            dy = player.y - self.y
            dist = math.hypot(dx, dy) # computes the distance between the two points
            if dist > 0: # if dist = 0, division would cause a ZeroDivisionError
                self.x += (dx / dist) * self.speed * dt # Without normalisation, the shark would move faster when far away and slower when close.
                # normalisation (dx / dist, dy / dist) is a standard way to make any object move toward a target at a consistent speed
                self.y += (dy / dist) * self.speed * dt 
        else:
            # Tier 3: straight-line crossing (like SmallFish)
            self.x += self.dx * dt
            self.y += self.dy * dt
            m = self._OFF_SCREEN_MARGIN
            if self.x < -m or self.x > SCREEN_W + m or \
                self.y < -m or self.y > SCREEN_H + m:
                self.done = True


    def draw(self, screen):
        """Draw the shark as a grey circle with a triangular dorsal fin on top."""
        cx, cy = int(self.x), int(self.y)

        # Body
        pygame.draw.circle(screen, self.COLOR, (cx, cy), self.radius)

        # Dorsal fin — triangle pointing upward from the centre
        fin_tip    = (cx,                     cy - self.radius - 10)
        fin_left   = (cx - self.radius // 2,  cy - self.radius // 2)
        fin_right  = (cx + self.radius // 2,  cy - self.radius // 2)
        pygame.draw.polygon(screen, self.COLOR, [fin_tip, fin_left, fin_right])