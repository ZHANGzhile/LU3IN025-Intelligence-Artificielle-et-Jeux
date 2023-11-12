# Nicolas
# 2021-03-31
import paintwar_ZHANGzhile_ZHANGjiawen
# Arena
import paintwars_arena
import paintwars_arena_gr2
get_arena = paintwars_arena_gr2.get_arena
arenaIndexSelector = 0 # numéro de l'arène, entre 0 et 4

# Starting position
invertStartingPosition = False # True: red commence à gauche. Sinon, commence à droite.

# Red team
import paintwars_team_challenger # importer votre code
get_name_red_team = paintwars_team_challenger.get_team_name# mettre ici votre fonction get_team_name
step_red_team = paintwars_team_challenger.step_follow# mettre ici votre fonction step
#step_red_team = paintwars_team_challenger.step_genetic
# Blue team
import paintwars_team_champion as paintwars_team_champion
get_name_blue_team = paintwars_team_champion.get_team_name
step_blue_team = paintwars_team_champion.step

# Simulation mode: realtime=0, fast=1, super_fast_no_render=2
simulation_mode = 0
