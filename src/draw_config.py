from enum import Enum
from typing import Optional
import pygame

from base_classes import Board, Player, Piece, TileType
from turn_logic import update_player_board, move_piece
from board_gen import BOARD_WIDTH, BOARD_HEIGHT

################################# Drawing Configuration #############################

# Sizes
TILE_SIZE = 18
MAP_WIDTH = BOARD_WIDTH * TILE_SIZE
MAP_HEIGHT = BOARD_HEIGHT * TILE_SIZE

# Colors
class TileColors(Enum):
    UNKNOW = (0, 0, 0)

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
            move_piece(board, selected_piece, x, y)
            update_player_board(selected_piece.owner, board)
            return None

