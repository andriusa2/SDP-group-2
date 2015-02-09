__author__ = 'samdavies'
from lib.strategy.attacker1 import Attacker1
from lib.world.world_state import WorldState, Zone


def milestone2():
    boundries = [47, 106, 165, 212]

    vision = None
    actual_robot = None
    world = WorldState()

    # set the initial state
    vision.update_world_state()
    # set the boundries
    world.set_zone_boundaries(boundries)

    # this is our chosen strategy
    attacker1 = Attacker1(world, Zone.L_ATT, actual_robot)

    while True:
        vision.update_world_state()
        attacker1.act()


if __name__ == '__main__':
    milestone2()



