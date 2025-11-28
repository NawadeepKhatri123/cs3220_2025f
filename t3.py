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

# --- 2. COURSE SCHEDULING PROBLEM DEFINITION ---
courses = {
    'PPM': {'type': 'Programming', 'components': ['Lec', 'Lab1', 'Lab2']},
    'Algo': {'type': 'Theory', 'components': ['Lec', 'Lab1', 'Lab2']},
    'AI': {'type': 'Theory', 'components': ['Lec', 'Lab1']}
}

# Resources
days = ['Mon', 'Tue', 'Wed']
times = ['10am', '2pm']
rooms = ['Room A', 'Room B']

# Generate Variables
variables = []
for course_name, details in courses.items():
    for comp in details['components']:
        variables.append(f"{course_name}_{comp}")

# Generate Domains (All possible combinations of Day, Time, Room)
domain_values = []
for d in days:
    for t in times:
        for r in rooms:
            domain_values.append((d, t, r))

domains = {var: domain_values for var in variables}

# Generate Neighbors (Complete graph - everyone checks everyone)
neighbors = {var: [v for v in variables if v != var] for var in variables}

# --- Constraints Function ---
def schedule_constraints(A, a_val, B, b_val):
    # a_val is tuple (day, time, room)
    day_A, time_A, room_A = a_val
    day_B, time_B, room_B = b_val
    
    # 1. Resource Constraint: No two classes in same room at same time
    if day_A == day_B and time_A == time_B and room_A == room_B:
        return False
    
    # Parse Course Names (e.g., PPM_Lab1 -> Course: PPM, Type: Lab1)
    course_A, type_A = A.split('_')
    course_B, type_B = B.split('_')
    
    # 2. Instructor Constraint: Same course parts usually shouldn't overlap in time 
    if course_A == course_B and day_A == day_B and time_A == time_B:
        return False

    # 3. Lab Adjacency Constraint
    # "There can't be 2 labs on the same course on an adjacent day."
    if course_A == course_B and "Lab" in type_A and "Lab" in type_B:
        # Map days to indices to check adjacency
        day_map = {'Mon': 0, 'Tue': 1, 'Wed': 2}
        idx_A = day_map[day_A]
        idx_B = day_map[day_B]
        
        # Check absolute difference
        if abs(idx_A - idx_B) == 1:
            return False

    return True

# --- 3. EXECUTION ---
if __name__ == "__main__":
    print("\n--- Solving Course Scheduling ---")
    schedule_csp = CSP(variables, domains, neighbors, schedule_constraints)

    # Run Min-Conflicts
    # Increased max_steps to ensure convergence for this harder problem
    sched_solution = min_conflicts(schedule_csp, max_steps=10000)

    # --- Output ---
    if sched_solution:
        # Sort for cleaner display
        sorted_sched = sorted(sched_solution.items(), key=lambda x: (x[1][0], x[1][1])) # Sort by Day, Time
        
        print(f"{'Class':<15} | {'Day':<5} | {'Time':<5} | {'Room':<10}")
        print("-" * 45)
        for var, val in sorted_sched:
            print(f"{var:<15} | {val[0]:<5} | {val[1]:<5} | {val[2]:<10}")
            
        # Verification
        conflicts = 0
        for var in variables:
            conflicts += schedule_csp.nconflicts(var, sched_solution[var], sched_solution)
        print(f"\nFinal Conflicts: {conflicts}")
    else:
        print("No valid schedule found. Try increasing max_steps or loosening constraints.")
