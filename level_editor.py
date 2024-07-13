import pygame
import button
import csv
import os
import pickle

pygame.init()

clock = pygame.time.Clock()
FPS = 60

# game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode(
    (SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN)
)
pygame.display.set_caption("Level Editor")


# define game variables
ROWS = 16
MAX_COLS = 20
TILE_SIZE = SCREEN_HEIGHT // ROWS

level = 0
current_tile = 1

# store tiles in a list
img_list = []
directory = "img/tile"
for filename in sorted(os.listdir(directory)):
    full_filename = os.path.join(directory, filename)
    _, ext = os.path.splitext(filename)
    if ext == ".png":
        img = pygame.image.load(full_filename).convert_alpha()
        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
        img_list.append(img)

save_img = pygame.image.load("img/save_btn.png").convert_alpha()
load_img = pygame.image.load("img/load_btn.png").convert_alpha()


# define colours
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

# define font
font = pygame.font.SysFont("Verdana", 15)

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [0] * MAX_COLS
    world_data.append(r)


# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# create function for drawing background
def draw_bg():
    screen.fill(GREEN)
    for y, row in enumerate(world_data):
        for x, _ in enumerate(row):
            screen.blit(img_list[0], (x * TILE_SIZE, y * TILE_SIZE))


# draw grid
def draw_grid():
    # vertical lines
    for c in range(MAX_COLS + 2):
        pygame.draw.line(
            screen,
            WHITE,
            (c * TILE_SIZE, 0),
            (c * TILE_SIZE, SCREEN_HEIGHT),
        )
    pygame.draw.line(
        screen,
        WHITE,
        (20 * TILE_SIZE - 1, 0),
        (20 * TILE_SIZE - 1, SCREEN_HEIGHT),
    )
    # horizontal lines
    for c in range(ROWS + 1):
        pygame.draw.line(
            screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE)
        )


# function for drawing the world tiles
def draw_world():
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile > 0:
                screen.blit(img_list[tile], (x * TILE_SIZE, y * TILE_SIZE))


# create buttons
save_button = button.Button(
    SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1
)
load_button = button.Button(
    SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1
)
# make a button list
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
    tile_button = button.Button(
        SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1
    )
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0


run = True
show_saved = 0
while run:
    clock.tick(FPS)

    draw_bg()
    draw_world()
    draw_grid()

    draw_text(f"Level: {level}", font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
    draw_text(
        "Press UP or DOWN to change level",
        font,
        WHITE,
        10,
        SCREEN_HEIGHT + LOWER_MARGIN - 60,
    )

    # save and load data
    if save_button.draw(screen):
        # save level data
        with open(f"level{level}_data.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            for row in world_data:
                writer.writerow(row)
            show_saved = 30
    if load_button.draw(screen):
        # load in level data
        with open(f"level{level}_data.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][y] = int(tile)

    if show_saved > 0:
        draw_text("SAVED", font, WHITE, 416, SCREEN_HEIGHT + LOWER_MARGIN - 90)
        show_saved -= 1

    # draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

    # choose a tile
    button_count = 0
    for button_count, i in enumerate(button_list):
        if i.draw(screen):
            current_tile = button_count

    # highlight the selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    # add new tiles to the screen
    # get mouse position
    pos = pygame.mouse.get_pos()
    x = (pos[0]) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    # check that the coordinates are within the tile area
    if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
        # update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1

    pygame.display.update()

pygame.quit()
