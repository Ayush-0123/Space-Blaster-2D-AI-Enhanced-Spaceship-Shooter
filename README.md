#  Space Blaster – 2D AI-Enhanced Spaceship Shooter

Spaceship Fighter
A classic 2D multiplayer and single-player space shooter game built with Python and Pygame. Dodge, weave, and shoot your way to victory in this fast-paced arcade-style battle!

<!-- You can replace this with a real screenshot of your game -->

Features
Two Game Modes:

Player vs. Player: Grab a friend and battle it out on the same keyboard.

Player vs. AI: Test your skills against a computer-controlled opponent with multiple difficulty settings.

Dynamic Power-Ups: Turn the tide of battle by collecting randomly spawning power-ups:

Health Pack (Blue): Instantly restores 2 health points.

Multi-Shot (Pink): Temporarily allows you to fire a three-bullet spread.

Intelligent AI: The computer opponent actively tracks the player and hunts for power-ups on its side of the field.

Engaging Audio: Features background music and sound effects for hits, shots, and power-up collection.

Polished UI: Includes a main menu, pause screen, ammo counters, and active power-up timers.

Robust & Stable: Built with a clean game loop, state management, and error handling for a smooth experience.

How to Play
Requirements
To run this game, you will need:

Python 3.x

Pygame library

If you don't have Pygame installed, you can install it via pip:

pip install pygame

Setup
Clone or download this repository to your local machine.

Create a folder named Assets in the same directory as the Python script (space_fighters_game.py).

Place all the required game assets (images and sound files) inside the Assets folder.


Controls
The game is controlled using the keyboard:

Control

Player 1 (Yellow)

Player 2 (Red) / AI

Move Up

W

Up Arrow

Move Down

S

Down Arrow

Move Left

A

Left Arrow

Move Right

D

Right Arrow

Shoot

Left Ctrl

Right Ctrl

Pause Game

P (during match)

Return to Menu

ESC (during match)



Game Logic Overview
Game State: The game operates on a simple state machine (MENU, PLAYING, PAUSED) to manage different screens and logic.

Game Loop: All game logic, including event handling, movement, shooting, and drawing, is processed within a central game loop.

Reset Function: A start_new_game() function ensures that all variables (health, position, bullets, etc.) are cleanly reset every time a new match begins, preventing bugs between sessions.

Power-Ups: Power-ups spawn randomly on either side of the screen. They have a limited lifespan and will disappear if not collected in time. The AI is programmed to actively seek out and collect power-ups on its side.
