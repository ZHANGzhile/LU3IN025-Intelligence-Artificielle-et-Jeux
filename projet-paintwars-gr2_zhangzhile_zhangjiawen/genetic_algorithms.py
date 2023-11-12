# UE IA & JEUX - L3, SU
# TP "comportement réactif"
#
# Nicolas Bredeche
# 2021-03-31

from pyroborobo import Pyroborobo, Controller, AgentObserver, WorldObserver, CircleObject, SquareObject, MovableObject
# from custom.controllers import SimpleController, HungryController
import numpy as np
import random
import math
import paintwars_arena

# =-=-=-=-=-=-=-=-=-= NE RIEN MODIFIER *AVANT* CETTE LIGNE =-=-=-=-=-=-=-=-=-=

param = []
bestParam = []
bestDistance = 0
bestScore = 0
evaluations = 500
population = []
current_evaluations = 0
mu = 5
lambda_ = 20
selected_parents = []

def get_extended_sensors(sensors):
    for key in sensors:
        sensors[key]["distance_to_robot"] = 1.0
        sensors[key]["distance_to_wall"] = 1.0
        if sensors[key]["isRobot"] == True:
            sensors[key]["distance_to_robot"] = sensors[key]["distance"]
        else:
            sensors[key]["distance_to_wall"] = sensors[key]["distance"]
    return sensors

def init_population(mu):
    return [[random.uniform(-1, 1) for _ in range(8)] for _ in range(mu)]

def mutation(individual, mutation_rate):
    mutated = individual.copy()
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[i] += random.uniform(-0.1, 0.1)
            mutated[i] = max(min(mutated[i], 1), -1)
    return mutated

def select(population, scores):
    select = []
    total_score = sum(scores)
    relative_scores = [score / total_score for score in scores]
    cumulative_scores = [sum(relative_scores[:i+1]) for i in range(len(relative_scores))]
    
    for _ in range(mu):
        r = random.random()
        for i in range(len(cumulative_scores)):
            if r <= cumulative_scores[i]:
                select.append(population[i])
                break
    return select
    
def crossover(parent1, parent2):
    child = []
    for i in range(len(parent1)):
        child.append((parent1[i] + parent2[i]) / 2)
    return child

def score(translation, rotation):
    return translation * (1 - abs(rotation))

def step(robotId, sensors):
    global current_evaluations, population, selected_parents, bestParam, bestScore, mu, lambda_, mutation_rate
    
    if len(population) == 0:
        population = init_population(mu)
        for p in population:
           translation = math.tanh(p[0] + p[1] * sensors["sensor_front_left"]["distance"] + p[2] * sensors["sensor_front"]["distance"] + p[3] * sensors["sensor_front_right"]["distance"])
           if translation > 0:
              param = p
              break
        param = population[0]
    else:
        param = population[current_evaluations % lambda_]

    translation = math.tanh(param[0] + param[1] * sensors["sensor_front_left"]["distance"] + param[2] * sensors["sensor_front"]["distance"] + param[3] * sensors["sensor_front_right"]["distance"])
    rotation = math.tanh(param[4] + param[5] * sensors["sensor_front_left"]["distance"] + param[6] * sensors["sensor_front"]["distance"] + param[7] * sensors["sensor_front_right"]["distance"])
    
    current_score = score(translation, rotation)
    if current_score > bestScore:
        bestScore = current_score
        bestParam = param.copy()

    current_evaluations += 1

    
    Scores = [score(math.tanh(individual[0] + individual[1] * sensors["sensor_front_left"]["distance"] + individual[2] * sensors["sensor_front"]["distance"] + individual[3] * sensors["sensor_front_right"]["distance"]), math.tanh(individual[4] + individual[5] * sensors["sensor_front_left"]["distance"] + individual[6] * sensors["sensor_front"]["distance"] + individual[7] * sensors["sensor_front_right"]["distance"])) for individual in population]
    select_parents = select(population, Scores)
    population = []
    for i in range(lambda_):
            parent1 = random.choice(select_parents)
            parent2 = random.choice(select_parents)
            child = crossover(parent1, parent2)
            mutate_child = mutation(child, 0.2)
            population.append(mutate_child)
    translation = math.tanh(param[0] + param[1] * sensors["sensor_front_left"]["distance"] + param[2] * sensors["sensor_front"]["distance"] + param[3] * sensors["sensor_front_right"]["distance"])
    rotation = math.tanh(param[4] + param[5] * sensors["sensor_front_left"]["distance"] + param[6] * sensors["sensor_front"]["distance"] + param[7] * sensors["sensor_front_right"]["distance"])

    return translation, rotation


