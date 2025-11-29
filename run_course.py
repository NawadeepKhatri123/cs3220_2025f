# run_course_schedule.py

from src.course_schedule_data import (
    make_course_schedule_csp,
    VARIABLES,
)
from src.course_schedule_utils import print_timetable
from src.algorithms import min_conflicts1  # adjust name if your lab uses a different one


if __name__ == "__main__":
    csp = make_course_schedule_csp()

    print("Solving course schedule CSP using min_conflicts...\n")

    # max_steps can be adjusted based on your lab instructions.
    solution = min_conflicts1(csp, max_steps=10000)

    if solution is None:
        print("No schedule found.")
    else:
        print("=== Raw assignment (variable -> (day, slot)) ===")
        for var in sorted(VARIABLES):
            print(f"{var:10s} -> {solution[var]}")

        print_timetable(solution)
