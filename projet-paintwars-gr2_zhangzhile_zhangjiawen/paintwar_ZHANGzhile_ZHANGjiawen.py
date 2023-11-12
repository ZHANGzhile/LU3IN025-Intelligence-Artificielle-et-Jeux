# Projet "robotique" IA&Jeux 2021
#
# Binome:
#  Prénom Nom: Zhile ZHANG
#  Prénom Nom: Jiawen ZHANG
import random

import braitenberg_avoider

import genetic_algorithms
import subsomption


def get_team_name():
    return "sugfsbks"


def get_extended_sensors(sensors):
    for key in sensors:
        sensors[key]["distance_to_robot"] = 1.0
        sensors[key]["distance_to_wall"] = 1.0
        if sensors[key]["isRobot"] == True:
            sensors[key]["distance_to_robot"] = sensors[key]["distance"]
        else:
            sensors[key]["distance_to_wall"] = sensors[key]["distance"]
    return sensors

def step(robotId, sensors):
    sensors = get_extended_sensors(sensors)
    translation = 1
    rotation = 0
    """
    if sensors["sensor_front"]["isRobot"] == True and sensors["sensor_front"]["isSameTeam"] == False:
        enemy_detected_by_front_sensor = True # exemple de détection d'un robot de l'équipe adversaire (ne sert à rien)
    """
    """
    if sensors["sensor_front_left"]["distance_to_wall"] < 1 or sensors["sensor_front"]["distance_to_wall"] < 1:
        rotation = 0.6 #rotation vers la droite
        return translation, rotation
    elif sensors["sensor_front_right"]["distance_to_wall"] < 1:
        rotation = -0.6 # rotation vers la gauche
        return translation, rotation
    """

    if sensors["sensor_front_left"]["distance_to_wall"] < 1 or sensors["sensor_front"]["distance_to_wall"] < 1 or sensors["sensor_front_right"]["distance_to_wall"] < 1:
        return step_hateWall(robotId,sensors)

    if sensors["sensor_front"]["isSameTeam"] == True or sensors["sensor_front_left"]["isSameTeam"] == True or sensors["sensor_front_right"]["isSameTeam"] == True:
        return step_hateBot(robotId,sensors)

    if sensors["sensor_front"]["isSameTeam"] == False :
        if sensors["sensor_front_left"]["distance_to_wall"] < 1 or sensors["sensor_front_right"]["distance_to_wall"] < 1 or sensors["sensor_front"]["distance_to_wall"] < 1:
            return step_hateWall(robotId,sensors)
        """
        if (sensors["sensor_front"]["isRobot"] or sensors["sensor_front_left"]["isRobot"] or sensors["sensor_front_right"]["isRobot"]) and (not sensors["sensor_front_left"]["isSameTeam"] and not sensors["sensor_front_right"]["isSameTeam"] and not sensors["sensor_front"]["isSameTeam"]):
            #translation = 1 * sensors["sensor_front"]["distance_to_robot"]
            #rotation = (1) * sensors["sensor_front_left"]["distance"] + (-1) * sensors["sensor_front_right"]["distance"]
            #return translation, rotation
            return braitenberg_loveBot.step(robotId, sensors)
        if sensors["sensor_front"]["isRobot"] and not sensors["sensor_front"]["isSameTeam"]:
            return braitenberg_loveBot.step(robotId, sensors)
        elif sensors["sensor_front_left"]["isRobot"] and not sensors["sensor_front_left"]["isSameTeam"]:
            translation = 1 * sensors["sensor_front_left"]["distance_to_robot"]
            rotation = (1) * sensors["sensor_front"]["distance"] + (-1) * sensors["sensor_front_right"]["distance"]
            return translation, rotation
        elif sensors["sensor_front_right"]["isRobot"] and not sensors["sensor_front_right"]["isSameTeam"]:
            translation = 1 * sensors["sensor_front_right"]["distance_to_robot"]
            rotation = (1) * sensors["sensor_front"]["distance"] + (-1) * sensors["sensor_front_left"]["distance"]
            return translation, rotation
        """
        if (sensors["sensor_front"]["isRobot"] or sensors["sensor_front_left"]["isRobot"] or sensors["sensor_front_right"]["isRobot"]) and \
                (not sensors["sensor_front_left"]["isSameTeam"] and not sensors["sensor_front_right"]["isSameTeam"] and not sensors["sensor_front"]["isSameTeam"]):
            return step_loveBot(robotId,sensors)

    return translation, rotation


