import json
from base_classes import PlayerTurn, PieceAction, Action, ActionType

class PlayerTurnEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PlayerTurn):
            encoded_turn = obj.__dict__
            encoded_turn["class"] = "PlayerTurn"

            encoded_pieces_actions = encoded_turn["pieces_actions"]
            encoded_pieces_actions.clear()

            for piece_action in obj.pieces:
                encoded_piece_action = piece_actions.__dict__
                encoded_piece_action["class"] = "PieceAction"

                encoded_actions = encoded_piece_action["actions"]
                encoded_actions.clear()

                for action in piece_action.actions:
                    encoded_action = action.__dict__
                    encoded_action["type"] = action.type.value
                    encoded_action["class"] = "Action"
                    encoded_actions.append(encoded_action)

                encoded_pieces_actions.append(encoded_piece_action)

            return encoded_turn

        return super().default(obj)

def as_player_turn(dct):
    if dct["class"] == "PlayerTurn":
        return PlayerTurn(dct["player_name"], dct["pieces_actions"])
    elif dct["class"] == "PieceAction":
        return PieceAction(dct["piece_number"], dct["actions"])
    elif dct["class"] == "Action":
        return Action(ActionType(dct["action_type"]), dct["args"])

    return dct
