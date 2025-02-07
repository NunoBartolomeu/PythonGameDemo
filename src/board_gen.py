from typing import List
import random
from base_classes import Board, Player, Piece, TileType

BOARD_WIDTH = 100
BOARD_HEIGHT = 50
TARGET_FLOOR_PERCENTAGE = 0.35

def mine_board(board: Board):
    cx, cy = random.randint(0, board.height-1), random.randint(0, board.width-1)
    board.tiles[cx][cy].type = TileType.FLOOR
    floor_count = 1
    target_floor = int(board.height * board.width * TARGET_FLOOR_PERCENTAGE)

    while floor_count < target_floor:
        directions = board.get_neighbors(cx, cy)
        valid_wall_moves = []
        valid_floor_moves = []
        for nx, ny in directions:
            if board.tiles[nx][ny].type == TileType.WALL and board.can_break_wall(nx, ny):
                valid_wall_moves.append((nx, ny))
            elif board.tiles[nx][ny].type == TileType.FLOOR:
                valid_floor_moves.append((nx, ny))

        if valid_wall_moves:
            cx, cy = random.choice(valid_wall_moves)
            board.tiles[cx][cy].type = TileType.FLOOR
            floor_count += 1
        elif valid_floor_moves:
            cx, cy = random.choice(valid_floor_moves)


def set_void_tiles(board: Board):
    for x in range(board.height):
        for y in range(board.width):
            if board.tiles[x][y].type == TileType.WALL:
                neighbors = board.get_neighbors(x, y, include_diagonals=True)
                wall_count = sum(1 for nx, ny in neighbors if board.out_of_bounds(nx, ny) or board.tiles[nx][ny].type in {TileType.WALL, TileType.VOID})
                if wall_count == len(neighbors):
                    board.tiles[x][y].type = TileType.VOID

def wall_percentage(board: Board):
    wall_count = sum(sum(1 for tile in row if tile.type == TileType.WALL) for row in board.tiles)
    total_cells = board.width * board.height
    return wall_count / total_cells

def setSpawns(board: Board, num_spawns: int) -> List[tuple[int, int]]:
    potential_spawns = []
    
    for x in range(board.height):
        for y in range(board.width):
            if board.get_tile(x, y).type == TileType.FLOOR:
                neighbors = board.get_neighbors(x, y)
                floor_neighbors = sum(1 for nx, ny in neighbors if board.get_tile(nx, ny).type == TileType.FLOOR)
                
                if floor_neighbors == 3:
                    potential_spawns.append((x, y))

    random.shuffle(potential_spawns)
    conv_spawns = potential_spawns[:num_spawns]

    for x, y in conv_spawns:
        board.get_tile(x, y).type = TileType.SPAWN
    
    return conv_spawns

def spawnStartingPieces(board: Board, player: Player):
    x, y = player.spawn
    neighbors = board.get_neighbors(x, y)
    piece_number = 1
    for nx, ny in neighbors:
        if board.get_tile(nx, ny).type == TileType.FLOOR:
            board.get_tile(nx, ny).pieces.append(Piece(piece_number, (nx, ny), player, False))
            piece_number += 1
            if piece_number > 3:
                break

def generate_board(width=BOARD_WIDTH, height=BOARD_HEIGHT) -> Board:
    while True:
        board = Board(width, height, TileType.WALL)
        mine_board(board)
        set_void_tiles(board)
        if wall_percentage(board) > TARGET_FLOOR_PERCENTAGE:
            return board

def generate_game(player_names: List[str], width=BOARD_WIDTH, height=BOARD_HEIGHT):
    board = generate_board(width, height)
    spawns = setSpawns(board, len(player_names))

    players = []
    for i, player_name in enumerate(player_names):
        player = Player(player_name, board.width, board.height, spawns[i])
        spawnStartingPieces(board, player)
        players.append(player)
    return board, players
