import random
from common.base_classes import Board, Player, TileType, Piece

def remove_piece(board: Board, piece: Piece):
    board.get_tile(piece.position[0], piece.position[1]).pieces.remove(piece)

def move_piece(board: Board, piece: Piece, x: int, y: int):
    if piece.is_ghost:
        return

    neighbors = board.get_neighbors(piece.position[0], piece.position[1])
    if (x, y) not in neighbors:
        return

    new_tile = board.get_tile(x, y)
    for p in new_tile.pieces:
        if p.owner == piece.owner and not p.is_ghost:
            return

    for p in new_tile.pieces:
        if p.owner == piece.owner and p.is_ghost and p.number == piece.number:
            p.is_ghost = False
            remove_piece(board, piece)
            return
    piece.is_ghost = True
    new_tile.pieces.append(Piece(piece.number, (x, y), piece.owner, False))

def break_wall(board: Board, piece: Piece, x: int, y: int):
    if not piece.is_ghost:
        return

    if not board.can_break_wall(x, y):
        return

    board.get_tile(x, y).type = TileType.FLOOR
    