def minimax_search(game, state):
    """
    Run minimax search to find the best move for the current player.
    Returns: (best_score, best_move)
    """
    player = state.to_move

    def max_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        
        v = -float('inf')
        move = None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v = v2
                move = a
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        
        v = float('inf')
        move = None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v = v2
                move = a
        return v, move

    return max_value(state)
