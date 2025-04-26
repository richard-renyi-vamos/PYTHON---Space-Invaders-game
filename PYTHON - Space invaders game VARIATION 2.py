import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# --- Screen Dimensions ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # Added yellow for explosion effects

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# --- Fonts ---
# Use a more modern font
font_name = 'Arial'  # Changed to Arial
title_font = pygame.font.SysFont(font_name, 36)
score_font = pygame.font.SysFont(font_name, 24)
game_over_font = pygame.font.SysFont(font_name, 64)
instruction_font = pygame.font.SysFont(font_name, 16) # Added instruction font

# --- Game Variables ---
player_size = 50
player_x = SCREEN_WIDTH // 2 - player_size // 2
player_y = SCREEN_HEIGHT - player_size - 20
player_speed = 5
bullet_size = 10
bullet_speed = 7
bullets = []
enemy_size = 30
num_enemies = 6
enemies = []
enemy_speed = 1
game_over = False
score = 0
lives = 3
wave = 1  # Added wave variable
explosion_frames = {}  # Dictionary to store explosion frames.  key is a tuple (x,y) and value is the frame number
MAX_EXPLOSION_FRAMES = 5 # Number of frames in explosion animation
game_active = False # Added game_active state

# --- Helper Functions ---

def draw_player(x, y):
    # Draw a spaceship-like player
    pygame.draw.polygon(screen, GREEN, [
        (x + player_size // 2, y),
        (x, y + player_size),
        (x + player_size, y + player_size)
    ])

def draw_bullet(x, y):
    pygame.draw.rect(screen, BLUE, (x, y, bullet_size, bullet_size))

def draw_enemy(x, y):
    # Draw a more distinct enemy shape
    pygame.draw.rect(screen, RED, (x, y, enemy_size, enemy_size))

def show_score():
    text = score_font.render("Score: " + str(score), True, WHITE)
    screen.blit(text, (10, 10))

def show_lives():
    text = score_font.render("Lives: " + str(lives), True, WHITE)
    screen.blit(text, (10, 40))

def show_game_over():
    text = game_over_font.render("Game Over", True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    screen.blit(text, text_rect)

def show_game_won(): # Added a win screen
    text = game_over_font.render("You Win!", True, YELLOW)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    screen.blit(text, text_rect)

def show_start_screen(): # Added start screen
    screen.fill(BLACK)
    title_text = title_font.render("Space Invaders", True, GREEN)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(title_text, title_rect)

    instruction_text_1 = instruction_font.render("Press SPACE to Start", True, WHITE)
    instruction_rect_1 = instruction_text_1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(instruction_text_1, instruction_rect_1)

    instruction_text_2 = instruction_font.render("Use LEFT/RIGHT arrows to move, SPACE to shoot", True, WHITE)
    instruction_rect_2 = instruction_text_2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(instruction_text_2, instruction_rect_2)

def generate_enemies():
    enemies.clear() # Clear existing enemies
    for i in range(num_enemies):
        enemy_x = random.randint(0, SCREEN_WIDTH - enemy_size)
        enemy_y = random.randint(50, 150)
        enemies.append([enemy_x, enemy_y])

def draw_explosion(x, y, frame_number):
    # Draw explosion animation frames
    explosion_colors = [YELLOW, RED, ORANGE, WHITE, (255, 165, 0)] # More colors
    if 0 <= frame_number < MAX_EXPLOSION_FRAMES:
        color = explosion_colors[frame_number % len(explosion_colors)] # Cycle through colors
        size = (MAX_EXPLOSION_FRAMES - frame_number) * 5  # Size decreases over time
        pygame.draw.circle(screen, color, (x, y), size)

# --- Event Handlers ---
def handle_input():
    keys = pygame.key.get_pressed()
    global player_x, player_speed, bullets, game_active

    if keys[pygame.K_SPACE]:
        if not game_active: # Start game on space bar
            game_active = True
            generate_enemies() # Generate enemies when game starts
            score = 0
            lives = 3
            player_x = SCREEN_WIDTH // 2 - player_size // 2 # Reset player position
        else:
            if len(bullets) < 3:  # Limit number of bullets on screen
                bullet_x = player_x + player_size // 2 - bullet_size // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_size:
        player_x += player_speed

def update_game():
    global bullets, enemies, enemy_speed, score, game_over, lives, wave, num_enemies, explosion_frames

    # Update bullets
    for i, bullet in enumerate(bullets):
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.pop(i)

    # Update enemies
    for i, enemy in enumerate(enemies):
        enemy[0] += enemy_speed
        if enemy[0] > SCREEN_WIDTH - enemy_size or enemy[0] < 0:
            enemy_speed *= -1
            enemy[1] += 10  # Move down slightly

        # Game over condition: enemy reaches player
        if enemy[1] > SCREEN_HEIGHT - enemy_size:
            game_over = True
            lives = 0 # set lives to 0

    # Check for collisions (bullets and enemies)
    for i, bullet in enumerate(bullets):
        for j, enemy in enumerate(enemies):
            if (
                bullet[0] < enemy[0] + enemy_size
                and bullet[0] + bullet_size > enemy[0]
                and bullet[1] < enemy[1] + enemy_size
                and bullet[1] + bullet_size > enemy[1]
            ):
                bullets.pop(i)
                enemies.pop(j)
                score += 10
                explosion_frames[(enemy[0], enemy[1])] = 0 # Add explosion at enemy position
                break  # Important: Break after handling collision

    # Update explosion frames
    for pos, frame_number in list(explosion_frames.items()): # Iterate over a copy of the dictionary
        explosion_frames[pos] += 1
        if explosion_frames[pos] >= MAX_EXPLOSION_FRAMES:
            del explosion_frames[pos] # Remove the explosion after it has finished

    # Check if all enemies are destroyed to advance wave (ADDED THIS)
    if not enemies:
        wave += 1
        num_enemies = min(num_enemies + 2, 15)  # Increase number of enemies, max 15
        generate_enemies()  # Generate the next wave of enemies
        enemy_speed *= 1.2  # Increase enemy speed slightly
        if wave > 5: # WIN CONDITION - After wave 5, the player wins.
            game_over = True # Set game over to true, and then check for win in the main loop
            lives = 0

    # Check for player death (lives)
    if lives <= 0:
        game_over = True

def draw_game():
    screen.fill(BLACK)
    draw_player(player_x, player_y)
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1])
    for enemy in enemies:
        draw_enemy(enemy[0], enemy[1])
    show_score()
    show_lives()
    for pos, frame_number in explosion_frames.items():
        draw_explosion(pos[0], pos[1], frame_number) #draw explosions
    if game_over:
        if lives <= 0:
            show_game_over()
        else:
            show_game_won()

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_active:
        show_start_screen()
    else:
        if not game_over:
            handle_input()
            update_game()
            draw_game()
        else:
            draw_game() # draw one last time.
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

