from enum import Enum
from typing import List, Optional
import pygame
import random

################################# Constants #################################

BOARD_WIDTH = 100
BOARD_HEIGHT = 50

################################# Classes #################################

class Player:
    def __init__(self, name: str, board_width: int, board_height: int, spawn: tuple[int, int]):
        self.name = name
        self.board = Board(board_width, board_height, TileType.UNKNOW)
        self.spawn = spawn

class Piece:
    def __init__(self, number: int, position: tuple[int, int], owner: 'Player', is_ghost: bool):
        self.owner = owner
        self.number = number
        self.position = position
        self.is_ghost = is_ghost

class TileType(Enum):
    UNKNOW = "UNKNOWN"

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

class Tile:
    def __init__(self, tile_type: TileType):
        self.type = tile_type
        self.pieces: List['Piece'] = []

    def isFloor(self) -> bool:
        return self.type in [TileType.FLOOR, TileType.FOG_FLOOR, TileType.SPAWN, TileType.EXIT, TileType.CHEST, TileType.TRAP]
    
    def isWall(self) -> bool:
        return self.type in [TileType.WALL, TileType.FOG_WALL]

    def breakWall(self):
        if self.type == TileType.WALL:
            self.type = TileType.FLOOR
        elif self.type == TileType.FOG_WALL:
            self.type = TileType.FOG_FLOOR

