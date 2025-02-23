from enum import Enum
from typing import List

class Player:
    def __init__(self, name: str, color: tuple[int, int, int], board_width: int, board_height: int, spawn: tuple[int, int]):
        self.name = name
        self.color = color
        self.board = Board(board_width, board_height, TileType.UNKNOWN)
        self.spawn = spawn
        self.pieces_exited = 0

class Piece:
    def __init__(self, number: int, position: tuple[int, int], owner: str, is_ghost: bool, color: tuple[int, int, int]):
        self.number = number
        self.owner = owner
        self.color = color
        self.position = position
        self.is_ghost = is_ghost

class TileType(Enum):
    UNKNOWN = "UNKNOWN"

    FOG_VOID = "FOG_VOID"
    FOG_WALL = "FOG_WALL"
    FOG_FLOOR = "FOG_FLOOR"
    
    VOID = "VOID"
    WALL = "WALL"
    FLOOR = "FLOOR"
    
    SPAWN = "SPAWN"
    EXIT = "EXIT"
    CHEST = "CHEST"
    TRAP = "TRAP"

    CLOSED_EXIT = "CLOSED_EXIT"

class Tile:
    def __init__(self, tile_type: TileType):
        self.type = tile_type
        self.pieces: List['Piece'] = []

    def is_floor(self) -> bool:
        return self.type in [TileType.FLOOR, TileType.FOG_FLOOR, TileType.SPAWN, TileType.EXIT, TileType.CHEST, TileType.TRAP, TileType.CLOSED_EXIT]
    
    def is_wall(self) -> bool:
        return self.type in [TileType.WALL, TileType.FOG_WALL]
    
    def is_clear(self) -> bool:
        return self.type not in [TileType.UNKNOWN, TileType.FOG_VOID, TileType.FOG_WALL, TileType.FOG_FLOOR]

    def break_wall(self):
        if self.type == TileType.WALL:
            self.type = TileType.FLOOR
        elif self.type == TileType.FOG_WALL:
            self.type = TileType.FOG_FLOOR

class Board:
    def __init__(self, width: int, height: int, base_tile_type: TileType):
        self.tiles: List[List[Tile]] = [[Tile(base_tile_type) for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        self.gameover = False
        
    def get_neighbors(self, x, y, include_diagonals=False):
        directions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]  # up, down, left, right
        if include_diagonals:
            directions += [(x-1, y-1), (x-1, y+1), (x+1, y-1), (x+1, y+1)]  # diagonals
        return [(nx, ny) for nx, ny in directions if 0 <= nx < self.height and 0 <= ny < self.width]

    def out_of_bounds(self, x, y):
        return x < 0 or x >= self.height or y < 0 or y >= self.width
    
    def can_break_wall(self, x, y):
        if x == 0 or x == self.height-1 or y == 0 or y == self.width-1:
            return False

        if x > 0 and y > 0 and self.get_tile(x-1, y).is_floor() and self.get_tile(x, y-1).is_floor() and self.get_tile(x-1, y-1).is_floor():
            return False
        if x > 0 and y < self.width-1 and self.get_tile(x-1, y).is_floor() and self.get_tile(x, y+1).is_floor() and self.get_tile(x-1, y+1).is_floor():
            return False
        if x < self.height-1 and y > 0 and self.get_tile(x+1, y).is_floor() and self.get_tile(x, y-1).is_floor() and self.get_tile(x+1, y-1).is_floor():
            return False
        if x < self.height-1 and y < self.width-1 and self.get_tile(x+1, y).is_floor() and self.get_tile(x, y+1).is_floor() and self.get_tile(x+1, y+1).is_floor():
            return False
        return True
    
    def get_tile(self, x, y)->Tile:
        return self.tiles[x][y]
    
    def get_pieces(self, player: Player, include_ghosts: bool) -> List[Piece]:
        pieces = []
        for x in range(self.height):
            for y in range(self.width):
                for piece in self.tiles[x][y].pieces:
                    if piece.owner == player.name and (include_ghosts or not piece.is_ghost):
                        pieces.append(piece)
        return pieces

    def get_piece(self, x, y):
        for piece in self.get_tile(x, y).pieces:
            if not piece.is_ghost:
                return piece
        return None
    
    def get_clear_vision(self):
        clear_tiles = set()
        for x in range(self.height):
            for y in range(self.width):
                if self.get_tile(x, y).is_clear():
                    clear_tiles.add((x, y))
        return clear_tiles

class PlayerTurn:
    def __init__(self, player_name):
        self.player_name = player_name
        self.pieces_actions = {}

    def add_move_action(self, piece, to):
        if piece.number not in self.pieces_actions:
            self.pieces_actions[piece.number] = []

        for action in reversed(self.pieces_actions[piece.number]):
            if action.type == ActionType.MOVE:
                if action.args[0] == to:
                    piece_actions = self.pieces_actions[piece.number]
                    self.pieces_actions[piece.number] = piece_actions[0: piece_actions.index(action)]
                    return
                else:
                    break

        self.pieces_actions[piece.number].append(Action(ActionType.MOVE, [piece.position, to]))

    def add_break_action(self, piece, wall_position):
        if piece.number not in self.pieces_actions:
            self.pieces_actions[piece.number] = []
        self.pieces_actions[piece.number].append(Action(ActionType.BREAK, [piece.position, wall_position]))

    def clear_actions(self):
        self.pieces_actions = {}

class Action:
    def __init__(self, action_type, args):
        self.type = action_type
        self.args = args

class ActionType(Enum):
    MOVE = "MOVE"
    BREAK = "BREAK_WALL"