def step_hateBot(robotId, sensors): # <<<<<<<<<------- fonction à modifier pour le TP1

    # sensors: dictionnaire contenant toutes les informations senseurs
    # Chaque senseur renvoie:
    #   la distance à l'obstacle (entre 0  et 1, distance max)
    #   s'il s'agit d'un robot ou non
    #   la distance au robot (= 1.0 s'il n'y a pas de robot)
    #   la distance au mur (= 1.0 s'il n'y a pas de robot)
    # cf. exemple ci-dessous

    # récupération des senseurs

    sensors = get_extended_sensors(sensors)
    print (
        "[robot #",robotId,"] senseur frontal: (distance à l'obstacle =",sensors["sensor_front"]["distance"],")",
        "(robot =",sensors["sensor_front"]["isRobot"],")",
        "(distance_to_wall =", sensors["sensor_front"]["distance_to_wall"],")", # renvoie 1.0 si ce n'est pas un mur
        "(distance_to_robot =", sensors["sensor_front"]["distance_to_robot"],")"  # renvoie 1.0 si ce n'est pas un robot
    )

    # contrôle moteur. Ecrivez votre comportement de Braitenberg ci-dessous.
    # il est possible de répondre à toutes les questions en utilisant seulement:
    #   sensors["sensor_front"]["distance_to_wall"]
    #   sensors["sensor_front"]["distance_to_robot"]
    #   sensors["sensor_front_left"]["distance_to_wall"]
    #   sensors["sensor_front_left"]["distance_to_robot"]
    #   sensors["sensor_front_right"]["distance_to_wall"]
    #   sensors["sensor_front_right"]["distance_to_robot"]

    translation = 1 * sensors["sensor_front"]["distance_to_robot"]
    rotation = (random.uniform(-2,-1)) * sensors["sensor_front_left"]["distance_to_robot"] + (1) * sensors["sensor_front_right"]["distance_to_robot"]

    # limite les valeurs de sortie entre -1 et +1
    translation = max(-1, min(translation,1))
    rotation = max(-1, min(rotation, 1))

    return translation, rotation

def step_hateWall(robotId, sensors): # <<<<<<<<<------- fonction à modifier pour le TP1

    # sensors: dictionnaire contenant toutes les informations senseurs
    # Chaque senseur renvoie:
    #   la distance à l'obstacle (entre 0  et 1, distance max)
    #   s'il s'agit d'un robot ou non
    #   la distance au robot (= 1.0 s'il n'y a pas de robot)
    #   la distance au mur (= 1.0 s'il n'y a pas de robot)
    # cf. exemple ci-dessous

    # récupération des senseurs

    sensors = get_extended_sensors(sensors)
    print (
        "[robot #",robotId,"] senseur frontal: (distance à l'obstacle =",sensors["sensor_front"]["distance"],")",
        "(robot =",sensors["sensor_front"]["isRobot"],")",
        "(distance_to_wall =", sensors["sensor_front"]["distance_to_wall"],")", # renvoie 1.0 si ce n'est pas un mur
        "(distance_to_robot =", sensors["sensor_front"]["distance_to_robot"],")"  # renvoie 1.0 si ce n'est pas un robot
    )

    # contrôle moteur. Ecrivez votre comportement de Braitenberg ci-dessous.
    # il est possible de répondre à toutes les questions en utilisant seulement:
    #   sensors["sensor_front"]["distance_to_wall"]
    #   sensors["sensor_front"]["distance_to_robot"]
    #   sensors["sensor_front_left"]["distance_to_wall"]
    #   sensors["sensor_front_left"]["distance_to_robot"]
    #   sensors["sensor_front_right"]["distance_to_wall"]
    #   sensors["sensor_front_right"]["distance_to_robot"]

    translation = 1 * sensors["sensor_front"]["distance_to_wall"]
    rotation = (random.uniform(-2, -1)) * sensors["sensor_front_left"]["distance_to_wall"] + (random.uniform(1, 2)) * sensors["sensor_front_right"]["distance_to_wall"]

    # limite les valeurs de sortie entre -1 et +1
    translation = max(-1, min(translation,1))
    rotation = max(-1, min(rotation, 1))
    print("tr",translation,"ro",rotation)
    return translation, rotation

def step_loveBot(robotId, sensors): # <<<<<<<<<------- fonction à modifier pour le TP1

    # sensors: dictionnaire contenant toutes les informations senseurs
    # Chaque senseur renvoie:
    #   la distance à l'obstacle (entre 0  et 1, distance max)
    #   s'il s'agit d'un robot ou non
    #   la distance au robot (= 1.0 s'il n'y a pas de robot)
    #   la distance au mur (= 1.0 s'il n'y a pas de robot)
    # cf. exemple ci-dessous

    # récupération des senseurs

    sensors = get_extended_sensors(sensors)
    print (
        "[robot #",robotId,"] senseur frontal: (distance à l'obstacle =",sensors["sensor_front"]["distance"],")",
        "(robot =",sensors["sensor_front"]["isRobot"],")",
        "(distance_to_wall =", sensors["sensor_front"]["distance_to_wall"],")", # renvoie 1.0 si ce n'est pas un mur
        "(distance_to_robot =", sensors["sensor_front"]["distance_to_robot"],")"  # renvoie 1.0 si ce n'est pas un robot
    )

    # contrôle moteur. Ecrivez votre comportement de Braitenberg ci-dessous.
    # il est possible de répondre à toutes les questions en utilisant seulement:
    #   sensors["sensor_front"]["distance_to_wall"]
    #   sensors["sensor_front"]["distance_to_robot"]
    #   sensors["sensor_front_left"]["distance_to_wall"]
    #   sensors["sensor_front_left"]["distance_to_robot"]
    #   sensors["sensor_front_right"]["distance_to_wall"]
    #   sensors["sensor_front_right"]["distance_to_robot"]

    translation = 1 * sensors["sensor_front"]["distance_to_robot"]
    rotation = (1) * sensors["sensor_front_left"]["distance"] + (-1) * sensors["sensor_front_right"]["distance"]

    # limite les valeurs de sortie entre -1 et +1
    translation = max(-1, min(translation,1))
    rotation = max(-1, min(rotation, 1))

    return translation, rotation



