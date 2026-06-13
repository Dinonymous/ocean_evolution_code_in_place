"""
spawner.py – manages all entity populations on screen.

Responsibilities:
  • Seed the initial zooplankton and SmallFish populations at game start.
  • Replace eaten zooplankton after a short delay (respawn queue).
  • Replace SmallFish that swim off-screen immediately (no delay).
  • Activate and manage the Shark when the player reaches Tier 2.
"""

import random
from entities import Zooplankton, SmallFish, Shark
from constants import ( SCREEN_W, SCREEN_H, 
                        ZOOPLANKTON_COUNT, RESPAWN_DELAY,
                        SF_COUNT )

class Spawner:
    """
    Manages the live populations of all entities on screen.

    Attributes:
        zooplankton    – list[Zooplankton] currently alive on screen
        _respawn_queue – list[float]       countdown timers for zooplankton replacements
        fish           – list[SmallFish]   currently crossing the screen
        shark          – Shark or None     active when player is Tier 2+
    """

    def __init__(self):
        self.zooplankton   = []
        self._respawn_queue = []

        # SmallFish list — no respawn queue needed.
        # A new fish enters immediately when self.done flips True.
        self.fish = []
        self.shark = None   # None until player reaches Tier 2

        # Fill the screen immediately on game start
        self._seed()


    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _seed(self):
        """
        Create ZOOPLANKTON_COUNT particles spread across the whole screen,
        and SF_COUNT SmallFish entering from random edges.
        Called once when the Spawner is first constructed.
        """
        for _ in range(ZOOPLANKTON_COUNT):
            self.zooplankton.append(Zooplankton())

        for _ in range(SF_COUNT):
            self.fish.append(SmallFish())


    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self, dt, player=None):
        """
        Tick every live zooplankton and count down pending respawns.

        dt – delta time in seconds

        How the respawn queue works:
          Each slot in _respawn_queue starts at RESPAWN_DELAY.
          Every frame we subtract dt from every slot.
          When a slot reaches 0 we pop it and spawn one new Zooplankton,
          keeping the population stable without a sudden burst of dots.
        """
        # Update each living zooplankton's drift
        for zp in self.zooplankton:
            zp.update(dt)

        # Count down respawn timers
        still_waiting = []
        for timer in self._respawn_queue:
            timer -= dt
            if timer <= 0:
                # Timer expired → spawn a replacement at the screen edge
                self.zooplankton.append(self._spawn_at_random_edge())
            else:
                still_waiting.append(timer)
        self._respawn_queue = still_waiting

        # Update SmallFish — remove any that swam off-screen and 
        # immediately replace them so the population stays at SF_COUNT.
        # SmallFish do NOT use a delay queue. 
        # A new fish simply enters from a fresh random edge the moment the old one exits.
        still_swimming = []
        replacements_needed = 0
        for fish in self.fish:
            fish.update(dt)
            if fish.done:
                replacements_needed += 1
            else:
                still_swimming.append(fish)
        self.fish = still_swimming
        for _ in range(replacements_needed):
            self.fish.append(SmallFish())

        # ── Update shark if active ────────────────────────────────────
        if self.shark:
            self.shark.update(dt, player)
            '''
            If the shark is in crossing mode (Tier 3, chasing=False) and
            drifted off-screen, reposition it at a new random edge so the
            player always has a shark to hunt and the game can be won.
            '''
            if not self.shark.chasing and self.shark.done:
                self.shark.done = False
                self.shark._spawn_from_edge()

    # ------------------------------------------------------------------
    # Called by game.py when a zooplankton is eaten
    # ------------------------------------------------------------------

    def notify_eaten(self, zp):
        """
        Remove the eaten zooplankton from the live list and schedule
        a replacement to appear after RESPAWN_DELAY seconds.

        Parameters:
            zp – the Zooplankton instance that was just eaten
        """
        if zp in self.zooplankton:
            self.zooplankton.remove(zp)
        self._respawn_queue.append(RESPAWN_DELAY)


    def notify_fish_eaten(self, fish):
        """
        Remove a SmallFish that the player just ate.
        A replacement spawns immediately (no delay) from a fresh edge.

        Parameters:
            fish – the SmallFish instance that was just eaten
        """
        if fish in self.fish:
            self.fish.remove(fish)
        # Immediate replacement — the ocean always has fish in it
        self.fish.append(SmallFish())


    # ------------------------------------------------------------------
    # Called by game.py to manage the Shark
    # ------------------------------------------------------------------

    def activate_shark(self):
        """Called by game.py the frame player.tier becomes 2."""
        self.shark = Shark()

    def deactivate_shark_chase(self):
        """Called by game.py the frame player.tier becomes 3."""
        if self.shark:
            self.shark.chasing = False
            self.shark._spawn_from_edge()   # reposition at edge for crossing mode

    # ------------------------------------------------------------------
    # Draw pass
    # ------------------------------------------------------------------

    def draw(self, screen):
        """Render every live zooplankton. Called inside the draw phase."""
        for zp in self.zooplankton:
            zp.draw(screen)
        for fish in self.fish:
            fish.draw(screen)
        if self.shark:
            self.shark.draw(screen)


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _spawn_at_random_edge(self):
        """
        Spawn a replacement just inside the screen boundary.
        Appearing at an edge makes it feel like new food drifted in
        from off-screen rather than popping up in the middle of play.
        """
        edge = random.choice(["top", "bottom", "left", "right"])
        margin = 10     # px from the edge

        if edge == "top":
            x = random.uniform(margin, SCREEN_W - margin)
            y = margin
        elif edge == "bottom":
            x = random.uniform(margin, SCREEN_W - margin)
            y = SCREEN_H - margin
        elif edge == "left":
            x = margin
            y = random.uniform(margin, SCREEN_H - margin)
        else:   # right
            x = SCREEN_W - margin
            y = random.uniform(margin, SCREEN_H - margin)

        return Zooplankton(x=x, y=y)
