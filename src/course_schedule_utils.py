# src/course_schedule_utils.py

from src.course_schedule_data import DAYS, SLOTS


def build_timetable(solution):
    """
    Build mapping (day, slot) -> list of event names from a solution dict.
    solution: dict var -> (day, slot)
    """
    timetable = {}
    for var, (day, slot) in solution.items():
        timetable.setdefault((day, slot), []).append(var)
    return timetable


def print_timetable(solution):
    """
    Pretty-print the schedule as a weekly timetable to the console.
    """
    if solution is None:
        print("No schedule found.")
        return

    timetable = build_timetable(solution)

    print("\n=== Weekly timetable ===")
    for day in DAYS:
        print(f"\n{day}:")
        for slot in SLOTS:
            events = timetable.get((day, slot), [])
            if events:
                print(f"  {slot}: {', '.join(events)}")
            else:
                print(f"  {slot}: -- free --")
