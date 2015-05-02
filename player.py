from dbhelper import *
from gamehelper import card2str
import sqlite3

# Constants
# TODO: Select based on api key
SELECT_QUERY = "SELECT Player.* FROM players Player INNER JOIN users User on Player.user_id = User.id WHERE User.apikey=? ORDER BY Player.id DESC LIMIT 1"

class PlayerNotFoundError(Exception):
    pass

class Player:
    def __init__(self, player):
        self.id = player[PLAYER_INDEX_COLUMN]
        self.player_id = player[PLAYER_USER_ID_COLUMN]
        self.table_id = player[PLAYER_TABLE_ID_COLUMN]
        self.initial_stack = player[PLAYER_INITIAL_STACK_COLUMN]
        self.stack = player[PLAYER_STACK_COLUMN]
        self.my_turn = bool(player[PLAYER_MY_TURN_COLUMN])
        card1 = card2str(player[PLAYER_HAND1_COLUMN])
        card2 = card2str(pplayer[PLAYER_HAND2_COLUMN]
        self.hand = [card1, card2]
        self.is_folded = bool(player[PLAYER_IS_FOLDED_COLUMN])

    def get_player_id(self):
        return self.player_id

    def get_table_id(self):
        return self.table_id

    def get_initial_stack(self):
        return self.initial_stack

    def get_stack(self):
        return self.stack

    def get_my_turn(self):
        return self.my_turn

    def get_hand(self):
        return self.hand

    def get_is_folded(self):
        return self.is_folded

    @classmethod
    def get(self_class, api_key):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (api_key, )
        c.execute(SELECT_QUERY, data)
        player = c.fetchone()
        conn.close()

        try:
            if player is None:
                raise PlayerNotFoundError
            return Player(player)
        except PlayerNotFoundError:
            return None
