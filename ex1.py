import random

# ---------------- Base Agent ----------------
class Agent:
    def __init__(self, program=None):
        self.alive = True
        self.performance = 5   # start performance
        self.location = None

        if program is None:
            def program(percept):
                return random.choice(["MoveRight", "MoveLeft", "Eat", "Drink", "Fight"])
        self.program = program


# ---------------- Base Environment ----------------
class Environment:
    def __init__(self):
        self.agents = []

    def percept(self, agent):
        raise NotImplementedError

    def execute_action(self, agent, action):
        raise NotImplementedError

    def default_location(self, thing):
        return 0

    def is_done(self):
        return not any(agent.alive for agent in self.agents)

    def step(self):
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    percept = self.percept(agent)
                    action = agent.program(percept)
                    print(f"Cat sees {percept}, chooses {action}")
                    actions.append((agent, action))
                else:
                    actions.append((agent, None))

            for (agent, action) in actions:
                if action:
                    self.execute_action(agent, action)
        else:
            print("Game Over - no alive agents.")

    def run(self, steps=10):
        for i in range(steps):
            if self.is_done():
                print("Game Over early.")
                break
            print(f"\nStep {i+1}:")
            self.step()


# ---------------- Cat Programs ----------------
def RandomCatProgram(actions):
    return lambda percept: random.choice(actions)

def ReflexCatProgram(rules):
    def program(percept):
        if percept is None:
            state = "Empty"
        elif "Mouse" in percept:
            state = "Mouse"
        elif "Milk" in percept:
            state = "Milk"
        elif "Dog" in percept:
            state = "Dog"
        else:
            state = "Empty"
        return rules.get(state, "MoveRight")
    return program


# ---------------- Rules & Actions ----------------
catActions = ["MoveRight", "MoveLeft", "Eat", "Drink", "Fight"]

catRules = {
    "Mouse": "Eat",
    "Milk": "Drink",
    "Dog": "Fight",
    "Empty": "MoveRight"
}


# ---------------- CrazyHouse Environment ----------------
class CrazyHouse(Environment):
    def __init__(self, cat):
        super().__init__()
        self.rooms = [None] * 5
        self.add_thing(cat, random.randint(0, 4))
        self.place_things()

    def add_thing(self, thing, location=None):
        if thing not in self.agents:
            thing.location = location if location is not None else self.default_location(thing)
            self.agents.append(thing)

    def place_things(self):
        positions = random.sample(range(5), 3)
        mouse_pos, milk_pos, dog_pos = positions

        # Mouse + Milk -> only Mouse stays
        if mouse_pos == milk_pos:
            self.rooms[mouse_pos] = ["Mouse"]
        else:
            self.rooms[mouse_pos] = ["Mouse"]
            self.rooms[milk_pos] = ["Milk"]

        # Mouse + Dog -> move Mouse to neighbor
        if mouse_pos == dog_pos:
            self.rooms[dog_pos] = ["Dog"]
            new_pos = max(0, min(4, dog_pos + random.choice([-1, 1])))
            self.rooms[new_pos] = ["Mouse"]
        else:
            if self.rooms[dog_pos] is None:
                self.rooms[dog_pos] = []
            self.rooms[dog_pos].append("Dog")

    def percept(self, agent):
        return self.rooms[agent.location]

    def execute_action(self, agent, action):
        room = self.rooms[agent.location]
        agent.performance-=1
        if room is None:
            room = []
            self.rooms[agent.location] = room

        if action == "MoveRight" and agent.location < 4:
            agent.location += 1
            
        elif action == "MoveLeft" and agent.location > 0:
            agent.location -= 1
            
        elif action == "Eat" and "Mouse" in room:
            
            if agent.performance >= 3:
                
                room.remove("Mouse")
                agent.performance += 10
        elif action == "Drink" and "Milk" in room:
            
            room.remove("Milk")
            agent.performance += 5
        elif action == "Fight" and "Dog" in room:
            
            if agent.performance >= 10:
                room.remove("Dog")
                
                agent.performance += 20
            else:
                agent.performance -= 10

        if agent.performance <= 0:
            agent.alive = False
            print("Cat died! Performance <= 0")

        if room == []:
            self.rooms[agent.location] = None

        print(f"Cat performance: {agent.performance} Location: {agent.location}")


# ---------------- Main ----------------
if __name__ == "__main__":
    # Random cat example
    cat = Agent(RandomCatProgram(catActions))
    env = CrazyHouse(cat)

    print(f"Initial House: {env.rooms}")
    print(f"Cat starts in room: {cat.location} Performance: {cat.performance}")
    env.run(steps=20)

    # Reflex cat example (uncomment to test)
    # cat = Agent(ReflexCatProgram(catRules))
    # env = CrazyHouse(cat)
    # env.run(steps=20)
