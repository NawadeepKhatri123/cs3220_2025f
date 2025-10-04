import streamlit as st
import random
import time

# --- 1. CORE CONSTANTS ---
# Locations (representing loc_A, loc_B, loc_C, loc_D from src.locations)
LOCATIONS = [
    "Room A (Mail)", 
    "Room B (Donuts)", 
    "Room C (Pizza)", 
    "Room D (Stop)"
]

# --- 2. BASE CLASSES (Simplified from src.thingClass, src.agentClass) ---

class Thing:
    """Base class for all objects in the environment (including agents and recipients)."""
    def __init__(self, name="Thing"):
        self.location = None
        self.name = name

    def __repr__(self):
        return self.name

class Agent(Thing):
    """The base agent class for the delivery person."""
    def __init__(self, program=None, name="Delivery Agent"):
        super().__init__(name)
        self.alive = True
        self.performance = 0 # Starts at 0 as per the original environment comment
        
        if program is None:
            def program(percept):
                return "Go ahead"
        self.program = program

    def is_alive(self):
        return self.alive


# --- 3. RECIPIENT CLASSES (from src.Task3YourClasses) ---

class Student(Thing):
    def __init__(self, name="Student"):
        super().__init__(name)
        self.package_received = False
        self.delivery_item = "pizza"

class ITStaff(Thing):
    def __init__(self, name="IT Staff"):
        super().__init__(name)
        self.package_received = False
        self.delivery_item = "donuts"

class OfficeManager(Thing):
    def __init__(self, name="Office Manager"):
        super().__init__(name)
        self.package_received = False
        self.delivery_item = "mail"


# --- 4. AGENT PROGRAMS ---

# Actions available to the delivery agent
deliveryActions = ['Go ahead', 'Give mail', 'Give donuts', 'Give pizza', 'Stop']

def RandomAgentProgram(actions):
    """Agent that chooses any valid action randomly."""
    return lambda percept: random.choice(actions)

# Rules mapping the perceived state to an action
deliveryRules = {
    "Office Manager": "Give mail",
    "IT Staff": "Give donuts",
    "Student": "Give pizza",
    "Empty Room": "Go ahead",
    "Stop Point": "Stop"
}

def interpret_percept(location, things):
    """Converts the raw percept (location, things) into a simple state string."""
    if location == LOCATIONS[-1]: # The last location is the Stop point
        return "Stop Point"
    
    # Check for recipients (priority order matters for reflex agent)
    if any(isinstance(t, OfficeManager) for t in things):
        return "Office Manager"
    if any(isinstance(t, ITStaff) for t in things):
        return "IT Staff"
    if any(isinstance(t, Student) for t in things):
        return "Student"
    
    # If no one is here, the room is empty
    return "Empty Room"

def DeliveryReflexAgentProgram(rules):
    """A Reflex Agent that chooses an action based on the simplified state."""
    def program(percept):
        location, things = percept
        state = interpret_percept(location, things)
        return rules.get(state, "Go ahead")
    return program


# --- 5. ENVIRONMENT BASE CLASS (Simplified) ---

class BaseEnvironment:
    """The base class for the environment, adapted for single-file use."""
    def __init__(self):
        self.agents = []
        # Stores all things mapped by location string: {"Room A": [Thing1, Thing2], ...}
        self.things = {} 

    def is_done(self):
        # By default, we're done when we can't find a live agent.
        return not any(agent.is_alive() for agent in self.agents)

    def percept(self, agent):
        # Implement in derived classes
        raise NotImplementedError

    def execute_action(self, agent, action, log):
        # Implement in derived classes
        raise NotImplementedError

    def default_location(self, thing):
        # Agent starts at the first location for predictable runs.
        return LOCATIONS[0] 

    def add_thing(self, thing, location=None):
        """Adds a thing to the environment."""
        loc = location if location is not None else self.default_location(thing)
        thing.location = loc
        
        if loc not in self.things:
            self.things[loc] = []
        self.things[loc].append(thing)

        if isinstance(thing, Agent) and thing not in self.agents:
            self.agents.append(thing)

    def delete_thing(self, thing):
        """Removes a thing from the environment."""
        if thing.location in self.things and thing in self.things[thing.location]:
            self.things[thing.location].remove(thing)
            if not self.things[thing.location]:
                del self.things[thing.location]
        
        if thing in self.agents:
            self.agents.remove(thing)

    def list_things_at(self, location, thingClass=None):
        """Returns a list of things at a given location, optionally filtered by class."""
        things = self.things.get(location, [])
        if thingClass:
            return [t for t in things if isinstance(t, thingClass)]
        return things

    def step(self, log):
        """Run the environment for one time step."""
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    percept_data = self.percept(agent)
                    action = agent.program(percept_data)
                    log.append(f"Agent at **{agent.location}** perceives: {self.get_percept_summary(percept_data)}")
                    actions.append((agent, action))
                else:
                    actions.append((agent, None))

            for (agent, action) in actions:
                if action:
                    self.execute_action(agent, action, log)
        else:
            log.append("There is no one here who could work...")

    def run(self, steps=10):
        """Run the Environment for given number of time steps."""
        logs = []
        for step in range(steps):
            if self.is_done():
                logs.append("We can't find a live agent, simulation complete.")
                break
            logs.append(f"\n### Step {step+1}:")
            self.step(logs)
        return logs
    
    def get_percept_summary(self, percept_data):
        """Helper for logging the contents of the room."""
        _, things = percept_data
        if not things:
            return "**Empty**"
        return f"**{', '.join(str(t) for t in things)}**"

