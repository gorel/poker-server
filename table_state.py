from gamehelper import card2str
import sqlite3

# Database column information
TABLE_INDEX_COLUMN          = 0
TABLE_ROUND_COLUMN          = 1
TABLE_CURRENT_BET_COLUMN    = 2
TABLE_CURRENT_POT_COLUMN    = 3
TABLE_PHASE_COLUMN          = 4
TABLE_COMM1_COLUMN          = 5
TABLE_COMM2_COLUMN          = 6
TABLE_COMM3_COLUMN          = 7
TABLE_COMM4_COLUMN          = 8
TABLE_COMM5_COLUMN          = 9

# Constants
SELECT_QUERY = "SELECT * FROM table_states WHERE table_id=?"
SELECT_ALL_QUERY = """
    SELECT Table.table_id, User.display, Player.stack, Player.my_turn, Player.is_folded,  Player.hand1, Player.hand2, Table.comm1, Table.comm2, Table.comm3, Table.comm4 Table.comm5
    FROM table_states Table
    INNER JOIN players Player
        ON Table.table_id=Player.table_id
    INNER JOIN users User
        ON Player.user_id=User.user_id
    ORDER BY Table.table_id
"""

class TableState:
    def __init__(self, table):
        self.table_id = table[TABLE_INDEX_COLUMN]
        self.round_id = table[TABLE_ROUND_COLUMN]
        self.current_bet = table[TABLE_CURRENT_BET_COLUMN]
        self.current_pot = table[TABLE_CURRENT_POT_COLUMN]
        self.phase = table[TABLE_PHASE_COLUMN]
        card1 = card2str(table[TABLE_COMM1_COLUMN])
        card2 = card2str(table[TABLE_COMM2_COLUMN]]
        card3 = card2str(table[TABLE_COMM3_COLUMN]]
        card4 = card2str(table[TABLE_COMM4_COLUMN]]
        card5 = card2str(table[TABLE_COMM5_COLUMN]]
        self.community = [card1, card2, card3, card4, card5]

    def get_table_id(self):
        return self.table_id

    def get_round_id(self):
        return self.round_id

    def get_current_bet(self):
        return self.current_bet

    def get_current_pot(self):
        return self.current_pot

    def get_phase(self):
        return self.phase

    def get_community_cards(self):
        return [card for card in self.community if card is not None]

    @classmethod
    def get(self_class, player):
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        data = (player.get_table_id(), )
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
    def get_all_info(self_class):
        # TODO: Learn SQL to make this actually work?
        tables_info = []
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute(SELECT_ALL_QUERY)

        for row in c.fetchone():

