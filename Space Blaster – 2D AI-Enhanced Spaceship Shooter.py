import pygame
import os
import random
import math

# --- INITIALIZATION ---
pygame.font.init()
pygame.mixer.init()

# --- CONSTANTS ---
# Screen Dimensions
WIDTH, HEIGHT = 900, 500

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
HEALTH_BAR_RED = (200, 0, 0)
HEALTH_BAR_GREEN = (0, 200, 0)
HEALTH_POWERUP_COLOR = (60, 180, 255) # Light Blue
MULTI_SHOT_POWERUP_COLOR = (255, 105, 180) # Pink

# Game Window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship Fighter!")

# Center Border
BORDER = pygame.Rect(WIDTH // 2 - 5, 0, 10, HEIGHT)

# Fonts
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)
MENU_FONT = pygame.font.SysFont('comicsans', 60)
INSTRUCTION_FONT = pygame.font.SysFont('comicsans', 30)
BUTTON_FONT = pygame.font.SysFont('comicsans', 50)
UI_FONT = pygame.font.SysFont('comicsans', 24)

# Game Settings
FPS = 60
VEL = 5  # Player spaceship velocity
BULLET_VEL = 7
MAX_BULLETS = 5 # Increased max bullets to accommodate multi-shot
PLAYER_BULLET_COOLDOWN = 500 # Milliseconds between player shots
MULTI_SHOT_DURATION = 5000 # 5 seconds
POWERUP_LIFESPAN = 5000 # 5 seconds for a power-up to exist

# --- AI Difficulty Settings ---
DIFFICULTY = "EASY" # Options: "EASY", "HARD"
if DIFFICULTY == "HARD":
    AI_VEL = 4.5
    AI_SHOOT_COOLDOWN = 600 # AI shoots faster
else: # EASY
    AI_VEL = 3
    AI_SHOOT_COOLDOWN = 1000 # AI shoots slower

# Spaceship Dimensions
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

# --- ASSET LOADING ---
# NOTE: Create an 'Assets' folder in the same directory as your script.
# Add your images and sounds there.

# Custom Events
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Sound Effects
try:
    BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Grenade+1.mp3'))
    BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Gun+Silencer.mp3'))
    POWERUP_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Powerup.wav')) # Add a sound for power-ups
    # Load background music - UPDATED to use theme.mp3
    pygame.mixer.music.load(os.path.join('Assets', 'theme.mp3'))
    pygame.mixer.music.set_volume(0.4) # Set volume to 40%
except pygame.error as e:
    print(f"Warning: Could not load sound files. Error: {e}")
    BULLET_HIT_SOUND = None
    BULLET_FIRE_SOUND = None
    POWERUP_SOUND = None


# Images
try:
    YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_yellow.png'))
    YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

    RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets', 'spaceship_red.png'))
    RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

    # List of possible backgrounds
    SPACE_BACKGROUNDS = [
        pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.png')), (WIDTH, HEIGHT)),
        pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space2.webp')), (WIDTH, HEIGHT))
    ]
    # Randomly select a background for the session
    CURRENT_BACKGROUND = random.choice(SPACE_BACKGROUNDS)

except pygame.error as e:
    print(f"Fatal Error: Could not load image files. Please ensure they are in the 'Assets' folder. Error: {e}")
    pygame.quit()
    exit()


# --- DRAW FUNCTIONS ---

