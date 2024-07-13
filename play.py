import pygame
import csv
import os

pygame.init()

clock = pygame.time.Clock()
FPS = 60

# Game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Playable Level')

# Define game variables
ROWS = 16
MAX_COLS = 20
TILE_SIZE = SCREEN_HEIGHT // ROWS

HEALTH_BOX_TILE = 2

health = 0
health_box_value = 1
total_health_boxes = 0
collected_health_boxes = 0

img_list = []
directory = "img/tile"
for filename in sorted(os.listdir(directory)):
    full_filename = os.path.join(directory, filename)
    _, ext = os.path.splitext(filename)
    if ext == ".png":
        img = pygame.image.load(full_filename).convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)

# Define colors
WHITE = (255, 255, 255)
GREEN = (144, 201, 120)
BLACK = (0, 0, 0)

# Define font
font = pygame.font.SysFont('Verdana', 20)

# Load level data from CSV and count total health boxes
def load_level_data(filename):
    global total_health_boxes
    world_data = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            row_data = [int(tile) for tile in row]
            world_data.append(row_data)
            total_health_boxes += row_data.count(HEALTH_BOX_TILE)
    return world_data

# Draw background
def draw_bg():
    screen.fill(GREEN)
    for y, row in enumerate(world_data):
        for x, _ in enumerate(row):
            screen.blit(img_list[0], (x * TILE_SIZE, y * TILE_SIZE))

# Draw the world
def draw_world(world_data):
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if x * TILE_SIZE < SCREEN_WIDTH:
                if tile >= 0:
                    screen.blit(img_list[tile], (x * TILE_SIZE, y * TILE_SIZE))

# Display health count
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Define player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE - 4, TILE_SIZE - 4))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 3

    def update(self, world_data):
        global health, collected_health_boxes
        self.vel_x, self.vel_y = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        if keys[pygame.K_UP]:
            self.vel_y = -self.speed
        if keys[pygame.K_DOWN]:
            self.vel_y = self.speed

        # Check boundaries
        new_x = self.rect.x + self.vel_x
        new_y = self.rect.y + self.vel_y
        if new_x < 0:
            new_x = 0
        if new_x + self.rect.width > SCREEN_WIDTH:
            new_x = SCREEN_WIDTH - self.rect.width
        if new_y < 0:
            new_y = 0
        if new_y + self.rect.height > SCREEN_HEIGHT:
            new_y = SCREEN_HEIGHT - self.rect.height

        # Collision detection
        if not self.check_collision(new_x, self.rect.y, world_data):
            self.rect.x = new_x
        if not self.check_collision(self.rect.x, new_y, world_data):
            self.rect.y = new_y

        # Check for health kit collection
        self.collect_health_kit(world_data)

    def check_collision(self, x, y, world_data):
        for row_idx, row in enumerate(world_data):
            for col_idx, tile in enumerate(row):
                if tile > 0 and tile != HEALTH_BOX_TILE:
                    tile_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    player_rect = pygame.Rect(x, y, self.rect.width, self.rect.height)
                    if tile_rect.colliderect(player_rect):
                        return True
        return False

    def collect_health_kit(self, world_data):
        global health, collected_health_boxes
        for row_idx, row in enumerate(world_data):
            for col_idx, tile in enumerate(row):
                if tile == HEALTH_BOX_TILE:  # Health kit tile
                    tile_rect = pygame.Rect(col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(tile_rect):
                        world_data[row_idx][col_idx] = -1  # Remove the health kit from the world
                        health += health_box_value  # Increase health
                        collected_health_boxes += 1  # Increment collected health boxes

# Initialize game objects
world_data = load_level_data('level0_data.csv')
player = Player(TILE_SIZE * 2, TILE_SIZE * 2)
player_group = pygame.sprite.Group()
player_group.add(player)

# Game loop
run = True
win = False
while run:
    clock.tick(FPS)

    draw_bg()
    if not win:
        player_group.update(world_data)
    draw_world(world_data)
    player_group.draw(screen)

    draw_text(f'Health: {health}', font, WHITE, 10, 10)

    if collected_health_boxes >= total_health_boxes:
        win = True

    if win:
        draw_text('You Win!', font, WHITE, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
