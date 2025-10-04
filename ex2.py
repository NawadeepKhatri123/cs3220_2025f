import random

# --- 1. Base Agent and Environment ---

class Agent:
    """Represents a basic intelligent agent."""
    def __init__(self, program=None):
        self.alive = True
        self.performance = 5
        self.location = None
        self.program = program

class Environment:
    """Represents the abstract environment."""
    def __init__(self):
        self.agents = []
        self.rooms = [] # Added for clarity in base class

    def percept(self, agent):
        raise NotImplementedError

    def execute_action(self, agent, action):
        raise NotImplementedError

    def is_done(self):
        """Check if all agents are dead."""
        return not any(agent.alive for agent in self.agents)

    def step(self):
        """Executes one step of the simulation."""
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    percept = self.percept(agent)
                    # The agent's program decides the action based on the percept
                    action = agent.program(percept) 
                    print(f"Cat sees {percept}, chooses {action}")
                    actions.append((agent, action))
                else:
                    actions.append((agent, None))

            for (agent, action) in actions:
                if action:
                    self.execute_action(agent, action)

    def run(self, steps=10):
        """Runs the simulation for a fixed number of steps or until all food is consumed."""
        for i in range(steps):
            if self.is_done():
                print("Game Over early.")
                break
            print(f"\nStep {i+1}:")
            self.step()
            
            # Check for total food consumption
            if all(not room for room in self.rooms):
                print("\nAll food consumed. Simulation ends.")
                break
        
        if not self.is_done() and i == steps - 1:
            print("\nSimulation reached max steps.")


# --- 1. Implement Food Base and Derived Classes ---

class Food:
    """Base class for food items. Weight is required for initialization."""
    # FIX: Corrected the constructor spelling
    def __init__(self, weight): 
        self.weight = weight
        self.calories = 0
        self.type = "GenericFood"

class Milk(Food):
    """Milk subclass with specific calorie count."""
    CALORIES = 15
    # FIX: Correctly call parent constructor and ensure spelling
    def __init__(self, weight):
        super().__init__(weight) 
        self.calories = self.CALORIES
        self.type = "Milk"

class Sausage(Food):
    """Sausage subclass with specific calorie count."""
    CALORIES = 25
    # FIX: Correctly call parent constructor and ensure spelling
    def __init__(self, weight):
        super().__init__(weight)
        self.calories = self.CALORIES
        self.type = "Sausage"

# --- 2. Implement Agent-Cat ---