def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health, powerups, yellow_multishot_timer, red_multishot_timer):
    """Draws all game elements to the window."""
    WIN.blit(CURRENT_BACKGROUND, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    # Health Bars
    pygame.draw.rect(WIN, HEALTH_BAR_RED, (WIDTH - 210, 10, 200, 30))
    pygame.draw.rect(WIN, HEALTH_BAR_GREEN, (WIDTH - 210, 10, red_health * 20, 30))
    pygame.draw.rect(WIN, HEALTH_BAR_RED, (10, 10, 200, 30))
    pygame.draw.rect(WIN, HEALTH_BAR_GREEN, (10, 10, yellow_health * 20, 30))

    # Health & Ammo Text
    red_health_text = HEALTH_FONT.render(f"Health: {red_health}", 1, WHITE)
    yellow_health_text = HEALTH_FONT.render(f"Health: {yellow_health}", 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 15, 45))
    WIN.blit(yellow_health_text, (15, 45))

    yellow_ammo_text = UI_FONT.render(f"Bullets: {len(yellow_bullets)}/{MAX_BULLETS}", 1, WHITE)
    red_ammo_text = UI_FONT.render(f"Bullets: {len(red_bullets)}/{MAX_BULLETS}", 1, WHITE)
    WIN.blit(yellow_ammo_text, (15, 85))
    WIN.blit(red_ammo_text, (WIDTH - red_ammo_text.get_width() - 15, 85))

    # Draw Spaceships
    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))
    
    # Draw Power-up Timers
    if yellow_multishot_timer > 0:
        timer_text = UI_FONT.render(f"Multi-Shot: {yellow_multishot_timer}", 1, MULTI_SHOT_POWERUP_COLOR)
        WIN.blit(timer_text, (yellow.x, yellow.y - 20))
    if red_multishot_timer > 0:
        timer_text = UI_FONT.render(f"Multi-Shot: {red_multishot_timer}", 1, MULTI_SHOT_POWERUP_COLOR)
        WIN.blit(timer_text, (red.x, red.y - 20))


    # Draw Power-ups as capsules
    for powerup_rect, powerup_type, _ in powerups: # _ ignores the spawn time
        color = HEALTH_POWERUP_COLOR if powerup_type == "HEALTH" else MULTI_SHOT_POWERUP_COLOR
        pygame.draw.rect(WIN, color, powerup_rect, border_radius=10)

    # Draw Bullets
    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()

def draw_winner(text):
    """Displays the winner text and waits before proceeding."""
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH / 2 - draw_text.get_width() / 2, HEIGHT / 2 - draw_text.get_height() / 2))
    pygame.display.update()
    pygame.time.delay(5000)

def draw_menu():
    """Draws the main menu screen with selectable game modes."""
    WIN.blit(CURRENT_BACKGROUND, (0, 0))
    title_text = MENU_FONT.render("Spaceship Fighter", 1, WHITE)
    WIN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 50))

    # Define buttons
    vs_ai_button = pygame.Rect(WIDTH/2 - 150, 200, 300, 60)
    vs_player_button = pygame.Rect(WIDTH/2 - 150, 300, 300, 60)

    # Draw buttons
    pygame.draw.rect(WIN, (0, 100, 200), vs_ai_button, border_radius=10)
    pygame.draw.rect(WIN, (200, 100, 0), vs_player_button, border_radius=10)

    # Draw button text
    ai_text = BUTTON_FONT.render("Play vs. AI", 1, WHITE)
    player_text = BUTTON_FONT.render("Play vs. Player", 1, WHITE)
    WIN.blit(ai_text, (vs_ai_button.x + (vs_ai_button.width - ai_text.get_width()) / 2, vs_ai_button.y + 5))
    WIN.blit(player_text, (vs_player_button.x + (vs_player_button.width - player_text.get_width()) / 2, vs_player_button.y + 5))
    
    pause_control = INSTRUCTION_FONT.render("P = Pause | ESC = Return to Menu", 1, WHITE)
    WIN.blit(pause_control, (WIDTH/2 - pause_control.get_width()/2, 420))

    pygame.display.update()
    return vs_ai_button, vs_player_button


def draw_pause_screen():
    """Draws the pause overlay."""
    pause_text = WINNER_FONT.render("PAUSED", 1, WHITE)
    WIN.blit(pause_text, (WIDTH/2 - pause_text.get_width()/2, HEIGHT/2 - pause_text.get_height()/2))
    pygame.display.update()


# --- GAME LOGIC FUNCTIONS ---

def handle_yellow_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:  # LEFT
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:  # RIGHT
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:  # UP
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:  # DOWN
        yellow.y += VEL

def handle_red_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:  # LEFT
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.width < WIDTH:  # RIGHT
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0:  # UP
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height < HEIGHT - 15:  # DOWN
        red.y += VEL