# =-=-=-=-=-=-=-=-=-= NE RIEN MODIFIER *APRES* CETTE LIGNE =-=-=-=-=-=-=-=-=-=

number_of_robots = 8  # 8 robots identiques placés dans l'arène

arena = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

rob = 0

offset_x = 36
offset_y = 36
edge_width = 28
edge_height = 28


class MyController(Controller):

    def __init__(self, wm):
        super().__init__(wm)

    def reset(self):
        return

    def step(self):

        sensors = {}

        self.get_robot_id_at(0) != -1
        sensors["sensor_left"] = {"distance": self.get_distance_at(0), "isRobot": self.get_robot_id_at(0) != -1}
        sensors["sensor_front_left"] = {"distance": self.get_distance_at(1), "isRobot": self.get_robot_id_at(1) != -1}
        sensors["sensor_front"] = {"distance": self.get_distance_at(2), "isRobot": self.get_robot_id_at(2) != -1}
        sensors["sensor_front_right"] = {"distance": self.get_distance_at(3), "isRobot": self.get_robot_id_at(3) != -1}
        sensors["sensor_right"] = {"distance": self.get_distance_at(4), "isRobot": self.get_robot_id_at(4) != -1}
        sensors["sensor_back_right"] = {"distance": self.get_distance_at(5), "isRobot": self.get_robot_id_at(5) != -1}
        sensors["sensor_back"] = {"distance": self.get_distance_at(6), "isRobot": self.get_robot_id_at(6) != -1}
        sensors["sensor_back_left"] = {"distance": self.get_distance_at(7), "isRobot": self.get_robot_id_at(7) != -1}

        translation, rotation = step(self.id, sensors)

        self.set_translation(translation)
        self.set_rotation(rotation)

    def check(self):
        # print (self.id)
        return True


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class MyAgentObserver(AgentObserver):
    def __init__(self, wm):
        super().__init__(wm)
        self.arena_size = Pyroborobo.get().arena_size

    def reset(self):
        super().reset()
        return

    def step_pre(self):
        super().step_pre()
        return

    def step_post(self):
        super().step_post()
        return


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class MyWorldObserver(WorldObserver):
    def __init__(self, world):
        super().__init__(world)
        rob = Pyroborobo.get()

    def init_pre(self):
        super().init_pre()

    def init_post(self):
        global offset_x, offset_y, edge_width, edge_height, rob

        super().init_post()

        for i in range(len(arena)):
            for j in range(len(arena[0])):
                if arena[i][j] == 1:
                    block = BlockObject()
                    block = rob.add_object(block)
                    block.soft_width = 0
                    block.soft_height = 0
                    block.solid_width = edge_width
                    block.solid_height = edge_height
                    block.set_color(164, 128, 0)
                    block.set_coordinates(offset_x + j * edge_width, offset_y + i * edge_height)
                    retValue = block.can_register()
                    # print("Register block (",block.get_id(),") :", retValue)
                    block.register()
                    block.show()

        counter = 0
        for robot in rob.controllers:
            x = 260 + counter*40
            y = 400
            robot.set_position(x, y)
            counter += 1

    def step_pre(self):
        super().step_pre()

    def step_post(self):
        super().step_post()


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class Tile(SquareObject):  # CircleObject):

    def __init__(self, id=-1, data={}):
        super().__init__(id, data)
        self.owner = "nobody"

    def step(self):
        return

    def is_walked(self, id_):
        return


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class BlockObject(SquareObject):
    def __init__(self, id=-1, data={}):
        super().__init__(id, data)

    def step(self):
        return

    def is_walked(self, id_):
        return


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def main():
    global rob

    rob = Pyroborobo.create(
        "config/paintwars.properties",
        controller_class=MyController,
        world_observer_class=MyWorldObserver,
        #        world_model_class=PyWorldModel,
        agent_observer_class=MyAgentObserver,
        object_class_dict={}
        ,override_conf_dict={"gInitialNumberOfRobots": number_of_robots} # defined in paintwars_config
    )
    
    rob.start()
  
    rob.update(1000000)
    rob.close()
    
if __name__ == "__main__":
    main()
