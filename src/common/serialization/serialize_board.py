import json
from common.base_classes import Board, Piece, Tile, TileType

class BoardEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Board):
            encoded_board = {
                "class": "Board",
                "width": obj.width,
                "height": obj.height,
                "gameover": obj.gameover,
                "tiles": []
            }

            for row in obj.tiles:
                encoded_row = []
                for tile in row:
                    encoded_tile = {
                        "class": "Tile",
                        "type": tile.type.value,
                        "pieces": []
                    }
                    for piece in tile.pieces:
                        encoded_piece = {
                            "class": "Piece",
                            "number": piece.number,
                            "position": piece.position,
                            "owner": piece.owner,
                            "is_ghost": piece.is_ghost,
                            "color": piece.color
                        }
                        encoded_tile["pieces"].append(encoded_piece)

                    encoded_row.append(encoded_tile)
                encoded_board["tiles"].append(encoded_row)

            return encoded_board

        return super().default(obj)

def as_board(dct):
    if dct["class"] == "Board":
        board = Board(dct["width"], dct["height"], TileType.WALL)
        board.gameover = dct["gameover"]

        board.tiles = dct["tiles"]

        return board

    elif dct["class"] == "Tile":
        tile = Tile(TileType(dct["type"]))
        tile.pieces = dct["pieces"]

        return tile
    
    elif dct["class"] == "Piece":
        return Piece(dct["number"], (dct["position"][0], dct["position"][1]), dct["owner"], dct["is_ghost"], dct["color"])

    return dct
