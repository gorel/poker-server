from gamehelper import card2str
import sqlite3

# Database column information
PLAYER_ROUND_ID_COLUMN      = 0
PLAYER_USER_ID_COLUMN       = 1
PLAYER_TABLE_ID_COLUMN      = 2
PLAYER_INITIAL_STACK_COLUMN = 3
PLAYER_STACK_COLUMN         = 4
PLAYER_MY_TURN_COLUMN       = 5
PLAYER_HAND1_COLUMN         = 6
PLAYER_HAND2_COLUMN         = 7
PLAYER_IS_FOLDED_COLUMN     = 8
PLAYER_DISPLAY_COLUMN       = 9

# Constants
SELECT_QUERY = "SELECT Player.*, User.display FROM players Player INNER JOIN users User on Player.user_id = User.id WHERE User.apikey=? ORDER BY Player.id DESC LIMIT 1"
SELECT_OPPONENTS_QUERY = "SELECT * FROM players WHERE table_id=? AND round_id=? AND user_id!=?"
INSERT_ACTION_QUERY = "INSERT INTO player_actions ('round_id', 'player_id', 'action', 'amount') VALUES (?, ?, ?, ?)"
GET_DISPLAY_QUERY = "SELECT User.* FROM users User INNER JOIN players Player on User.id = Player.user_id WHERE Player.user_id=?"

class PlayerNotFoundError(Exception):
    pass

class Player:
    def __init__(self, player):
        self.round_id = player[PLAYER_ROUND_ID_COLUMN]
        self.player_id = player[PLAYER_USER_ID_COLUMN]
        self.table_id = player[PLAYER_TABLE_ID_COLUMN]
        self.initial_stack = player[PLAYER_INITIAL_STACK_COLUMN]
        self.stack = player[PLAYER_STACK_COLUMN]
        self.my_turn = bool(player[PLAYER_MY_TURN_COLUMN])
        card1 = card2str(player[PLAYER_HAND1_COLUMN])
        card2 = card2str(player[PLAYER_HAND2_COLUMN])
        self.hand = [card1, card2]
        self.is_folded = bool(player[PLAYER_IS_FOLDED_COLUMN])
        self.display = None
        self.display = player.get_display()

    def get_round_id(self):
        return self.round_id

    def get_player_id(self):
        return self.player_id

    def get_table_id(self):
        return self.table_id

    def get_display(self):
        if self.display is None:
            conn = sqlite3.connect(app.config['DATABASE'])
            c = conn.cursor()
            data = (self.get_player_id(), )
            c.execute(GET_DISPLAY_QUERY, data)
            user = c.fetchone()
            conn.close()

            self.display = user[USER_DISPLAY_COLUMN]

        return self.display

    def get_initial_stack(self):
        return self.initial_stack

    def get_stack(self):
        return self.stack

    def get_my_turn(self):
        return self.my_turn

    def get_hand(self):
        return [card for card in self.hand if card is not None]

    def get_is_folded(self):
        return self.is_folded

    def post_action(self, action, amount=0):
        action = action2db(action)
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (self.get_round_id(), self.get_player_id(), action, amount, )
        c.execute(INSERT_ACTION_QUERY, data)
        conn.close()

    def get_public_info(self):
        info = {}
        info['name'] = self.get_display()
        info['initial_stack'] = self.get_initial_stack()
        info['stack'] = self.get_stack()
        info['folded'] = self.get_is_folded()
        return info

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

    @classmethod
    def get_opponents(self_class, player):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (player.get_table_id(), player.get_round_id(), player.get_user_id(), )
        c.execute(SELECT_OPPONENTS_QUERY, data)
        opponents = c.fetchall()
        conn.close()

        return [Player(opponent).get_public_info() for opponent in opponents]
