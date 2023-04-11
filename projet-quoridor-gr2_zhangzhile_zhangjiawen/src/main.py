# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import copy
import math
import random
import time
from math import inf

import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme








# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'mini-quoridorMap'
    game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main(mode0,mode1):

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)
    init()
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize
    assert nbLignes == nbCols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker les murs)
    lMax=nbLignes-2 
    cMin=2
    cMax=nbCols-2
    depth = 5
   
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
       
           
    # on localise tous les états initiaux (loc du joueur)
    # positions initiales des joueurs
    initStates = [o.get_rowcol() for o in players]
    ligneObjectif = (initStates[1][0],initStates[0][0]) # chaque joueur cherche a atteindre la ligne ou est place l'autre 
    print(ligneObjectif)
    
    # on localise tous les murs
    # sur le layer ramassable    
    walls = [[],[]]
    walls[0] = [o for o in game.layers['ramassable'] if (o.get_rowcol()[0] == 0 or o.get_rowcol()[0] == 1)]  
    walls[1] = [o for o in game.layers['ramassable'] if (o.get_rowcol()[0] == nbLignes-2 or o.get_rowcol()[0] == nbLignes-1)]  
    allWalls = walls[0]+walls[1]
    nbWalls = len(walls[0])
    assert len(walls[0])==len(walls[1]) # les 2 joueurs doivent avoir le mm nombre de murs
    
    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets murs ou joueurs
    #-------------------------------
    
    def wallStates(walls): 
        # donne la liste des coordonnees dez murs
        return [w.get_rowcol() for w in walls]
    
    def playerStates(players):
        # donne la liste des coordonnees dez joueurs
        return [p.get_rowcol() for p in players]

    wall_coords = wallStates(allWalls)
    player_coords = playerStates(players)
    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print("lignes", nbLignes)
    print("colonnes", nbCols)
    print("Trouvé ", nbPlayers, " joueurs avec ", int(nbWalls/2), " murs chacun" )
    print ("Init states:", initStates)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo 
    # 2 joueurs 
    # Joueur 0: place au hasard
    # Joueur 1: A*
    #-------------------------------
    
        
    #-------------------------------
    # On choisit une case objectif au hasard pour chaque joueur
    #-------------------------------
    
    allObjectifs = ([(ligneObjectif[0],i) for i in range(cMin,cMax)],[(ligneObjectif[1],i) for i in range(cMin,cMax)])
    print("Tous les objectifs joueur 0", allObjectifs[0])
    print("Tous les objectifs joueur 1", allObjectifs[1])
    objectifs =  (allObjectifs[0][random.randint(cMin,cMax-3)], allObjectifs[1][random.randint(cMin,cMax-3)])
    print("Objectif joueur 0 choisi au hasard", objectifs[0])
    print("Objectif joueur 1 choisi au hasard", objectifs[1])


    # -------------------------------
    # Fonctions definissant les positions legales et placement de mur aléatoire
    # -------------------------------
    def legal_wall_position(pos):
        row,col = pos
        # une position legale est dans la carte et pas sur un mur deja pose ni sur un joueur
        # attention: pas de test ici qu'il reste un chemin vers l'objectif
        return ((pos not in wallStates(allWalls)) and (pos not in playerStates(players)) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)
    
    def draw_random_wall_location():
        # tire au hasard un couple de position permettant de placer un mur
        while True:
            random_loc = (random.randint(lMin,lMax),random.randint(cMin,cMax))
            if legal_wall_position(random_loc):  
                inc_pos =[(0,1),(0,-1),(1,0),(-1,0)] 
                random.shuffle(inc_pos)
                for w in inc_pos:
                    random_loc_bis = (random_loc[0] + w[0],random_loc[1]+w[1])
                    if legal_wall_position(random_loc_bis):
                        return(random_loc,random_loc_bis)


    ######################################### Alpha-Beta strategie ########################################################


    def court_chemin(state, player):
        g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
        for w in wallStates(allWalls):  # on met False quand murs
            g[w] = False
        for (w1, w2) in state['wall']:
            g[w1] = False
            g[w2] = False
        for i in range(nbLignes):  # on exclut aussi les bordures du plateau
            g[0][i] = False
            g[1][i] = False
            g[nbLignes - 1][i] = False
            g[nbLignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nbLignes - 1] = False
            g[i][nbLignes - 2] = False
        p = ProblemeGrid2D(state['player_positions'][player], objectifs[player], g, 'manhattan')
        path = probleme.astar(p, verbose=False)  # calcule A* par le position maintenant
        return path

    # pour évaluer l’état actuel du jeu
    def evaluation_function(state, player):
        # avantages = avantages_walls(state, player)
        return len(court_chemin(state, 1 - player)) - 1 - (len(court_chemin(state, player)) - 1)

    def est_legal_move(position):
        row, col = position
        # Vérifiez si l’emplacement se trouve dans l’interface du jeu
        if not (lMin <= row <= lMax - 1 and cMin <= col <= cMax - 1):
            return False
        # Vérifiez que l’emplacement n’est pas occupé par un autre joueur
        #   if position in player_positions.values():
        #      return False
        # Vérifiez s’il y a un mur qui le bloque
        for w in wallStates(allWalls):
            if w == position:
                return False

        return True

    def draw_all_wall_location():
        legal_wall_positions = []

        # Traversez tous les emplacements de mur possibles
        for row in range(lMin, lMax + 1):
            for col in range(cMin, cMax + 1):
                current_pos = (row, col)

                # Vérifiez si l’emplacement actuel est légitime
                if legal_wall_position(current_pos):
                    inc_pos = [(0, 1), (0, -1), (1, 0), (-1, 0)]

                    # Traverser les emplacements adjacents
                    for w in inc_pos:
                        neighbor_pos = (current_pos[0] + w[0], current_pos[1] + w[1])

                        # Si l’emplacement du voisin est également légal, ajoutez l’emplacement actuel du mur et l’emplacement du voisin à la liste
                        if legal_wall_position(neighbor_pos):
                            legal_wall_positions.append((current_pos, neighbor_pos))

        return legal_wall_positions

    def peut_placer_wall(wall_pos, state, player):
        ((x1, y1), (x2, y2))= wall_pos
        g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
        for w in wallStates(allWalls):  # on met False quand murs
            g[w] = False
        g[(x1,y1)] = False
        g[(x2,y2)] = False
        for i in range(nbLignes):  # on exclut aussi les bordures du plateau
            g[0][i] = False
            g[1][i] = False
            g[nbLignes - 1][i] = False
            g[nbLignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nbLignes - 1] = False
            g[i][nbLignes - 2] = False

        prob = ProblemeGrid2D(state['player_positions'][player], objectifs[player], g, 'manhattan')
        prob2 = ProblemeGrid2D(state['player_positions'][1-player], objectifs[1-player], g, 'manhattan')
        path = probleme.astar(prob, verbose=False)  # calcule A* par le position maintenant
        path2 =probleme.astar(prob2, verbose=False)
        if path[len(path) - 1] == objectifs[player] and path2[len(path2)-1] == objectifs[1-player]:
            return True
        else:
            return False


    def est_termine(state, player):
        if state['player_positions'][player] == objectifs[player]:
            return True, 200  # retourner une valeur plus grande
        else:
            return False, 0

    def successor_function(state, player):
        player_positions, wall = state['player_positions'], state['wall']
        current_position = player_positions[player]
        successors = []

        # Générez tous les mouvements possibles
        for move in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_position = (current_position[0] + move[0], current_position[1] + move[1])

            if est_legal_move(new_position):
                new_player_positions = player_positions.copy()
                new_player_positions[player] = new_position
                successors.append({'player_positions': new_player_positions, 'wall': wall})
                # print("successor:",successors)
        # Générez tous les emplacements muraux possibles
        if len(walls[player]) >= 2:
            for w in draw_all_wall_location():
                if peut_placer_wall(w, state, player):
                    new_walls = wall.copy()
                    new_walls.append(w)
                    successors.append({'player_positions': player_positions, 'wall': new_walls})
                    # print("successor:",successors)
        return successors

    def alpha_beta_search(state, player, depth, alpha, beta, maximizing_player):
        termine, score = est_termine(state, player)
        if depth == 0 or est_termine(state, player):
            # print("evaluation player",player,":",evaluation_function(state))
            return evaluation_function(state,player) + score
        if maximizing_player:
            value = float('-inf')
            for successor in successor_function(state, 1 - player):
                value = max(value, alpha_beta_search(successor, 1 - player, depth - 1, alpha, beta, False))
                #alpha = max(alpha, value)
                if value >= beta:  # coupe beta, pas la peine d'étendre les autres fils
                    print("coupe beta")
                    return value
                alpha = max(alpha, value)
            return value
        else:
            value = float('inf')
            for successor in successor_function(state, 1 - player):
                value = min(value, alpha_beta_search(successor, 1 - player, depth - 1, alpha, beta, True))
                if value <= alpha:  # coupe alpha, pas la peine d'étendre les autres fils
                    print("coupe alpha")
                    return value
                beta = min(beta, value)
            return value


    # pour trouver le meilleur coup du joueur dans l’état actuel
    def trouve_meilleur_move(state, player, depth):
        if player == 0:
            maximizing_player = True
        else:
            maximizing_player = False
        best_value = float('-inf')
        best_move = None

        for successor in successor_function(state, player):
            # print("state s", successor)
            value = alpha_beta_search(successor, player, depth, float('-inf'), float('inf'), maximizing_player)
            #  print("value:",value)
            if value > best_value:
                best_value = value
                best_move = successor
        print("best move:", best_move)
        return best_move

    ################################################## Fini Alpha-Beta #####################################################



    ################################################ Stratégies 3 (personnel) #####################################################

    # -------------------------------
    # fonction pour trouver un chemin
    # -------------------------------
    def trouve_chemin(joueur):
        g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
        for w in wallStates(allWalls):  # on met False quand murs
            g[w] = False
        for i in range(nbLignes):  # on exclut aussi les bordures du plateau
            g[0][i] = False
            g[1][i] = False
            g[nbLignes - 1][i] = False
            g[nbLignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nbLignes - 1] = False
            g[i][nbLignes - 2] = False
        p = ProblemeGrid2D(playerStates(players)[joueur], objectifs[joueur], g, 'manhattan')
        path = probleme.astar(p, verbose=False)  # calcule A* par le position maintenant
        #print("Chemin trouvé:", path)
        return path



    # -------------------------------
    # fonction pour deplacer
    # -------------------------------
    def deplacer(joueur):
        g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
        for w in wallStates(allWalls):  # on met False quand murs
            g[w] = False
        path = trouve_chemin(joueur)
        (row, col) = path[1]
        players[joueur].set_rowcol(row, col)
        game.mainiteration()


    # -------------------------------
    # fonction pour deposer des murs et verifier s'il déposer un mur à un endroit qui fermerait tout chemin d'un des autres joueurs vers ses objectifs.
    # -------------------------------
    def deposer_mur(joueur, joueur2):
        ((x1, y1), (x2, y2)) = draw_random_wall_location()
        g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
        for w in wallStates(allWalls):  # on met False quand murs
            g[w] = False
        g[(x1, y1)] = False
        g[(x2, y2)] = False
        for i in range(nbLignes):  # on exclut aussi les bordures du plateau
            g[0][i] = False
            g[1][i] = False
            g[nbLignes - 1][i] = False
            g[nbLignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nbLignes - 1] = False
            g[i][nbLignes - 2] = False
        p = ProblemeGrid2D(playerStates(players)[joueur], objectifs[joueur], g, 'manhattan')
        p2 = ProblemeGrid2D(playerStates(players)[joueur2], objectifs[joueur2], g, 'manhattan')
        path = probleme.astar(p, verbose=False)  # calcule A* par le position maintenant
        path2 = probleme.astar(p2, verbose=False)
        if path[len(path) - 1] == objectifs[joueur] and path2[len(path2) - 1] == objectifs[joueur2]:
                if walls[joueur] != 0:
                    walls[joueur][0].set_rowcol(x1, y1)
                    walls[joueur][1].set_rowcol(x2, y2)
                    del (walls[joueur][0])
                    del (walls[joueur][0])
                    game.mainiteration()


    # -------------------------------
    # Joueur joue, le paramètre joueur est le numéro du joueur
    # Stratégies personnel
    # -------------------------------
    def algo_S3(joueur,joueur2,length_chemin,state):
        path = trouve_chemin(joueur)
        #print("path",path)
        length = length_chemin
        if len(walls[joueur]) > 0:
            if len(path) > length:  # on pose les mur pour lui bloquer
                nb_fois = 0
                b = True
                while b:
                    ((x1, y1), (x2, y2)) = draw_random_wall_location()
                    nb_fois += 1
                    g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
                    for (w1, w2) in state['wall']:
                        g[w1] = False
                        g[w2] = False
                    g[(x1, y1)] = False
                    g[(x2, y2)] = False
                    for i in range(nbLignes):  # on exclut aussi les bordures du plateau
                        g[0][i] = False
                        g[1][i] = False
                        g[nbLignes - 1][i] = False
                        g[nbLignes - 2][i] = False
                        g[i][0] = False
                        g[i][1] = False
                        g[i][nbLignes - 1] = False
                        g[i][nbLignes - 2] = False
                    p = ProblemeGrid2D(playerStates(players)[joueur], objectifs[joueur], g, 'manhattan')
                    p2 = ProblemeGrid2D(playerStates(players)[joueur2], objectifs[joueur2], g, 'manhattan')
                    path1 = probleme.astar(p, verbose=False)  # calcule A* par le position maintenant
                    #print("path1", path1)
                    path2 = probleme.astar(p2, verbose=False)
                    #print("path2", path2)
                    if len(path1) < len(path2):
                        if path1[len(path1) - 1] == objectifs[joueur] and path2[len(path2) - 1] == objectifs[joueur2]:
                            if len(walls[joueur]) != 0:
                                walls[joueur][0].set_rowcol(x1, y1)
                                walls[joueur][1].set_rowcol(x2, y2)
                                del (walls[joueur][0])
                                del (walls[joueur][0])
                                game.mainiteration()
                                length = len(path1)
                                b = False

                    if nb_fois >= 2*(nbLignes-1)*(nbCols-3):
                        deplacer(joueur)
                        length = len(path) - 1
                        b = False
            else:
                deplacer(joueur)
                length = len(path) - 1
        else:
            deplacer(joueur)
            length = len(path) -1

        return playerStates(players)[joueur], length


    ################################################# Fini Strategie 3 ########################################################


    ################################################### Strategie Random ##########################################################

    # -------------------------------
    # Joueur joue, le paramètre joueur est le numéro du joueur
    # mode = 1 : déplacer le joueur
    # mode = 0 : deposer un mur
    # mode choisit au hasard
    # -------------------------------

    def joueur_aleatoire(joueur,joueur2):
        mode = random.choice([0, 1])
        # walls[joueur] : les murs de joueur
        if mode == 1 and len(walls[joueur]) != 0:  # poser un mur
            deposer_mur(joueur, joueur2)
        else:  # déplacer le joueur
            deplacer(joueur)
        return playerStates(players)[joueur]

    ################################################### Fini Strategie Random ##########################################################



    ################################################### Strategie S4 ##########################################################

    def legal_move(state, player):
        player_positions = state['player_positions']
        current_position = player_positions[player]
        legal_move = []

        # Générez tous les mouvements possibles
        for move in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_position = (current_position[0] + move[0], current_position[1] + move[1])
            if est_legal_move(new_position):
                legal_move.append(new_position)
        return legal_move

    def deposer_mur1(joueur, state):
        ((x1, y1), (x2, y2)) = draw_random_wall_location()
        g = np.ones((nbLignes, nbCols), dtype=bool)  # une matrice remplie par defaut a True
        for w in wallStates(allWalls):  # on met False quand murs
            g[w] = False
        g[(x1, y1)] = False
        g[(x2, y2)] = False
        for i in range(nbLignes):  # on exclut aussi les bordures du plateau
            g[0][i] = False
            g[1][i] = False
            g[nbLignes - 1][i] = False
            g[nbLignes - 2][i] = False
            g[i][0] = False
            g[i][1] = False
            g[i][nbLignes - 1] = False
            g[i][nbLignes - 2] = False
        p = ProblemeGrid2D(playerStates(players)[joueur], objectifs[joueur], g, 'manhattan')
        p2 = ProblemeGrid2D(playerStates(players)[1-joueur], objectifs[1-joueur], g, 'manhattan')
        path = probleme.astar(p, verbose=False)  # calcule A* par le position maintenant
        path2 = probleme.astar(p2, verbose=False)

        if path[len(path) - 1] == objectifs[joueur] and path2[len(path2) - 1] == objectifs[1-joueur]:
            if len(walls[joueur]) != 0:
                walls[joueur][0].set_rowcol(x1, y1)
                walls[joueur][1].set_rowcol(x2, y2)
                del (walls[joueur][0])
                del (walls[joueur][0])
                new_walls = state['wall'].copy()
                new_walls.append(((x1, y1), (x2, y2)))
                state = {'player_positions': state['player_positions'], 'wall': new_walls,
                         'dernier_move': state['dernier_move']}
                print("new walls est placés par player", player, ":", ((x1, y1), (x2, y2)))
                game.mainiteration()


    def evaluation(state, player):
        d1 = len(court_chemin(state, player))
        d2 = len(court_chemin(state, 1 - player))
        diff_distance = d2 - d1
        wall_reste = len(walls[player])
        res = 0.9 * diff_distance + 0.08 * wall_reste
        print("evaluation res player", player, ":", res)
        return res

    def est_cooperatif(state, player):
        dernier_move = state['dernier_move'][player]
        if dernier_move is not None and dernier_move == 'placer_wall':
            return False
        return True

    def trouve_meilleur_move1(state, player):
        player_positions = state['player_positions']
        meilleur_move = None
        meilleur_score = float('-inf')

        for new_position in legal_move(state, player):
            new_player_positions = player_positions.copy()
            new_player_positions[player] = new_position
            new_state = {'player_positions': new_player_positions, 'wall': state['wall'],
                         'dernier_move': state['dernier_move']}
            score = evaluation(new_state, player)

            if score > meilleur_score:
                meilleur_move = new_position
                meilleur_score = score

        return meilleur_move

    def comportement_adaptatif(state, player):
        diff_eva = evaluation(state, player) - evaluation(state, 1 - player)
        print("diff_eva:", diff_eva)
        if not est_cooperatif(state, 1 - player):
            # Si la valeur imposable ne prévaut pas, adoptez une stratégie de confrontation et érigez un mur
            if diff_eva > 1.7 and len(walls[player]) != 0:
                deposer_mur1(player, state)
                state['dernier_move'][player] = "placer_wall"
            else:
                move = trouve_meilleur_move1(state, player)
                state['player_positions'][player] = move
                print("new position palyer", player, ":", move)
                players[player].set_rowcol(move[0], move[1])
                state['dernier_move'][player] = "se_deplacer"
        else:
            # S’il n’y a pas de grandes lacunes dans les valeurs de la fonction d’évaluation, prenez la coopération
            if -diff_eva <= 1.7 or len(walls[player]) == 0:
                move = trouve_meilleur_move1(state, player)
                state['player_positions'][player] = move
                print("new position palyer", player, ":", move)
                players[player].set_rowcol(move[0], move[1])
                state['dernier_move'][player] = "se_deplacer"
            else:
                deposer_mur1(player, state)
                state['dernier_move'][player] = "placer_wall"


    ################################################### Fini strategie S4 ##########################################################



    ################################################### Test les strategies ##########################################################
    def jouer_joueur_aleatoire():
        for i in range(iterations):

            # on fait bouger le joueur 1 jusqu'à son but
            # en suivant le chemin trouve avec A*

            (row0, col0) = joueur_aleatoire(0)
            (row1, col1) = joueur_aleatoire(1)
            if (row0, col0) == objectifs[0]:
                print("le joueur 0 a atteint son but!")
                break
            if (row1, col1) == objectifs[1]:
                print("le joueur 1 a atteint son but!")
                break

            # mise à jour du pleateau de jeu
            game.mainiteration()



    def jouer_algo_S3():
        len0 = 0
        len1 = 0
        for i in range(iterations):

            # on fait bouger le joueur 1 jusqu'à son but
            # en suivant le chemin trouve avec A*
            if i == 0:
                deposer_mur(0)
                deposer_mur(1)
                len0 = len(trouve_chemin(0))
                len1 = len(trouve_chemin(1))
            else:
                (row0, col0), length = algo_S3(0, 1, len1)
                print("len0", length)
                len0 = length
                (row1, col1), length = algo_S3(1, 0, len0)
                len1 = length
                print("len1", len1)
                if (row0, col0) == objectifs[0]:
                    print("le joueur 0 a atteint son but!")
                    break
                if (row1, col1) == objectifs[1]:
                    print("le joueur 1 a atteint son but!")
                    break

            # mise à jour du pleateau de jeu
            game.mainiteration()

    def jouer_alphaB():
        state = {'player_positions': {0: player_coords[0], 1: player_coords[1]}, 'wall': []}
        W = state['wall']
        P = state['player_positions']
        game_over = False
        for _ in range(iterations):
            if game_over:
                break
            for player in [0, 1]:
                best_move = trouve_meilleur_move(state, player, depth)
                state = best_move
                # print("state:",state)

                # Mettre à jour la position du joueur dans le jeu
                new_position = state['player_positions']
                if new_position[player] != P[player]:
                    P = new_position
                    new_position = state['player_positions'][player]
                    print("new position palyer", player, ":", new_position)
                    players[player].set_rowcol(new_position[0], new_position[1])

                # Mettre à jour les murs dans le jeu
                new_walls = state['wall']
                if new_walls != W:
                    W = new_walls
                    for i, (w1, w2) in enumerate(new_walls):
                        if i == (len(new_walls) - 1):
                            walls[player][0].set_rowcol(w1[0], w1[1])
                            walls[player][1].set_rowcol(w2[0], w2[1])
                            del (walls[player][0])
                            del (walls[player][0])
                            print("new walls est placés par player", player, ":", (w1, w2))
                game.mainiteration()
                termine, score = est_termine(state, player)
                if termine:
                    print("Player", player, "wins!")
                    game_over = True
                    break

    def jouer_cooperation():
        state = {'player_positions': {0: player_coords[0], 1: player_coords[1]}, 'wall': [],
                 'dernier_move': {0: "", 1: ""}}
        game_over = False
        for _ in range(iterations):
            if game_over:
                break
            for player in [0, 1]:
                comportement_adaptatif(state, player)
                game.mainiteration()

                if est_termine(state, player):
                    print("Player", player, "wins!")
                    game_over = True
                    break

    ################################################### Fini test les strategies ##########################################################



    ################################################### La confrontation stratégique ##########################################################
    def contre(mode0,mode1):
        state = {'player_positions': {0: player_coords[0], 1: player_coords[1]}, 'wall':[], 'dernier_move': {0: "", 1: ""}}
        W = state['wall']
        P = state['player_positions']
        for i in range(iterations):
            player = 0
            if mode0 == 1: #alpha-beta
                best_move = trouve_meilleur_move(state, player, depth)
                best_move['dernier_move'] = {}
                if state['player_positions'][0] != best_move['player_positions'][0]:
                    best_move['dernier_move'][0] = "se_deplacer"
                else:
                    best_move['dernier_move'][0] = 'placer_wall'
                state = best_move
                # Mettre à jour la position du joueur dans le jeu
                new_position = state['player_positions']
                if new_position[player] != P[player]:
                    P = new_position
                    new_position = state['player_positions'][player]
                    print("new position palyer", player, ":", new_position)
                    players[player].set_rowcol(new_position[0], new_position[1])

                # Mettre à jour les murs dans le jeu
                new_walls = state['wall']
                if new_walls != W:
                    W = new_walls
                    for i, (w1, w2) in enumerate(new_walls):
                        if i == (len(new_walls) - 1):
                            walls[player][0].set_rowcol(w1[0], w1[1])
                            walls[player][1].set_rowcol(w2[0], w2[1])
                            del (walls[player][0])
                            del (walls[player][0])
                            print("new walls est placés par player", player, ":", (w1, w2))
                game.mainiteration()
                termine, score = est_termine(state, player)

                if termine:
                    print("Player", player, "wins!")
                    return 0

            elif mode0 == 0:# random
                (row, col) = joueur_aleatoire(player,1-player)
                if (row, col) == objectifs[player]:
                    print("le joueur", player, "a atteint son but!")
                    return player
                game.mainiteration()

            elif mode0 == 2: #S4
                comportement_adaptatif(state, player)
                game.mainiteration()

                termine, score = est_termine(state, player)

                if termine:
                    print("Player", player, "wins!")
                    return player



            player = 1

            if mode1 == 0: # random
                (row, col) = joueur_aleatoire(player,1-player)
                if (row, col) == objectifs[player]:
                    print("le joueur", player, "a atteint son but!")
                    return player
                game.mainiteration()

            elif mode1 == 3: # S3
                if i == 0:
                    #time.sleep(1)
                    deposer_mur(1, 0)
                    l = wallStates(allWalls)
                    state['wall'].append((l[len(l) - 2], l[len(l) - 1]))
                else:
                    #time.sleep(1)
                    len1 = len(trouve_chemin(0))
                    l = wallStates(allWalls)
                    (row1, col1), length = algo_S3(player, 1 - player, len1, state)
                    l2 = wallStates(allWalls)
                    if len(l2) > len(l):
                        state['wall'].append((l[len(l) - 2], l[len(l) - 1]))
                    state['player_positions'][1] = (row1, col1)

                    if (row1, col1) == objectifs[1]:
                        print("le joueur 1 a atteint son but!")
                        return player

            elif mode1 == 2:  #S4
                comportement_adaptatif(state, player)
                game.mainiteration()

                termine, score = est_termine(state, player)

                if termine:
                    print("Player", player, "wins!")
                    return player





    ####################################### Calculer le taux de réussite de différentes stratégies ####################################################




    #jouer_joueur_aleatoire()
    #jouer_joueur_S3()
    #jouer_alpha()

    winner = contre(mode0, mode1)
    return winner
    pygame.quit()




if __name__ == '__main__':
    # 0: Random, 1: Alpha-beta, 2: cooperation(miroir) 3: S3(plus court)
    #list mode0: 0,1,2
    #list mode1: 0,2,3
    nb_0 = 0
    nb_1 = 0
    for i in range(30):
        winner = main(1, 0)
        #winner = main(1, 2)
        #winner = main(1, 3)
        if winner == 0:
            nb_0 += 1
        else:
            nb_1 += 1

    print("joueur 0 win : ", nb_0)
    print("joueur 1 win : ", nb_1)
