import random

# --- 1. COPY OF CSP CLASS & ALGORITHM ---
class CSP:
    def __init__(self, variables, domains, neighbors, constraints):
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.nassigns = 0

    def assign(self, var, val, assignment):
        assignment[var] = val
        self.nassigns += 1

    def nconflicts(self, var, val, assignment):
        def conflict(var2):
            val2 = assignment.get(var2)
            return val2 is not None and not self.constraints(var, val, var2, val2)
        return sum(conflict(v) for v in self.neighbors[var])

def min_conflicts(csp, max_steps=1000):
    current = {}
    for var in csp.variables:
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)

    for i in range(max_steps):
        conflicted = [v for v in csp.variables if csp.nconflicts(v, current[v], current) > 0]
        if not conflicted:
            return current
        var = random.choice(conflicted)
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)
    return None

def min_conflicts_value(csp, var, current):
    def count_conflicts(val):
        return csp.nconflicts(var, val, current)
    vals = csp.domains[var][:]
    random.shuffle(vals)
    return min(vals, key=count_conflicts)

# --- 2. AUSTRALIA MAP PROBLEM DEFINITION ---
australia_vars = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
colors = ['R', 'G', 'B']

australia_domains = {var: colors for var in australia_vars}

# Adjacency graph
australia_neighbors = {
    'WA': ['NT', 'SA'],
    'NT': ['WA', 'Q', 'SA'],
    'Q':  ['NT', 'NSW', 'SA'],
    'NSW':['Q', 'V', 'SA'],
    'V':  ['NSW', 'SA'],
    'SA': ['WA', 'NT', 'Q', 'NSW', 'V'],
    'T':  []
}

# Constraint function: Neighbors cannot have same color
def map_constraints(A, a, B, b):
    return a != b

# --- 3. EXECUTION ---
if __name__ == "__main__":
    print("--- Solving Australia Map Coloring ---")
    map_csp = CSP(australia_vars, australia_domains, australia_neighbors, map_constraints)

    solution = min_conflicts(map_csp)

    if solution:
        print("Solution found:")
        for k, v in solution.items():
            print(f"{k}: {v}")
        
        # Verify solution
        conflicts = 0
        for var in australia_vars:
            conflicts += map_csp.nconflicts(var, solution[var], solution)
        print(f"Total Conflicts: {conflicts}")
    else:
        print("No solution found within step limit.")