class Cat(Agent):
    """The Cat agent, specialized for consuming food."""
    def __init__(self, program=None):
        super().__init__(program)

    def consume(self, food_instance):
        """Processes food consumption and updates performance."""
        if isinstance(food_instance, Milk):
            # Performance changes: calories + weight
            perf_change = food_instance.calories + food_instance.weight
            self.performance += perf_change
            print(f"Cat drank Milk (W:{food_instance.weight} C:{food_instance.calories}). Perf +{perf_change}")
            return True
        elif isinstance(food_instance, Sausage):
            # Performance changes: (calories * 2) - (weight // 2)
            perf_change = (food_instance.calories * 2) - (food_instance.weight // 2)
            self.performance += perf_change
            print(f"Cat ate Sausage (W:{food_instance.weight} C:{food_instance.calories}). Perf changes: +{food_instance.calories * 2} -{food_instance.weight // 2} (Net: {perf_change})")
            return True
        else:
            print("Cat tried to consume an unknown item.")
            return False

# --- 3. & 4. Implement Cat-Friendly-House Environment ---

class CatFriendlyHouse(Environment):
    """The 2-room environment where food is placed randomly."""
    def __init__(self, cat, food_items):
        super().__init__()
        self.rooms = [[], []] # Rooms 0 and 1
        self.add_agent(cat)
        
        # Place items in random, but not necessarily different, rooms (as per original logic)
        self.place_food(food_items)
        
        # Place the Cat in a random room
        cat.location = random.randint(0, 1)

    def add_agent(self, agent):
        if agent not in self.agents:
            self.agents.append(agent)

    def place_food(self, items):
        """Places two food items in two different rooms (indices 0 and 1)."""
        if len(items) != 2:
            raise ValueError("Exactly two food items required.")
        
        # Choose two different random rooms
        room_indices = random.sample([0, 1], 2)
        
        # Place item 1 in the first chosen room
        self.rooms[room_indices[0]].append(items[0])
        # Place item 2 in the second chosen room
        self.rooms[room_indices[1]].append(items[1])

    def percept(self, agent):
        """Returns the Cat's current percept based on room content."""
        room_content = self.rooms[agent.location]
        if not room_content:
            return 'Empty'
        
        # Priority check for the type of food
        if any(isinstance(item, Milk) for item in room_content):
            return 'MilkHere'
        if any(isinstance(item, Sausage) for item in room_content):
            return 'SausageHere'
        
        return 'Unknown'

    def execute_action(self, agent, action):
        """
        Executes the Cat's action and updates performance.
        Includes universal -1 cost per action.
        """
        room_index = agent.location
        room = self.rooms[room_index]
        initial_perf = agent.performance
        
        # Flag to prevent applying the universal -1 cost on top of a consumption reward/penalty
        is_consumption_action = False
        
        # 1. Handle Movement Actions
        if action == "MoveRight":
            if room_index < 1:
                agent.location += 1
            # Universal -1 cost applied below

        elif action == "MoveLeft":
            if room_index > 0:
                agent.location -= 1
            # Universal -1 cost applied below
            
        # 2. Handle Consumption Actions
        elif action == "Drink":
            is_consumption_action = True
            milk_instance = next((item for item in room if isinstance(item, Milk)), None)
            if milk_instance:
                agent.consume(milk_instance) # Consumption updates performance (+reward)
                room.remove(milk_instance)
            else:
                agent.performance -= 1 # Penalty for wrong action/no item

        elif action == "Eat":
            is_consumption_action = True
            sausage_instance = next((item for item in room if isinstance(item, Sausage)), None)
            if sausage_instance:
                agent.consume(sausage_instance) # Consumption updates performance (+reward)
                room.remove(sausage_instance)
            else:
                agent.performance -= 1 # Penalty for wrong action/no item

        # 3. Universal -1 Performance Cost for non-consumption actions (movement, invalid move)
        if not is_consumption_action:
             agent.performance -= 1

        # Check for death
        if agent.performance <= 0:
            agent.alive = False
            print("Cat died! Performance <= 0")

        # Status update
        perf_delta = agent.performance - initial_perf
        print(f"Cat's performance: {agent.performance} ({perf_delta:+}). Location: {agent.location}.")
        

# --- 9. Reflex-Random Hybrid Program ---

reflexRules = {
    'MilkHere': 'Drink',
    'SausageHere': 'Eat',
}

def ReflexRandomCatProgram(rules):
    """
    Program that uses fixed rules for food, and moves randomly when the room is empty.
    """
    def program(percept):
        # 1. Check for immediate food action (Highest priority)
        action = rules.get(percept)
        if action:
            return action
        
        # 2. If the room is empty, choose to move randomly
        if percept == 'Empty':
            # This is the desired random movement
            return random.choice(['MoveRight', 'MoveLeft'])
        
        # Fallback for 'Unknown' or other percepts
        return 'MoveRight'
        
    return program

# --- 10. Run the Simulation ---

if __name__ == "__main__":
    # Setup
    # random.seed(42) # Commented out to allow for truly random, varying results on each run.
    
    # Create Food instances (will now work due to fixed __init__)
    milk = Milk(weight=2)
    sausage = Sausage(weight=8)
    
    food_items = [milk, sausage]

    # Create the Agent-Cat with the fixed reflex program
    cat_program = ReflexRandomCatProgram(reflexRules)
    cat = Cat(cat_program)

    # Create the Environment
    env = CatFriendlyHouse(cat, food_items)

    print("-" * 40)
    print("Cat-Friendly-House Simulation (Fixed Constructor, Universal -1 Cost)")
    print("-" * 40)
    
    # Initial state summary
    room_contents = {i: [item.type for item in room] for i, room in enumerate(env.rooms)}
    print(f"Initial House Rooms (Content): Room 0: {room_contents[0]}, Room 1: {room_contents[1]}")
    print(f"Cat starts in Room: {cat.location}. Performance: {cat.performance}")
    
    # Run the simulation
    env.run(steps=10)
    
    print("-" * 40)
    print(f"Final Cat Status: Alive={cat.alive}, Performance={cat.performance}")
