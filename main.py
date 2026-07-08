import pygame
import random

pygame.init()

CELL_SIZE = 30
COLS = 10
ROWS = 20
SIDE_PANEL = 220

WIDTH = COLS * CELL_SIZE + SIDE_PANEL
HEIGHT = ROWS * CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 20)

BLACK = (15, 15, 20)
GRID = (45, 45, 55)
WHITE = (240, 240, 240)
GRAY = (120, 120, 130)

COLORS = [
    (0, 240, 240),
    (240, 240, 0),
    (160, 0, 240),
    (0, 240, 0),
    (240, 0, 0),
    (0, 0, 240),
    (240, 160, 0),
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
]


class Piece:
    def __init__(self, index=None):
        self.index = random.randint(0, len(SHAPES) - 1) if index is None else index
        self.shape = [row[:] for row in SHAPES[self.index]]
        self.color = COLORS[self.index]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def reset_position(self):
        self.shape = [row[:] for row in SHAPES[self.index]]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0


def create_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def create_queue():
    return [Piece() for _ in range(3)]


def get_next_piece(queue):
    piece = queue.pop(0)
    queue.append(Piece())
    piece.reset_position()
    return piece


def valid_position(piece, board, offset_x=0, offset_y=0):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece.x + x + offset_x
                new_y = piece.y + y + offset_y

                if new_x < 0 or new_x >= COLS:
                    return False

                if new_y >= ROWS:
                    return False

                if new_y >= 0 and board[new_y][new_x] is not None:
                    return False

    return True


def lock_piece(piece, board):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                board[piece.y + y][piece.x + x] = piece.color


def clear_lines(board):
    new_board = []
    cleared = 0

    for row in board:
        if all(cell is not None for cell in row):
            cleared += 1
        else:
            new_board.append(row)

    while len(new_board) < ROWS:
        new_board.insert(0, [None for _ in range(COLS)])

    return new_board, cleared


def draw_board(board):
    screen.fill(BLACK)

    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID, rect, 1)

            if board[y][x] is not None:
                pygame.draw.rect(screen, board[y][x], rect.inflate(-2, -2))


def draw_piece(piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    (piece.x + x) * CELL_SIZE,
                    (piece.y + y) * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(screen, piece.color, rect.inflate(-2, -2))


def draw_small_piece(piece, start_x, start_y, block_size=18):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    start_x + x * block_size,
                    start_y + y * block_size,
                    block_size,
                    block_size
                )
                pygame.draw.rect(screen, piece.color, rect.inflate(-2, -2))


def draw_ui(score, level, lines, queue, hold_piece, game_over):
    panel_x = COLS * CELL_SIZE + 20

    screen.blit(small_font.render(f"Score: {score}", True, WHITE), (panel_x, 30))
    screen.blit(small_font.render(f"Level: {level}", True, WHITE), (panel_x, 60))
    screen.blit(small_font.render(f"Lines: {lines}", True, WHITE), (panel_x, 90))

    screen.blit(small_font.render("Hold C", True, WHITE), (panel_x, 135))
    if hold_piece is not None:
        draw_small_piece(hold_piece, panel_x + 15, 165)

    screen.blit(small_font.render("Next 3", True, WHITE), (panel_x, 240))
    for i, piece in enumerate(queue):
        draw_small_piece(piece, panel_x + 15, 270 + i * 65)

    controls = [
        "Left / Right: Move",
        "Down: Soft Drop",
        "Up: Rotate",
        "Space: Hard Drop",
        "C: Hold",
        "R: Restart"
    ]

    for i, text in enumerate(controls):
        screen.blit(small_font.render(text, True, GRAY), (panel_x, 465 + i * 22))

    if game_over:
        over_text = font.render("GAME OVER", True, WHITE)
        restart_text = small_font.render("Press R to restart", True, WHITE)

        screen.blit(over_text, (45, HEIGHT // 2 - 40))
        screen.blit(restart_text, (70, HEIGHT // 2))


def hard_drop(piece, board):
    while valid_position(piece, board, offset_y=1):
        piece.y += 1


def spawn_next_piece(queue):
    return get_next_piece(queue)


def hold_piece_func(current_piece, hold_piece, queue):
    if hold_piece is None:
        hold_piece = Piece(current_piece.index)
        current_piece = spawn_next_piece(queue)
    else:
        old_index = current_piece.index
        current_piece = Piece(hold_piece.index)
        hold_piece = Piece(old_index)

    current_piece.reset_position()
    hold_piece.reset_position()

    return current_piece, hold_piece


def calculate_speed(level):
    return max(80, 600 - (level - 1) * 75)


def reset_game():
    board = create_board()
    queue = create_queue()
    current_piece = spawn_next_piece(queue)
    hold_piece = None

    score = 0
    lines = 0
    level = 1
    fall_speed = calculate_speed(level)
    game_over = False
    can_hold = True

    return board, queue, current_piece, hold_piece, score, lines, level, fall_speed, game_over, can_hold


board, queue, current_piece, hold_piece, score, lines, level, fall_speed, game_over, can_hold = reset_game()

fall_time = 0
running = True

while running:
    dt = clock.tick(60)
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                board, queue, current_piece, hold_piece, score, lines, level, fall_speed, game_over, can_hold = reset_game()
                fall_time = 0
                continue

            if game_over:
                continue

            if event.key == pygame.K_LEFT:
                if valid_position(current_piece, board, offset_x=-1):
                    current_piece.x -= 1

            elif event.key == pygame.K_RIGHT:
                if valid_position(current_piece, board, offset_x=1):
                    current_piece.x += 1

            elif event.key == pygame.K_DOWN:
                if valid_position(current_piece, board, offset_y=1):
                    current_piece.y += 1
                    score += 1

            elif event.key == pygame.K_UP:
                old_shape = [row[:] for row in current_piece.shape]
                current_piece.rotate()

                if not valid_position(current_piece, board):
                    current_piece.shape = old_shape

            elif event.key == pygame.K_SPACE:
                hard_drop(current_piece, board)

                lock_piece(current_piece, board)
                board, cleared = clear_lines(board)

                if cleared > 0:
                    lines += cleared
                    score += cleared * cleared * 100
                    level = lines // 10 + 1
                    fall_speed = calculate_speed(level)

                current_piece = spawn_next_piece(queue)
                can_hold = True
                fall_time = 0

                if not valid_position(current_piece, board):
                    game_over = True

            elif event.key == pygame.K_c:
                if can_hold:
                    current_piece, hold_piece = hold_piece_func(current_piece, hold_piece, queue)
                    can_hold = False

                    if not valid_position(current_piece, board):
                        game_over = True

    if not game_over:
        if fall_time >= fall_speed:
            fall_time = 0

            if valid_position(current_piece, board, offset_y=1):
                current_piece.y += 1
            else:
                lock_piece(current_piece, board)
                board, cleared = clear_lines(board)

                if cleared > 0:
                    lines += cleared
                    score += cleared * cleared * 100
                    level = lines // 10 + 1
                    fall_speed = calculate_speed(level)

                current_piece = spawn_next_piece(queue)
                can_hold = True

                if not valid_position(current_piece, board):
                    game_over = True

    draw_board(board)

    if not game_over:
        draw_piece(current_piece)

    draw_ui(score, level, lines, queue, hold_piece, game_over)

    pygame.display.flip()

pygame.quit()