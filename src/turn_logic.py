import random
from base_classes import Board, Player, TileType, Piece

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

def remove_piece(board: Board, piece: Piece):
    board.get_tile(piece.position[0], piece.position[1]).pieces.remove(piece)

def kill_piece(board: Board, piece: Piece):
    for x in range(board.height):
        for y in range(board.width):
            for p in board.get_tile(x, y).pieces:
                if p.owner == piece.owner and p.number == piece.number:
                    board.get_tile(x, y).pieces.remove(p)

def clear_vision(player: Player):
    for x in range(player.board.height):
        for y in range(player.board.width):
            if player.board.get_tile(x, y).type == TileType.UNKNOW:
                continue
            if player.board.get_tile(x, y).is_floor():
                player.board.get_tile(x, y).type = TileType.FOG_FLOOR
            elif player.board.get_tile(x, y).is_wall():
                player.board.get_tile(x, y).type = TileType.FOG_WALL
            else:
                player.board.get_tile(x, y).type = TileType.FOG_VOID

def clear_pieces(player: Player):
    for x in range(player.board.height):
        for y in range(player.board.width):
            player.board.get_tile(x, y).pieces = []

def get_piece_vision(board: Board, piece: Piece):
    fog_tiles = set()
    clear_tiles = set()

    for x in range(piece.position[0] - 4, piece.position[0] + 5):
        for y in range(piece.position[1] - 4, piece.position[1] + 5):
            if board.out_of_bounds(x, y):
                continue
            fog_tiles.add((x, y))
    for x in range(piece.position[0] - 2, piece.position[0] + 3):
        for y in range(piece.position[1] - 2, piece.position[1] + 3):
            if board.out_of_bounds(x, y):
                continue
            clear_tiles.add((x, y))

    return fog_tiles, clear_tiles

def update_own_pieces(player: Player, board: Board):
    clear_pieces(player)
    pieces = board.get_pieces(player, True)
    for piece in pieces:
        player.board.get_tile(piece.position[0], piece.position[1]).pieces.append(piece)


def update_vision(player: Player, board: Board):
    clear_vision(player)

    fog_tiles = set()
    clear_tiles = set()

    for piece in player.board.get_pieces(player, True):
        fog, clear = get_piece_vision(board, piece)
        fog_tiles.update(fog)
        clear_tiles.update(clear)

    for x in range(board.height):
        for y in range(board.width):
            if (x, y) in clear_tiles:
                player.board.get_tile(x, y).type = board.get_tile(x, y).type
            elif (x, y) in fog_tiles:
                if board.get_tile(x, y).is_floor():
                    player.board.get_tile(x, y).type = TileType.FOG_FLOOR
                elif board.get_tile(x, y).is_wall():
                    player.board.get_tile(x, y).type = TileType.FOG_WALL
                else:
                    player.board.get_tile(x, y).type = TileType.FOG_VOID

def update_opponent_pieces(player: Player, board: Board):
    clear_vision = player.board.get_clear_vision()
    for x, y in clear_vision:
        for piece in board.get_tile(x, y).pieces:
            if piece.owner != player:
                player.board.get_tile(x, y).pieces.append(piece)

def update_player_board(player: Player, board: Board):
    update_own_pieces(player, board)
    update_vision(player, board)
    update_opponent_pieces(player, board)

def remove_ghost_pieces(board: Board):
    for x in range(board.height):
        for y in range(board.width):
            board.tiles[x][y].pieces = [p for p in board.tiles[x][y].pieces if not p.is_ghost]

def resolve_duels(game_board: Board):
    for x in range(game_board.height):
        for y in range(game_board.width):
            tile = game_board.get_tile(x, y)
            if not tile.is_floor() or len(tile.pieces) < 2:
                continue

            pieces_by_owner = {}

            for piece in tile.pieces:
                if piece.owner not in pieces_by_owner:
                    pieces_by_owner[piece.owner] = []
                pieces_by_owner[piece.owner].append(piece)

            if len(pieces_by_owner) > 1:
                participants = [pieces[0] for pieces in pieces_by_owner.values()]
                print(f"Participants: {[p.number for p in participants]}")
                rolls = {piece: random.randint(1, 6) for piece in participants}
                min_roll = min(rolls.values())

                losers = [piece for piece, roll in rolls.items() if roll == min_roll]
                print(f"Losers: {[p.number for p in losers]}")
                for loser in losers:
                    kill_piece(game_board, loser)
                    print(f"Player {loser.owner.name}'s piece {loser.number} was killed")