from enum import Enum
from typing import Optional
import pygame
import sys

sys.path.append("../")
from common.base_classes import Board, Player, Piece, TileType

################################# Drawing Configuration #############################

BOARD_WIDTH = 100
BOARD_HEIGHT = 50

# Sizes
TILE_SIZE = 18
MAP_WIDTH = BOARD_WIDTH * TILE_SIZE
MAP_HEIGHT = BOARD_HEIGHT * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class TileColors(Enum):
    UNKNOWN = (0, 0, 0)

    FOG_VOID = (50, 50, 50)
    FOG_WALL = (100, 100, 100)
    FOG_FLOOR = (150, 150, 150)
    
    VOID = (50, 50, 50)
    WALL = (255, 165, 0)
    FLOOR = (255, 255, 255)
    
    SPAWN = (0, 255, 0)
    EXIT = (0, 0, 255)
    CHEST = (255, 0, 0)
    TRAP = (255, 0, 0)

class PieceColors(Enum):
    ALLY_PIECE = (255, 0, 0)
    ALLY_GHOST_PIECE = (255, 180, 180)
    ENEMY_PIECE = (0, 0, 255)
    ENEMY_GHOST_PIECE = (180, 180, 255)
    MOVE_DOT = (0, 0, 0)

BACKGROUND_COLOR = (100, 100, 100)

def draw_board(screen, board: Board, player: Player):
    for x in range(board.height):
        for y in range(board.width):
            tile = board.tiles[x][y]
            color = TileColors[tile.type.name].value
            pygame.draw.rect(screen, color, (y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE))

            for piece in tile.pieces:
                piece_color = None
                if piece.is_ghost:
                    piece_color = PieceColors.ALLY_GHOST_PIECE.value if piece.owner == player else PieceColors.ENEMY_GHOST_PIECE.value
                else:
                    piece_color = PieceColors.ALLY_PIECE.value if piece.owner == player else PieceColors.ENEMY_PIECE.value 
                center = (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2)
                pygame.draw.circle(screen, piece_color, center, TILE_SIZE // 3)

selected_piece = None

def draw_possible_moves(screen, board: Board, piece: Piece):
    possible_moves = board.get_neighbors(piece.position[0], piece.position[1])
    for x, y in possible_moves:
        tile = board.tiles[x][y]
        if tile.is_floor() and not any(p for p in tile.pieces if not p.is_ghost):
            center = (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(screen, PieceColors.MOVE_DOT.value, center, TILE_SIZE // 6)

def handle_click(board: Board, x: int, y: int, selected_piece: Optional[Piece]):
    clicked_tile = board.tiles[x][y]
    
    for piece in clicked_tile.pieces:
        if not piece.is_ghost:
            return piece
            
    if selected_piece:
        possible_moves = board.get_neighbors(selected_piece.position[0], selected_piece.position[1])
        if (x, y) in possible_moves and board.tiles[x][y].is_floor():
            #move_piece(board, selected_piece, x, y)
            #update_player_board(selected_piece.owner, board)
            return None

################################# Pages #############################

# Draw text
def draw_text(screen, text, x, y, color=WHITE):
    width, height = screen.get_size()
    font = pygame.font.Font(None, height // 20)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Draw welcome page
def draw_welcome_page(screen, input_text, rgb, selected_channel):
    screen.fill(BLACK)
    width, height = screen.get_size()
    draw_text(screen, "Welcome to Castle Run Demo", width // 4, height // 10)
    draw_text(screen, "Write your name:", width // 4, height // 4)
    
    # Name input box
    pygame.draw.rect(screen, WHITE, (width // 2, height // 4, width // 4, height // 20), 2)
    draw_text(screen, input_text, width // 2 + 10, height // 4)
    
    # RGB Color selection
    draw_text(screen, "Choose your color:", width // 4, height // 3)
    for i, color in enumerate(["R", "G", "B"]):
        color_pos = (width // 3, height // 3 + (i + 1) * height // 15)
        draw_text(screen, color, *color_pos)
        draw_text(screen, str(rgb[i]), color_pos[0] + width // 10, color_pos[1])
        if i == selected_channel:
            pygame.draw.rect(screen, WHITE, (color_pos[0] - 10, color_pos[1] - 10, 100, 40), 2)
    
    # Color preview
    pygame.draw.rect(screen, (rgb[0], rgb[1], rgb[2]), (width // 2, height // 3, width // 10, height // 10))
    
    draw_text(screen, "Press ENTER to confirm", width // 4, height - height // 10)

# Draw waiting page
def draw_waiting_page(screen, players, num_players):
    screen.fill(BLACK)
    width, height = screen.get_size()
    draw_text(screen, "Awaiting Game Creation", width // 4, height // 10)
    draw_text(screen, f"Players connected: {len(players)}/{num_players}", width // 4, height // 5)
    
    y_offset = height // 4
    for player in players:
        draw_text(screen, f"-> {player.name}", width // 4, y_offset)
        pygame.draw.rect(screen, player.color, (width // 2, y_offset, width // 20, height // 20))
        y_offset += height // 15
