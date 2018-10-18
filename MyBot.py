#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
from hlt.game_map import MapCell

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging
# kittens
def intendMove(ship, direction, override=False):
    sourceCell = game_map[ship.position]
    targetCell = game_map[ship.position.directional_offset(direction)]
    has_enough_halite = ship.halite_amount >= (sourceCell.halite_amount * 0.1)
    logging.warning("Ship " + str(ship.id) + " is currently at " + str(ship.position) + " and will move to " + str(targetCell) + " which is_occupied " + str(targetCell.is_occupied) + " and has_structure " + str(targetCell.has_structure) + " and ship halite is " + str(ship.halite_amount) + " and source cell halite is " + str(sourceCell.halite_amount) + " and has_enough_halite " + str(has_enough_halite) + " and OVERRIDE is " + str(override) + " and WILL I EXECUTE? " + str(override or (not targetCell.is_occupied and not targetCell.has_structure and has_enough_halite)))
    if override or (not targetCell.is_occupied and not targetCell.has_structure and has_enough_halite):
        game_map[ship.position].mark_safe()
        game_map[ship.position.directional_offset(direction)].mark_unsafe(ship)
        logging.warning("Executing: " + str(ship.move(direction)))
        return ship.move(direction)
    logging.warning("Executing: " + str(ship.stay_still()))
    return ship.stay_still()
    

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("PingueBot_v1")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    for ship in me.get_ships():
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if ship.halite_amount > 900:
            naive_target = game_map.naive_navigate(ship, me.shipyard.position)
            intendedMove=intendMove(ship, naive_target, True)
            command_queue.append(intendedMove)
        else:
            if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
                collision_free_move = intendMove(ship, random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ]))
                command_queue.append(collision_free_move)
            else:
                command_queue.append(ship.stay_still())

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    logging.info(command_queue)
    game.end_turn(command_queue)

