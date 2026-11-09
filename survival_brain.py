import random
import pickle
import os
import time

class SurvivalEngine:
    MODULE_KEY = 'survival'
    ARCHITECTURE = {'inputs': 3, 'hidden': 6, 'outputs': 1}

    def __init__(self, brn_file="brain.brn"):
        self.brn_file = brn_file
        self.load_brain()

    def load_brain(self):
        if not os.path.exists(self.brn_file):
            raise FileNotFoundError(f"{self.brn_file} not found! Run create_brain.py first.")
        
        with open(self.brn_file, 'rb') as f:
            self.brain_data = pickle.load(f)
        
        # LAZY INITIALIZATION: If this module doesn't exist, create it.
        if self.MODULE_KEY not in self.brain_data['modules']:
            print(f"[SurvivalEngine] Module '{self.MODULE_KEY}' not found. Initializing new lobe...")
            self._init_module()
        
        self.module = self.brain_data['modules'][self.MODULE_KEY]

    def _init_module(self):
        arch = self.ARCHITECTURE
        w1 = [[random.uniform(-1, 1) for _ in range(arch['inputs'])] for _ in range(arch['hidden'])]
        w2 = [[random.uniform(-1, 1) for _ in range(arch['hidden'])] for _ in range(arch['outputs'])]
        self.brain_data['modules'][self.MODULE_KEY] = {'w1': w1, 'w2': w2}
        self.module = self.brain_data['modules'][self.MODULE_KEY]
        self.save_brain()

    def save_brain(self):
        self.brain_data['modules'][self.MODULE_KEY] = self.module
        with open(self.brn_file, 'wb') as f:
            pickle.dump(self.brain_data, f)

    def think(self, inputs):
        hidden = [max(0, sum(i * w for i, w in zip(inputs, w_row))) for w_row in self.module['w1']]
        outputs = [sum(h * w for h, w in zip(hidden, w_row)) for w_row in self.module['w2']]
        return outputs

    def mutate(self, intensity=0.3):
        def mutate_list(lst):
            for i in range(len(lst)):
                if isinstance(lst[i], list): mutate_list(lst[i])
                else:
                    if random.random() < 0.2: lst[i] += random.uniform(-intensity, intensity)
        mutate_list(self.module['w1'])
        mutate_list(self.module['w2'])
        self.save_brain()

if __name__ == "__main__":
    try:
        brain = SurvivalEngine()
    except FileNotFoundError as e:
        print(e); exit()

    hunger, energy, thirst, days = 0.5, 0.5, 0.5, 0
    print("--- SURVIVAL TRAINING ---")
    try:
        while True:
            senses = [hunger, energy, thirst]
            dec = brain.think(senses)[0]
            action = "IDLE"
            if dec < -1.0: action, hunger, energy, thirst = "EAT", hunger-0.3, energy-0.1, thirst+0.05
            elif -1.0 <= dec < -0.1: action, thirst, energy, hunger = "DRINK", thirst-0.3, energy-0.1, hunger+0.05
            elif 0.1 <= dec <= 1.0: action, energy, hunger, thirst = "SLEEP", energy+0.3, hunger+0.1, thirst+0.1
            else: action, hunger, energy, thirst = "IDLE", hunger+0.08, energy-0.08, thirst+0.08
            
            hunger, energy, thirst = max(0, min(1, hunger)), max(0, min(1, energy)), max(0, min(1, thirst))
            print(f"Day {days} | H:{round(hunger,2)} E:{round(energy,2)} T:{round(thirst,2)} | {action}")
            
            if hunger >= 1 or energy <= 0 or thirst >= 1:
                print("💀 DIED. Mutating..."); brain.mutate(); hunger, energy, thirst, days = 0.5, 0.5, 0.5, 0
            else: days += 1
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped. Progress saved.")