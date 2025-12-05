import sys
import os

# Ensure we can import from the current directory (acting as root)
sys.path.append(os.getcwd())

# We need to mock the imports if the files aren't physically in a 'src' folder 
# during this execution, or ensure the user puts them there.
# This script assumes the user has the following structure:
# /
#   test_tictactoe.py
#   src/
#       minimax.py
#       boardClass.py
#       gameClass.py     (User provided)
#       TicTacToeGameClass.py (User provided)
#       players.py       (User provided)

try:
    from src.TicTacToeGameClass import TicTacToe
    from src.players import random_player, smart_player
    from src.minimax import minimax_search
    from src.gameClass import play_game
except ImportError:
    print("Error: Could not import modules. Please ensure you have the 'src' folder containing:")
    print(" - gameClass.py")
    print(" - TicTacToeGameClass.py")
    print(" - players.py")
    print(" - minimax.py")
    print(" - boardClass.py")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting Tic-Tac-Toe Game: Random (X) vs Minimax (O)")
    
    # Initialize Game
    game = TicTacToe()
    
    # Define Strategies
    # X plays randomly, O uses the Minimax algorithm we just created
    strategies = {
        'X': random_player,
        'O': smart_player(minimax_search)
    }
    
    # Play the game
    # play_game returns the final state
    final_state = play_game(game, strategies, verbose=True)
    
    print("\nGame Over!")
    if final_state.utility == 0:
        print("Result: Draw")
    else:
        # Note: TicTacToe.utility stores +1 for X win, -1 for O win relative to board
        # But game.utility(state, player) handles the perspective.
        winner = 'X' if final_state.utility > 0 else 'O'
        print(f"Result: {winner} Wins!")
