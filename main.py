"""
main.py — entry point for Ocean Evolution.
Run this file to start the game: python main.py
"""
import pygame
from constants import SCREEN_W, SCREEN_H
from gameloop import run_game


def main():
    pygame.init()                                           # start all pygame subsystems

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H)) # create the window
    pygame.display.set_caption("Ocean Evolution")

    run_game(screen)                                        # hand off to the game loop

    pygame.quit()                                           # clean shutdown when loop ends


main()