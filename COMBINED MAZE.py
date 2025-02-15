import pygame
import random
import heapq
import time

# Initialize Pygame and display system
pygame.init()
pygame.display.init()

# Constants
WIDTH, HEIGHT = 1500, 700  # Set a specific window size
BLOCK_SIZE = 40

# Colors
WHITE = (26, 26, 46, 1)
BLACK = (233, 69, 96, 1)
BLUE = (255, 255, 255)
GREEN = (249, 223, 177)
YELLOW = (255, 136, 0, 1)

# Directions for movement
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # Set windowed mode with specified size
pygame.display.set_caption("Moving Maze AI")
clock = pygame.time.Clock()

# Load and play background music in a loop
pygame.mixer.music.load("background_music.mp3")  # Load your music file
pygame.mixer.music.play(-1, 0.0)  # Loop the music indefinitely (-1 means infinite loops)

# Generate a solvable maze
def generate_maze(rows, cols):
    maze = [[1] * cols for _ in range(rows)]
    def carve(x, y):
        maze[y][x] = 0
        random.shuffle(DIRECTIONS)
        for dx, dy in DIRECTIONS:
            nx, ny = x + 2 * dx, y + 2 * dy
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve(nx, ny)
    carve(1, 1)
    return maze

# A* Pathfinding Algorithm
def astar(start, goal, maze):
    rows, cols = len(maze), len(maze[0])
    queue = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            break
        for dx, dy in DIRECTIONS:
            next_pos = (current[0] + dx, current[1] + dy)
            if 0 <= next_pos[0] < cols and 0 <= next_pos[1] < rows and maze[next_pos[1]][next_pos[0]] == 0:
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + abs(goal[0] - next_pos[0]) + abs(goal[1] - next_pos[1])
                    heapq.heappush(queue, (priority, next_pos))
                    came_from[next_pos] = current
    path = []
    current = goal
    while current in came_from and current is not None:
        path.append(current)
        current = came_from[current]
    return path[::-1] if path else []

# Convert maze coordinates to pixels
def to_pixels(x, y):
    return x * BLOCK_SIZE, y * BLOCK_SIZE

# Move black boxes (walls)
def move_walls(maze, rows, cols, player_pos, goal_pos):
    num_moves = 20  # Move 20 walls at once
    for _ in range(num_moves):
        x, y = random.randint(1, cols - 2), random.randint(1, rows - 2)
        if maze[y][x] == 1:  # Check if it's a wall
            dx, dy = random.choice(DIRECTIONS)
            new_x, new_y = x + dx, y + dy
            # Ensure within bounds and not blocking player/goal
            if 0 < new_x < cols - 1 and 0 < new_y < rows - 1:
                if (new_x, new_y) != player_pos and (new_x, new_y) != goal_pos and maze[new_y][new_x] == 0:
                    # Swap wall and empty space
                    maze[y][x], maze[new_y][new_x] = 0, 1
    return maze

# Choose game mode
def choose_mode():
    bg_image = pygame.image.load("background.jpg")  # Load your image
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))  # Scale to fit screen
    font = pygame.font.Font(None, 40)
    ai_text = font.render("Press A for AI Mode", True, (255, 215, 0))  # Change to yellow
    manual_text = font.render("Press M for Manual Mode", True, (255, 153, 51))  # Change to yellow
    while True:
        screen.blit(bg_image, (0, 0))  # Display background image
        screen.blit(ai_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        screen.blit(manual_text, (WIDTH // 2 - 100, HEIGHT // 2 + 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    return "AI"
                elif event.key == pygame.K_m:
                    return "Manual"

# Game variables
rows, cols = HEIGHT // BLOCK_SIZE, WIDTH // BLOCK_SIZE
maze = generate_maze(rows, cols)
player_pos = (1, 1)
goal_pos = (cols - 2, rows - 2)
ai_path = astar(player_pos, goal_pos, maze)
ai_index = 0

# Choose mode
game_mode = choose_mode()

# Main game loop
running = True
game_won = False
last_update_time = time.time()  # Keeps track of AI movement timing
while running:
    screen.fill(WHITE)
    # Move walls every few frames
    maze = move_walls(maze, rows, cols, player_pos, goal_pos)
    # Draw maze
    for y in range(rows):
        for x in range(cols):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (*to_pixels(x, y), BLOCK_SIZE, BLOCK_SIZE))
    # Draw goal (Green Square)
    pygame.draw.rect(screen, GREEN, (*to_pixels(goal_pos[0], goal_pos[1]), BLOCK_SIZE, BLOCK_SIZE))
    # Draw player (Blue Circle)
    pygame.draw.circle(screen, BLUE, (player_pos[0] * BLOCK_SIZE + BLOCK_SIZE // 2, player_pos[1] * BLOCK_SIZE + BLOCK_SIZE // 2), BLOCK_SIZE // 3)
    # Check win condition
    if player_pos == goal_pos:
        game_won = True
    if game_won:
        font = pygame.font.Font(None, 50)
        text = font.render("You Won!", True, BLUE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False
        continue
    # AI Mode (Faster AI)
    if game_mode == "AI":
        current_time = time.time()
        if current_time - last_update_time > 0.005 and ai_index < len(ai_path):  # AI moves every 0.1 seconds
            next_pos = ai_path[ai_index]
            if maze[next_pos[1]][next_pos[0]] == 0:  # Only move if not a wall
                player_pos = next_pos
                ai_index += 1
            if ai_index >= len(ai_path):  # Recalculate if stuck
                ai_path = astar(player_pos, goal_pos, maze)
                ai_index = 0
            last_update_time = current_time
    # Manual Mode (Now Works!)
    elif game_mode == "Manual":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
                if 0 <= new_x < cols and 0 <= new_y < rows and maze[new_y][new_x] == 0:
                    player_pos = (new_x, new_y)

    # Update display
    pygame.display.flip()
    clock.tick(30)  # 30 FPS for smoother movement

# Stop the music when the game ends
pygame.mixer.music.stop()
pygame.quit()
