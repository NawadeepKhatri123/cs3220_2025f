import random

# ==========================================
# PART A: THE CSP FRAMEWORK (REQUIRED FOR ALL TASKS)
# ==========================================

class CSP:
    def __init__(self, variables, domains, neighbors, constraints):
        """
        variables: List of variable names.
        domains: Dict mapping variables to their domain of values.
        neighbors: Dict mapping variables to list of neighbors.
        constraints: Function f(A, a, B, b) returns True if consistent.
        """
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.nassigns = 0

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment."""
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""
        def conflict(var2):
            val2 = assignment.get(var2)
            return val2 is not None and not self.constraints(var, val, var2, val2)

        return sum(conflict(v) for v in self.neighbors[var])

# ==========================================
# PART B: MIN-CONFLICTS ALGORITHM
# ==========================================

def min_conflicts(csp, max_steps=1000):
    """
    Solves a CSP by iteratively changing the value of a variable 
    that is currently in conflict to a value that minimizes conflicts.
    """
    # 1. Generate a complete assignment for all variables (can be random)
    current = {}
    for var in csp.variables:
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)

    # 2. Iterate to improve
    for i in range(max_steps):
        conflicted = [v for v in csp.variables if csp.nconflicts(v, current[v], current) > 0]
        
        if not conflicted:
            return current  # Solution found (0 conflicts)

        # Pick a random conflicted variable
        var = random.choice(conflicted)
        
        # Choose value that minimizes conflicts
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)

    return None  # Failed to find solution within max_steps

def min_conflicts_value(csp, var, current):
    """
    Return the value that will give the least number of conflicts.
    If there is a tie, choose one at random.
    """
    def count_conflicts(val):
        return csp.nconflicts(var, val, current)
    
    # Get shuffle of domain to ensure randomness in ties
    vals = csp.domains[var][:]
    random.shuffle(vals)
    
    return min(vals, key=count_conflicts)

# ==========================================
# PART C: SIMPLE TEST (So the script does something)
# ==========================================
if __name__ == "__main__":
    print("--- Testing Min-Conflicts Implementation ---")
    
    # Simple problem: A must not equal B
    vars_test = ['A', 'B']
    domains_test = {'A': [1, 2, 3], 'B': [1, 2, 3]}
    neighbors_test = {'A': ['B'], 'B': ['A']}
    
    def test_constraints(A, a, B, b):
        return a != b
        
    simple_csp = CSP(vars_test, domains_test, neighbors_test, test_constraints)
    result = min_conflicts(simple_csp)
    
    print(f"Test Result: {result}")
    print("If you see a result where A != B, the algorithm works!")
