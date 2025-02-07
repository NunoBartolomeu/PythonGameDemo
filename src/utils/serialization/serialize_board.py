import json
from base_classes import Board, Piece, Tile, TileType

class BoardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Board):
            encoded_board = obj.__dict__
            encoded_board["class"] = "Board"

            encoded_tiles = encoded_board["tiles"]

            for idx, tilesX in enumerate(obj.tiles):
                for idy, tileY in enumerate(tilesX):
                    encoded_tiles[idx][idy] = tileY.__dict__
                    encoded_tiles[idx][idy]["class"] = "Tile"

                    encoded_tiles[idx][idy]["type"] = tileY.type.value

                    for piece in tileY.pieces:
                        encoded_piece = piece.__dict__
                        encoded_piece["class"] = "Piece"
                        encoded_tiles[idx][idy]["pieces"].append(encoded_piece)

            return encoded_board

        return super().default(obj)

def as_board(dct):
    # Tiles have to be replaced, maybe shouldn't initialize tiles inside constructor or use another class

    if dct["class"] == "Board":
        board = Board(dct["width"], dct["height"], TileType.WALL)

        board.tiles = dct["tiles"]

        return board
    elif dct["class"] == "Tile":
            tile = Tile(TileType(dct["type"]))
            tile.pieces = dct["pieces"]

            return tile
    elif dct["class"] == "Piece":
        return Piece(dct["number"], dct["position"], dct["owner"], dct["is_ghost"])

    return dct