def handle_red_ai_movement(red, yellow, powerups):
    """Controls the red spaceship with smarter AI to prioritize power-ups."""
    target_y = yellow.centery
    target_x = None  # Default: no horizontal target

    # Find the closest power-up on the AI's side
    closest_powerup = None
    min_dist = float('inf')
    for p_rect, p_type, p_time in powerups:
        if p_rect.centerx > BORDER.centerx:
            dist = ((red.centerx - p_rect.centerx)**2 + (red.centery - p_rect.centery)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest_powerup = p_rect
    
    # If a power-up is found, make it the primary target
    if closest_powerup:
        target_y = closest_powerup.centery
        target_x = closest_powerup.centerx

    # --- Execute Movement ---
    # Vertical movement
    if red.centery < target_y:
        red.y += AI_VEL
    elif red.centery > target_y:
        red.y -= AI_VEL

    # Horizontal movement
    if target_x:  # If there's a horizontal target (a power-up)
        if red.centerx < target_x:
            red.x += AI_VEL
        elif red.centerx > target_x:
            red.x -= AI_VEL
    else:  # If no power-up, do the slight random wiggle
        if random.randint(0, 100) > 98:
            move_dir = random.choice([-1, 1])
            red.x += (AI_VEL * move_dir)

    # Clamp position to stay within bounds
    if red.x < BORDER.x + BORDER.width:
        red.x = BORDER.x + BORDER.width
    if red.x + red.width > WIDTH:
        red.x = WIDTH - red.width
    if red.y < 0:
        red.y = 0
    if red.y + red.height > HEIGHT:
        red.y = HEIGHT - red.height


def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    # Iterate over a copy of the list to allow safe removal
    for bullet in yellow_bullets[:]:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            if bullet in yellow_bullets: yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            if bullet in yellow_bullets: yellow_bullets.remove(bullet)

    # Iterate over a copy of the list to allow safe removal
    for bullet in red_bullets[:]:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            if bullet in red_bullets: red_bullets.remove(bullet)
        elif bullet.x < 0:
            if bullet in red_bullets: red_bullets.remove(bullet)

def handle_powerups(powerups, yellow, red, yellow_health, red_health, yellow_multishot_end_time, red_multishot_end_time):
    """Checks for powerup collision and applies effects."""
    current_time = pygame.time.get_ticks()
    # Iterate over a copy of the list to allow safe removal
    for powerup_rect, powerup_type, spawn_time in powerups[:]:
        if yellow.colliderect(powerup_rect):
            if powerup_type == "HEALTH":
                yellow_health = min(10, yellow_health + 2)
            elif powerup_type == "MULTI_SHOT":
                yellow_multishot_end_time = current_time + MULTI_SHOT_DURATION
            if POWERUP_SOUND: POWERUP_SOUND.play()
            powerups.remove((powerup_rect, powerup_type, spawn_time))
        elif red.colliderect(powerup_rect):
            if powerup_type == "HEALTH":
                red_health = min(10, red_health + 2)
            elif powerup_type == "MULTI_SHOT":
                red_multishot_end_time = current_time + MULTI_SHOT_DURATION
            if POWERUP_SOUND: POWERUP_SOUND.play()
            powerups.remove((powerup_rect, powerup_type, spawn_time))
            
    return yellow_health, red_health, yellow_multishot_end_time, red_multishot_end_time


# --- GAME STATE MANAGEMENT ---

def start_new_game():
    """Initializes all variables for a new game session."""
    game_vars = {
        "red": pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT),
        "yellow": pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT),
        "red_bullets": [],
        "yellow_bullets": [],
        "red_health": 10,
        "yellow_health": 10,
        "last_yellow_shot": 0,
        "last_red_shot": 0,
        "powerups": [],
        "last_powerup_spawn_time": pygame.time.get_ticks(),
        "yellow_multishot_end_time": 0,
        "red_multishot_end_time": 0
    }
    return game_vars

# --- MAIN GAME LOOP ---

