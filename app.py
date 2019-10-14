import random
import pygame
import sys
from pprint import pprint

screen_width = 320
screen_height = 780
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.init()
font = pygame.font.SysFont("comicsansms", 30)

# SOUNDS
touch_sound = pygame.mixer.Sound("touch.wav")
clear_line_sound = pygame.mixer.Sound("clear_line.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")


# images
background = pygame.image.load('urss.jpg')
block_size = 30

# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
game_rect = {'x': 10, 'y': 150, 'width': 300, 'height': 600}


def convert_shape_format(shape):
    positions = []
    for y, row in enumerate(shape):
        for x, col in enumerate(row):
            if shape[y][x] == "0":
                positions.append((x, y))
    return positions


class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.rotation = 0
        self.color = shape_colors[shapes.index(self.shape)]

    @staticmethod
    def create(grid):
        shape = random.choice(shapes)
        return Piece((grid.width // 2) - 2, -4, shape)

    def rotate(self):
        self.rotation += 1

    def move(self, direction):
        coef = {"left": -1, "right": 1}
        self.x += coef[direction]

    def get_shape(self, rotation=0):
        return self.shape[(self.rotation + rotation) % len(self.shape)]

    def get_shape_positions(self, rotation=0):
        '''
            rotation {0: current shape, 1: next, -1: previous}
            return [(1, 3), (1, 4), ...]
        '''
        shape = self.get_shape(rotation)
        local_positions = convert_shape_format(shape)
        # remove empty column and row
        return local_positions

    def get_global_shape_positions(self,  coords=(0, 0), rotation=0):
        local_positions = self.get_shape_positions(rotation)
        global_positions = []
        for position in local_positions:
            global_positions.append(
                (position[0] + self.x + coords[0], position[1] + self.y + coords[1]))
        return global_positions


class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.initialize()

    def initialize(self):
        self.grid = [[(0, 0, 0) for _ in range(self.width)]
                     for _ in range(self.height)]

    def add(self, x, y, color):
        self.grid[x][y] = color

    def add_piece(self, piece):
        positions = piece.get_shape_positions()
        for position in positions:
            if position[1] + piece.y >= 0 and position[0] + piece.x >= 0:
                self.grid[position[1] + piece.y][position[0] +
                                                 piece.x] = piece.color

    def draw_lines(self, surface):
        for i in range(screen_height // block_size):
            # draw horizontal lines
            pygame.draw.line(surface, (125, 125, 125), (game_rect['x'], (
                block_size * i) + game_rect['y']), (game_rect['x'] + game_rect['width'], (block_size * i) + game_rect['y']))
            # draw vertical lines
        for j in range(screen_height // block_size):
            pygame.draw.line(surface, (125, 125, 125), ((block_size * j) + game_rect['x'], game_rect['y']), ((
                block_size * j) + game_rect['x'], game_rect['height'] + game_rect['y']))

    def draw_content(self, surface):
        BORDER = 1
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                color = self.grid[i][j]
                border_color = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.rect(surface, border_color, ((
                    j * block_size) + game_rect['x'], (i * block_size) + game_rect['y'], block_size, block_size))
                pygame.draw.rect(surface, color, (j * block_size + game_rect['x'] + BORDER, i * block_size +
                                                  game_rect['y'] + BORDER, (block_size - BORDER * 2), (block_size - BORDER * 2)))


def get_piece():
    shape = random.choice(shapes)
    return Piece(3, 0, shape)


def colide(positions, other):
    for position in positions:
        if position in other:
            return True
    return False


def isOutside(positions):
    for position in positions:
        if(position[0] > 9 or position[0] < 0 or position[1] > 19):
            return True
    return False


def count_by_row(keys):  # [(1,0), (1,1)..,]
    count_y = {}  # {12: 2, 13: 5,... }
    for key in keys:
        if not (key[1] in count_y):
            count_y[key[1]] = 1
        else:
            count_y[key[1]] += 1
    return count_y


def clean_blocks(blocks):

    keys = list(blocks.keys())  # [(1,2), (3,2),..]
    lines = count_by_row(keys)  # {10:2, 12:10, ...}
    lines_removed = []
    for line, count in lines.items():
        if count >= 10:
            lines_removed.append(line)
            list_blocks_to_remove = [(x, line) for x in range(10)]
            for block_to_remove in list_blocks_to_remove:
                blocks.pop(block_to_remove)
    if len(lines_removed) > 0:
        clear_line_sound.play()

        lines_to_move = {}
        for line_removed in lines_removed:
            for line, count in lines.items():
                if line < line_removed:
                    if line in lines_to_move:
                        lines_to_move[line] += 1
                    else:
                        lines_to_move[line] = 1

        if len(lines_to_move) > 0:
            new_blocks = {}
            max_line_number = 0
            for line, count in lines_to_move.items():
                if line > max_line_number:
                    max_line_number = line
                for block in blocks:
                    if block[1] == line:
                        new_blocks[(block[0], block[1] + count)
                                   ] = blocks[block]
            for block in blocks:
                if block[1] > max_line_number:
                    new_blocks[block] = blocks[block]
            return new_blocks
    return blocks


# INIT

grid = Grid(10, 20)
current_piece = Piece.create(grid)
next_piece = Piece.create(grid)
blocks = {}  # [(1,2): (255, 0, 0), ...]
clock = pygame.time.Clock()

FALL_SPEED = 500
time_elapsed = pygame.time.get_ticks()
fall_event = pygame.USEREVENT + 1
pygame.time.set_timer(fall_event, FALL_SPEED - (time_elapsed // 10000) * 10)
score = "0"
gameover = False

run = True
while run:
    current_positions = current_piece.get_global_shape_positions()
    next_positions = current_piece.get_global_shape_positions((0, 1))

    if gameover == True:
        game_over_sound.play()
        text = font.render("Game Over", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_x = screen.get_width() / 2 - text_rect.width / 2
        text_y = screen.get_height() / 2 - text_rect.height / 2
        screen.blit(text, [text_x, text_y])
        pygame.display.update()

        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    else:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            else:
                if event.type == fall_event:

                    if isOutside(next_positions) or colide(next_positions, blocks):
                        touch_sound.play()
                        for position in current_positions:
                            if position[1] < 0:
                                gameover = True
                            blocks[position] = current_piece.color
                        current_piece = next_piece
                        next_piece = Piece.create(grid)

                        ########### blocks operation here ##############
                        if len(blocks) > 0:
                            blocks = clean_blocks(blocks)
                    else:
                        current_piece.y += 1

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        next_positions = current_piece.get_global_shape_positions(
                            (-1, 0))
                        if not (colide(next_positions, blocks) or isOutside(next_positions)):
                            current_piece.move('left')
                    if event.key == pygame.K_RIGHT:
                        next_positions = current_piece.get_global_shape_positions(
                            (1, 0))
                        if not (colide(next_positions, blocks) or isOutside(next_positions)):
                            current_piece.move('right')
                    if event.key == pygame.K_DOWN:
                        next_positions = current_piece.get_global_shape_positions(
                            (0, 1))
                        if not (colide(next_positions, blocks) or isOutside(next_positions)):
                            current_piece.y += 1
                    if event.key == pygame.K_UP:
                        next_positions = current_piece.get_global_shape_positions(
                            (0, 0), 1)
                        if not (colide(next_positions, blocks) or isOutside(next_positions)):
                            current_piece.rotate()
                    if event.key == pygame.K_SPACE:
                        run = False

        # backgound
        screen.fill([200, 0, 0])
        screen.blit(background, (0, 0, screen_width, screen_height))

        # recreate the grid from scratch
        grid.initialize()

        grid.add_piece(current_piece)
        for key, value in blocks.items():
            grid.grid[key[1]][key[0]] = value

        grid.draw_lines(screen)
        grid.draw_content(screen)

        # draw next piece
        next_piece_position = (250, 20)
        for position in next_piece.get_shape_positions():
            pprint(position)
            pygame.draw.rect(screen, next_piece.color, (next_piece_position[0] + (
                15 * position[0]), next_piece_position[1] + (15 * position[1]), 15, 15))

        text = font.render(score, True, (0, 0, 0))
        screen.blit(text, ((screen_width // 2) - (text.get_width() // 2), 10))
    pygame.display.update()


'''
blocks
current_piece
    current_position
    next_position






EVENT current_piece fall
    current_piece.fall()
    if next_position.hit(blocks)
        blocks.add(current_piece.current_position)
EVENT current_piece rotate
    if Not next_position.hit(blocks) or next_position.isOutside()
        current_piece.rotate()

update screen
'''