# --- 6. COMPANY DELIVERY ENVIRONMENT (from companyenvironment.py) ---

class CompanyDeliveryEnvironment(BaseEnvironment):
    """The specific environment for the delivery simulation."""
    def __init__(self, agent):
        super().__init__()
        self.locations = LOCATIONS
        self.add_recipient_things()
        self.add_thing(agent) # Agent will now start at LOCATIONS[0] via default_location
        self.agent = agent

    def add_recipient_things(self):
        """Adds a single recipient to each relevant room."""
        self.add_thing(OfficeManager(), location=LOCATIONS[0]) # Room A
        self.add_thing(ITStaff(), location=LOCATIONS[1])       # Room B
        self.add_thing(Student(), location=LOCATIONS[2])       # Room C
        # LOCATIONS[3] (Room D) is the stop point and is empty

    def percept(self, agent):
        """Returns location and list of things at that location."""
        return agent.location, self.list_things_at(agent.location)

    def execute_action(self, agent, action, log):
        """Executes the action and updates performance/environment state."""
        current_location = agent.location
        
        # 1. Action: Move
        if action == "Go ahead":
            current_index = self.locations.index(agent.location)
            if current_index < len(self.locations) - 1:
                agent.location = self.locations[current_index + 1]
                log.append(f"Agent chose **Go ahead**. Moved from {current_location} to **{agent.location}** (Perf: {agent.performance}).")
            else:
                log.append(f"Agent chose **Go ahead**. Cannot move past the last location.")

        # 2. Action: Delivery
        elif action in ['Give mail', 'Give donuts', 'Give pizza']:
            
            # Map action to target class and item
            target_map = {
                'Give mail': (OfficeManager, "mail"),
                'Give donuts': (ITStaff, "donuts"),
                'Give pizza': (Student, "pizza")
            }
            TargetClass, item_name = target_map[action]
            
            # Find the recipient at the current location
            recipient = next((t for t in self.list_things_at(current_location) if isinstance(t, TargetClass)), None)

            if recipient:
                agent.performance += 3
                self.delete_thing(recipient) # Remove recipient from environment
                log.append(f"Agent chose **{action}**. Delivered {item_name} to {recipient} (**SUCCESS! +3 Perf**). Total: {agent.performance}.")
            else:
                # Simplified log: just state the failure
                log.append(f"Agent chose **{action}**. Delivery target not found. No change (Perf: {agent.performance}).")

        # 3. Action: Stop
        elif action == 'Stop':
            agent.alive = False
            log.append(f"Agent chose **Stop**. Agent is now inactive. Final Perf: {agent.performance}.")
        
        else:
            log.append(f"Agent chose **{action}**. Action had no recognizable effect (Perf: {agent.performance}).")


# ---------------- 7. STREAMLIT UI (Execution Block) ----------------
st.title("📦 Task 3: Office Delivery Simulation")
st.markdown("Simulates a delivery agent moving through a four-room office to drop off items.")

# Sidebar settings
st.sidebar.header("Agent and Simulation Settings")
agent_choice = st.sidebar.selectbox("Choose Agent Type", ["Delivery Reflex Agent", "Random Agent"])
steps = st.sidebar.slider("Number of steps to run", 5, 20, 10)
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Reflex Agent's Goal:**
1. **Room A:** Deliver **mail** to Office Manager.
2. **Room B:** Deliver **donuts** to IT Staff.
3. **Room C:** Deliver **pizza** to Student.
4. **Room D:** Stop.
""")


# Run simulation button
if st.button("Run Delivery Simulation", type="primary"):
    
    # 1. Initialize Agent
    if agent_choice == "Random Agent":
        agent = Agent(RandomAgentProgram(deliveryActions))
    else:
        agent = Agent(DeliveryReflexAgentProgram(deliveryRules))

    # 2. Initialize Environment
    env = CompanyDeliveryEnvironment(agent)

    # 3. Display Initial State (Simplified)
    st.markdown("---")
    st.subheader("Initial Setup")
    st.write(f"**Agent Type:** **{agent_choice}**")
    st.write(f"**Agent Starting Location:** **{agent.location}** with **{agent.performance}** Performance.")
    
    st.markdown("**Initial Office Layout:**")
    st.markdown(f"- **{LOCATIONS[0]}:** Office Manager")
    st.markdown(f"- **{LOCATIONS[1]}:** IT Staff")
    st.markdown(f"- **{LOCATIONS[2]}:** Student")
    st.markdown(f"- **{LOCATIONS[3]}:** Empty Stop Point")


    # 4. Run Steps and Display Logs
    st.markdown("---")
    st.subheader(f"Simulation Log ({steps} Steps)")
    
    # Run the core logic
    with st.spinner("Running simulation..."):
        all_logs = env.run(steps=steps)

    # Display results
    log_container = st.container(height=400)
    for entry in all_logs:
        log_container.markdown(entry, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Final Summary")
    
    final_status_tag = '✅' if agent.is_alive() else '🛑'
    final_status = '**Active**' if agent.is_alive() else '<span style="color:red; font-weight:bold;">**Stopped/Inactive**</span>'
    
    st.write(f"**Final Performance Score:** **{agent.performance}** (Max possible score is 9)")
    st.write(f"**Final Location:** **{agent.location}**")
    st.markdown(f"**Status:** {final_status_tag} {final_status}", unsafe_allow_html=True)
