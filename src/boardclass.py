class Board(dict):
    """A dictionary-like object that represents the state of a board."""
    
    def __init__(self, height=3, width=3, to_move='X', utility=0):
        self.height = height
        self.width = width
        self.to_move = to_move
        self.utility = utility
        # The dictionary itself stores {square: player} mappings.
        # e.g. {(0,0): 'X', (1,1): 'O'}
    
    def new(self, changes, to_move=None):
        """Return a new Board with some changes."""
        if to_move is None:
            to_move = self.to_move
            
        board = Board(self.height, self.width, to_move, self.utility)
        board.update(self) # Copy current state
        board.update(changes) # Apply new moves
        return board
