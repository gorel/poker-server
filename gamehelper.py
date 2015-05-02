# Constants
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
SUITS = ["C", "D", "S", "H"]

# Helper functions for neatly returning game state data
def card2str(card_id):
    if card_id is None:
        return None

    rank = RANKS[card_id / 4]
    suit = SUITS[card_id % 4]
    return rank + suit
