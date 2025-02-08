import json
import sys

sys.path.append("../")
from common.base_classes import Board, Piece, Tile

class PlayerInfoDTO():
    def __init__(self, name, color):
        self.name = name
        self.color = color
    
    

def piece_to_dict(piece: Piece):
    return {
        "number": piece.number,
        "position": piece.position,
        "owner": piece.owner,
        "is_ghost": piece.is_ghost,
        "color": piece.color
    }

def tile_to_dict(tile: Tile):
    return {
        "type": tile.type.value,  # Serialize the TileType enum to its string value
        "pieces": [piece_to_dict(piece) for piece in tile.pieces]  # Serialize pieces in this tile
    }

def board_to_dict(board: Board):
    return {
        "width": board.width,
        "height": board.height,
        "tiles": [[tile_to_dict(board.get_tile(x, y)) for y in range(board.width)] for x in range(board.height)]
    }

# This function can be used to send the board in JSON format
def board_to_json(board: Board):
    board_dict = board_to_dict(board)
    return json.dumps(board_dict)
