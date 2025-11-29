# src/course_schedule_data.py

from src.CSPclass import CSP

# ---------- Basic sets ----------

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
SLOTS = ["class1", "class2", "class3"]


def all_times():
    """All possible (day, slot) pairs."""
    return [(d, s) for d in DAYS for s in SLOTS]


# Events (variables) and their (course, kind)
# kind: 'lec' for lecture, 'lab' for lab
EVENTS = {
    # Practical Programming Methodology (PPM): 2 lectures, 2 labs
    "PPM_lec1": ("PPM", "lec"),
    "PPM_lec2": ("PPM", "lec"),
    "PPM_lab1": ("PPM", "lab"),
    "PPM_lab2": ("PPM", "lab"),

    # Algorithms I (ALG): 2 lectures, 1 lab
    "ALG_lec1": ("ALG", "lec"),
    "ALG_lec2": ("ALG", "lec"),
    "ALG_lab1": ("ALG", "lab"),

    # Operating Systems (OS): 2 lectures, 1 lab
    "OS_lec1": ("OS", "lec"),
    "OS_lec2": ("OS", "lec"),
    "OS_lab1": ("OS", "lab"),

    # File & DB Management (FDB): 2 lectures, 1 lab
    "FDB_lec1": ("FDB", "lec"),
    "FDB_lec2": ("FDB", "lec"),
    "FDB_lab1": ("FDB", "lab"),
}

VARIABLES = list(EVENTS.keys())


def day_index(day: str) -> int:
    """Map day string to index 0..4 (Mon=0,...,Fri=4)."""
    return DAYS.index(day)


def make_domains():
    """
    Domain for each variable: all (day, slot) combinations.
    """
    domain = all_times()
    return {var: domain[:] for var in VARIABLES}


def make_neighbors():
    """
    Make a complete neighbor graph: every event is neighbor with every other.
    All constraints are checked pairwise.
    """
    neighbors = {}
    for v in VARIABLES:
        neighbors[v] = [u for u in VARIABLES if u != v]
    return neighbors


def schedule_constraint(Xi, vi, Xj, vj):
    """
    Binary constraint between two events Xi, Xj.

    Xi, Xj: variable names like "PPM_lec1"
    vi, vj: assignments (day, slot) like ("Mon", "class1")
    """

    # 1) No two events at the exact same (day, slot)
    if vi == vj:
        return False

    day_i, slot_i = vi
    day_j, slot_j = vj

    course_i, kind_i = EVENTS[Xi]
    course_j, kind_j = EVENTS[Xj]

    # If they are different courses, only "no same time slot" matters
    # (already enforced above). So we're fine.
    if course_i != course_j:
        return True

    # Same course => apply extra rules.

    # 2) Two lectures of same course can't be on the same day
    if kind_i == "lec" and kind_j == "lec":
        if day_i == day_j:
            return False

    # 3) Two labs of same course can't be on adjacent days
    if kind_i == "lab" and kind_j == "lab":
        if abs(day_index(day_i) - day_index(day_j)) == 1:
            return False

    # Lecture + lab of same course is allowed, even on same day.
    return True


def make_course_schedule_csp():
    """
    Build and return the CSP for the course scheduling problem.
    """
    domains = make_domains()
    neighbors = make_neighbors()

    def constraints(Xi, vi, Xj, vj):
        return schedule_constraint(Xi, vi, Xj, vj)

    return CSP(VARIABLES, domains, neighbors, constraints)