def main():
    """Main function to run the game, including menus and restart logic."""
    if pygame.mixer.get_init():
        pygame.mixer.music.play(-1)

    clock = pygame.time.Clock()
    game_state = "MENU" # Can be "MENU", "PLAYING", "PAUSED"
    game_mode = "AI" # Default game mode
    game_vars = {} # Dictionary to hold all game-specific variables
    run = True
    while run:
        if game_state == "MENU":
            vs_ai_button, vs_player_button = draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mode_selected = None
                    if vs_ai_button.collidepoint(event.pos):
                        mode_selected = "AI"
                    elif vs_player_button.collidepoint(event.pos):
                        mode_selected = "PVP"
                    
                    if mode_selected:
                        game_mode = mode_selected
                        game_vars = start_new_game() # Initialize game variables
                        game_state = "PLAYING"

        elif game_state == "PAUSED":
            draw_pause_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    game_state = "PLAYING" # Unpause

        elif game_state == "PLAYING":
            current_time = pygame.time.get_ticks()

            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    
                if event.type == pygame.KEYDOWN:
                    # Pause Game
                    if event.key == pygame.K_p:
                        game_state = "PAUSED"
                        continue
                    # Return to Menu
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"
                        continue

                    # Player 1 (Yellow) Firing
                    can_fire_multi = current_time < game_vars["yellow_multishot_end_time"]
                    bullets_to_fire = 3 if can_fire_multi else 1
                    if event.key == pygame.K_LCTRL and len(game_vars["yellow_bullets"]) <= MAX_BULLETS - bullets_to_fire:
                        if current_time - game_vars["last_yellow_shot"] > PLAYER_BULLET_COOLDOWN:
                            game_vars["last_yellow_shot"] = current_time
                            if can_fire_multi: # Multi-shot active
                                game_vars["yellow_bullets"].append(pygame.Rect(game_vars["yellow"].x + game_vars["yellow"].width, game_vars["yellow"].y + game_vars["yellow"].height // 2 - 2 - 10, 10, 5))
                                game_vars["yellow_bullets"].append(pygame.Rect(game_vars["yellow"].x + game_vars["yellow"].width, game_vars["yellow"].y + game_vars["yellow"].height // 2 - 2, 10, 5))
                                game_vars["yellow_bullets"].append(pygame.Rect(game_vars["yellow"].x + game_vars["yellow"].width, game_vars["yellow"].y + game_vars["yellow"].height // 2 - 2 + 10, 10, 5))
                            else: # Normal shot
                                game_vars["yellow_bullets"].append(pygame.Rect(game_vars["yellow"].x + game_vars["yellow"].width, game_vars["yellow"].y + game_vars["yellow"].height // 2 - 2, 10, 5))
                            if BULLET_FIRE_SOUND: BULLET_FIRE_SOUND.play()

                    # Player 2 (Red) Firing - ONLY in PVP mode
                    if game_mode == "PVP":
                        can_fire_multi_red = current_time < game_vars["red_multishot_end_time"]
                        bullets_to_fire_red = 3 if can_fire_multi_red else 1
                        if event.key == pygame.K_RCTRL and len(game_vars["red_bullets"]) <= MAX_BULLETS - bullets_to_fire_red:
                            if current_time - game_vars["last_red_shot"] > PLAYER_BULLET_COOLDOWN:
                                game_vars["last_red_shot"] = current_time
                                if can_fire_multi_red: # Multi-shot active
                                    game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2 - 10, 10, 5))
                                    game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2, 10, 5))
                                    game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2 + 10, 10, 5))
                                else: # Normal shot
                                    game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2, 10, 5))
                                if BULLET_FIRE_SOUND: BULLET_FIRE_SOUND.play()

                # Health Handling from custom events
                if event.type == RED_HIT:
                    game_vars["red_health"] -= 1
                    if BULLET_HIT_SOUND: BULLET_HIT_SOUND.play()
                if event.type == YELLOW_HIT:
                    game_vars["yellow_health"] -= 1
                    if BULLET_HIT_SOUND: BULLET_HIT_SOUND.play()

            # AI Shooting Logic - ONLY in AI mode
            if game_mode == "AI":
                can_fire_multi_ai = current_time < game_vars["red_multishot_end_time"]
                bullets_to_fire_ai = 3 if can_fire_multi_ai else 1
                if current_time - game_vars["last_red_shot"] > AI_SHOOT_COOLDOWN and len(game_vars["red_bullets"]) <= MAX_BULLETS - bullets_to_fire_ai:
                    if abs((game_vars["red"].y + game_vars["red"].height//2) - (game_vars["yellow"].y + game_vars["yellow"].height//2)) < 50:
                        game_vars["last_red_shot"] = current_time
                        if can_fire_multi_ai: # Multi-shot active
                           game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2 - 10, 10, 5))
                           game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2, 10, 5))
                           game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2 + 10, 10, 5))
                        else: # Normal shot
                           game_vars["red_bullets"].append(pygame.Rect(game_vars["red"].x, game_vars["red"].y + game_vars["red"].height // 2 - 2, 10, 5))
                        if BULLET_FIRE_SOUND: BULLET_FIRE_SOUND.play()

            # Check for Winner
            if game_vars: # Ensure game has started
                winner_text = ""
                if game_vars["red_health"] <= 0:
                    winner_text = "Yellow Wins!"
                if game_vars["yellow_health"] <= 0:
                    winner_text = "Red Wins!" if game_mode == "PVP" else "Computer Wins!"

                if winner_text != "":
                    draw_winner(winner_text)
                    game_state = "MENU" # Go back to menu after a win
                    continue

            # Power-up Timeout Logic
            if game_vars:
                game_vars["powerups"] = [(r, t, s) for r, t, s in game_vars["powerups"] if current_time - s <= POWERUP_LIFESPAN]


            # Power-up Spawning Logic
            if game_vars and len(game_vars["powerups"]) < 2 and current_time - game_vars["last_powerup_spawn_time"] > random.randint(8000, 15000):
                game_vars["last_powerup_spawn_time"] = current_time
                
                spawn_side = random.choice(["LEFT", "RIGHT"])
                powerup_type = random.choices(["HEALTH", "MULTI_SHOT"], weights=[3, 1], k=1)[0]
                
                # Spawn attempt with collision avoidance
                tries = 0
                while True:
                    if spawn_side == "LEFT":
                        powerup_x = random.randint(50, BORDER.left - 50)
                    else: # spawn_side == "RIGHT"
                        powerup_x = random.randint(BORDER.right + 50, WIDTH - 50)
                    
                    powerup_y = random.randint(50, HEIGHT - 50)
                    powerup_rect = pygame.Rect(powerup_x, powerup_y, 20, 20)
                    
                    # Avoid spawning on ships
                    if not powerup_rect.colliderect(game_vars["yellow"]) and not powerup_rect.colliderect(game_vars["red"]):
                        game_vars["powerups"].append((powerup_rect, powerup_type, current_time))
                        break
                    
                    tries += 1
                    if tries > 20:  # Fallback to prevent infinite loop
                        break


            # Handle Movement and Game Logic
            if game_vars:
                keys_pressed = pygame.key.get_pressed()
                handle_yellow_movement(keys_pressed, game_vars["yellow"])
                
                if game_mode == "AI":
                    handle_red_ai_movement(game_vars["red"], game_vars["yellow"], game_vars["powerups"])
                else: # PVP mode
                    handle_red_movement(keys_pressed, game_vars["red"])

                handle_bullets(game_vars["yellow_bullets"], game_vars["red_bullets"], game_vars["yellow"], game_vars["red"])
                (game_vars["yellow_health"], game_vars["red_health"], 
                 game_vars["yellow_multishot_end_time"], game_vars["red_multishot_end_time"]) = handle_powerups(
                    game_vars["powerups"], game_vars["yellow"], game_vars["red"], 
                    game_vars["yellow_health"], game_vars["red_health"], 
                    game_vars["yellow_multishot_end_time"], game_vars["red_multishot_end_time"])

                # Calculate remaining time for UI
                yellow_timer = 0
                if current_time < game_vars["yellow_multishot_end_time"]:
                    yellow_timer = math.ceil((game_vars["yellow_multishot_end_time"] - current_time) / 1000)
                
                red_timer = 0
                if current_time < game_vars["red_multishot_end_time"]:
                    red_timer = math.ceil((game_vars["red_multishot_end_time"] - current_time) / 1000)

                # Create a dictionary with only the arguments needed for drawing
                draw_args = {
                    "red": game_vars["red"],
                    "yellow": game_vars["yellow"],
                    "red_bullets": game_vars["red_bullets"],
                    "yellow_bullets": game_vars["yellow_bullets"],
                    "red_health": game_vars["red_health"],
                    "yellow_health": game_vars["yellow_health"],
                    "powerups": game_vars["powerups"],
                    "yellow_multishot_timer": yellow_timer,
                    "red_multishot_timer": red_timer
                }
                # Draw all elements
                draw_window(**draw_args)
        
        # This part runs regardless of game state
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
