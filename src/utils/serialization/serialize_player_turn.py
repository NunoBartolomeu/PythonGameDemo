import json
from common.base_classes import PlayerTurn, Action, ActionType

class PlayerTurnEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PlayerTurn):
            encoded_turn = {
                "class": "PlayerTurn",
                "player_name": obj.player_name,
                "pieces_actions": {}
            }

            for piece_number, actions in obj.pieces_actions.items():
                encoded_turn["pieces_actions"][piece_number] = []
                for action in actions:
                    encoded_action = {
                        "class": "Action",
                        "action_type": action.type.value,
                        "args": []
                    }

                    for arg in action.args:
                        encoded_action["args"].append(arg)
                    encoded_turn["pieces_actions"][piece_number].append(encoded_action)

            return encoded_turn

        return super().default(obj)

def as_player_turn(dct):
    if "class" not in dct:
        return dct

    if dct["class"] == "PlayerTurn":
        player_turn = PlayerTurn(dct["player_name"])
        player_turn.pieces_actions = dct["pieces_actions"]

        return player_turn

    elif dct["class"] == "Action":
        return Action(ActionType(dct["action_type"]), dct["args"])

    return dct
