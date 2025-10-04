import random
from src.agentClass import Agent,Environment
from src.thingClass import Thing   # assume you have these base classes already

# --- Recipients ---
class OfficeManager(Thing):
    def __init__(self):
        super().__init__()
        self.package_received = False

class ITSpecialist(Thing):
    def __init__(self):
        super().__init__()
        self.package_received = False

class Student(Thing):
    def __init__(self):
        super().__init__()
        self.package_received = False


# --- Environment Classes ---
class environmentPro(Environment):
    """Extended Environment with ability to place recipients randomly."""
    def __init__(self, num_rooms=4):
        super().__init__()
        self.num_rooms = num_rooms
        self.rooms = [[] for _ in range(num_rooms)]  # each room can have multiple recipients
        self.agent_location = random.randint(0, num_rooms - 1)

    def add_thing(self, thing, room=None):
        if room is None:
            room = random.randint(0, self.num_rooms - 1)
        self.rooms[room].append(thing)

    def percept(self, agent):
        """Return agent location and all recipients in the current room."""
        return (self.agent_location, self.rooms[self.agent_location])

    def execute_action(self, agent, action):
        """Actions: Deliver <package>, MoveRight, Stop"""
        if action.startswith("Deliver"):
            _, recipient = action.split()
            # mark recipient as served
            for r in self.rooms[self.agent_location]:
                if not r.package_received and r.__class__.__name__.lower() == recipient.lower():
                    r.package_received = True
                    print(f"Delivered to {recipient} at room {self.agent_location}")
        elif action == "MoveRight":
            if self.agent_location < self.num_rooms - 1:
                self.agent_location += 1
            else:
                self.agent_location = self.num_rooms - 1
        elif action == "Stop":
            print("Agent has stopped.")

class CompanyEnvironment(environmentPro):
    """Specific Office Delivery Environment"""
    def __init__(self):
        super().__init__(num_rooms=4)
        # Randomly place one recipient of each type
        self.add_thing(OfficeManager())
        self.add_thing(ITSpecialist())
        self.add_thing(Student())