class Board:
    def __init__(self, width: int, height: int, base_tile_type: TileType):
        self.tiles: List[List[Tile]] = [[Tile(base_tile_type) for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        
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

        if x > 0 and y > 0 and self.getTile(x-1, y).isFloor() and self.getTile(x, y-1).isFloor() and self.getTile(x-1, y-1).isFloor():
            return False
        if x > 0 and y < self.width-1 and self.getTile(x-1, y).isFloor() and self.getTile(x, y+1).isFloor() and self.getTile(x-1, y+1).isFloor():
            return False
        if x < self.height-1 and y > 0 and self.getTile(x+1, y).isFloor() and self.getTile(x, y-1).isFloor() and self.getTile(x+1, y-1).isFloor():
            return False
        if x < self.height-1 and y < self.width-1 and self.getTile(x+1, y).isFloor() and self.getTile(x, y+1).isFloor() and self.getTile(x+1, y+1).isFloor():
            return False
        return True
    
    def getTile(self, x, y)->Tile:
        return self.tiles[x][y]
    
    def kill_piece(self, piece: Piece):
        self.getTile(piece.position[0], piece.position[1]).pieces.remove(piece)

    def move_piece(self, piece: Piece, x: int, y: int):
        if piece.is_ghost:
            print("Invalid move")
            return

        neighbors = self.get_neighbors(piece.position[0], piece.position[1])
        if (x, y) not in neighbors:
            print("Invalid move")
            return

        new_tile = self.getTile(x, y)
        for p in new_tile.pieces:
            if p.owner == piece.owner and not p.is_ghost:
                print("Invalid move")
                return

        for p in new_tile.pieces:
            if p.owner == piece.owner and p.is_ghost and p.number == piece.number:
                p.is_ghost = False
                self.kill_piece(piece)
                return
        piece.is_ghost = True
        new_tile.pieces.append(Piece(piece.number, (x, y), piece.owner, False))
    
    def getPieces(self, player: Player, include_ghosts: bool) -> List[Piece]:
        pieces = []
        for x in range(self.height):
            for y in range(self.width):
                for piece in self.tiles[x][y].pieces:
                    if piece.owner == player and (include_ghosts or not piece.is_ghost):
                        pieces.append(piece)
        return pieces

############################## Update Vision ##############################

def clear_vision(player: Player):
    for x in range(player.board.height):
        for y in range(player.board.width):
            if player.board.getTile(x, y).type == TileType.UNKNOW:
                continue
            if player.board.getTile(x, y).isFloor():
                player.board.getTile(x, y).type = TileType.FOG_FLOOR
            elif player.board.getTile(x, y).isWall():
                player.board.getTile(x, y).type = TileType.FOG_WALL
            else:
                player.board.getTile(x, y).type = TileType.FOG_VOID

def clear_pieces(player: Player):
    for x in range(player.board.height):
        for y in range(player.board.width):
            player.board.getTile(x, y).pieces = []

def update_player_board(player: Player, board: Board):
    pieces = board.getPieces(player, True)
    fog_tiles = set()
    clear_tiles = set()

    clear_vision(player)
    clear_pieces(player)

    for piece in pieces:
        px, py = piece.position
        player.board.getTile(px, py).pieces.append(piece)

        for x in range(px - 4, px + 5):
            for y in range(py - 4, py + 5):
                if board.out_of_bounds(x, y):
                    continue
                fog_tiles.add((x, y))
        for x in range(px - 2, px + 3):
            for y in range(py - 2, py + 3):
                if board.out_of_bounds(x, y):
                    continue
                clear_tiles.add((x, y))

    for x in range(board.height):
        for y in range(board.width):
            if (x, y) in clear_tiles:
                player.board.getTile(x, y).type = board.getTile(x, y).type
            elif (x, y) in fog_tiles:
                if board.getTile(x, y).isFloor():
                    player.board.getTile(x, y).type = TileType.FOG_FLOOR
                elif board.getTile(x, y).isWall():
                    player.board.getTile(x, y).type = TileType.FOG_WALL
                else:
                    player.board.getTile(x, y).type = TileType.FOG_VOID

def remove_ghost_pieces(board: Board):
    for x in range(board.height):
        for y in range(board.width):
            board.tiles[x][y].pieces = [p for p in board.tiles[x][y].pieces if not p.is_ghost]

############################## Board Generation ##############################

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
            if board.getTile(x, y).type == TileType.FLOOR:
                neighbors = board.get_neighbors(x, y)
                floor_neighbors = sum(1 for nx, ny in neighbors if board.getTile(nx, ny).type == TileType.FLOOR)
                
                if floor_neighbors == 3:
                    potential_spawns.append((x, y))

    random.shuffle(potential_spawns)
    conv_spawns = potential_spawns[:num_spawns]

    for x, y in conv_spawns:
        board.getTile(x, y).type = TileType.SPAWN
    
    return conv_spawns

def spawnStartingPieces(board: Board, player: Player):
    x, y = player.spawn
    neighbors = board.get_neighbors(x, y)
    piece_number = 1
    for nx, ny in neighbors:
        if board.getTile(nx, ny).type == TileType.FLOOR:
            board.getTile(nx, ny).pieces.append(Piece(piece_number, (nx, ny), player, False))
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

def generate_game(player_names: List[str]):
    board = generate_board()
    spawns = setSpawns(board, len(player_names))

    players = []
    for i, player_name in enumerate(player_names):
        player = Player(player_name, board.width, board.height, spawns[i])
        spawnStartingPieces(board, player)
        update_player_board(player, board)
        players.append(player)
    return board, players

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
    PIECE = (255, 0, 0)
    GHOST_PIECE = (255, 180, 180)
    MOVE_DOT = (0, 0, 0)

BACKGROUND_COLOR = (100, 100, 100)

def draw_board(screen, board: Board):
    for x in range(board.height):
        for y in range(board.width):
            tile = board.tiles[x][y]
            color = TileColors[tile.type.name].value
            pygame.draw.rect(screen, color, (y * TILE_SIZE, x * TILE_SIZE, TILE_SIZE, TILE_SIZE))

            for piece in tile.pieces:
                piece_color = PieceColors.GHOST_PIECE.value if piece.is_ghost else PieceColors.PIECE.value
                center = (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2)
                pygame.draw.circle(screen, piece_color, center, TILE_SIZE // 3)

selected_piece = None

def draw_possible_moves(screen, board: Board, piece: Piece):
    possible_moves = board.get_neighbors(piece.position[0], piece.position[1])
    for x, y in possible_moves:
        tile = board.tiles[x][y]
        if tile.isFloor() and not any(p for p in tile.pieces if not p.is_ghost):
            center = (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(screen, PieceColors.MOVE_DOT.value, center, TILE_SIZE // 6)

def handle_click(board: Board, x: int, y: int):
    global selected_piece

    clicked_tile = board.tiles[x][y]
    
    for piece in clicked_tile.pieces:
        if not piece.is_ghost:
            selected_piece = piece
            return
    
    if selected_piece:
        possible_moves = board.get_neighbors(selected_piece.position[0], selected_piece.position[1])
        if (x, y) in possible_moves and board.tiles[x][y].isFloor():
            board.move_piece(selected_piece, x, y)
            update_player_board(selected_piece.owner, board)
            selected_piece = None

################################# Main Loop #################################

def main():
    global selected_piece

    pygame.init()
    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
    clock = pygame.time.Clock()
    
    board_state, players = generate_game(["Player 1", "Player 2"])
    current_view = board_state

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_board(screen, current_view)

        if selected_piece:
            draw_possible_moves(screen, current_view, selected_piece)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[1] // TILE_SIZE, event.pos[0] // TILE_SIZE
                handle_click(board_state, x, y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    current_view = board_state  # Show full board state
                elif event.key == pygame.K_1:
                    current_view = players[0].board  # Show Player 1's board
                elif event.key == pygame.K_2:
                    current_view = players[1].board  # Show Player 2's board
                elif event.key == pygame.K_RETURN:
                    remove_ghost_pieces(board_state)
                    update_player_board(players[0], board_state)
                    update_player_board(players[1], board_state)

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()