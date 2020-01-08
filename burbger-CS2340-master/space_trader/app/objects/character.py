from math import sqrt
from random import choice as randchoice
from random import randint
from .universe import Universe
from .borg import Borg
from .ship import Ship
from .ship_types import SHIP_TYPES


DEFAULT_SKILLS = {
    'pilot': 3,
    'fighter': 3,
    'merchant': 3,
    'engineer': 3
}


# Player calls this method when attempting to travel,
# it calculates the fuel cost based on pilot skill and distance
def get_fuel_cost(character, new_location):
    skills = character.skills
    curr_location = character.location
    x_1 = curr_location.position[0]
    x_2 = new_location.position[0]
    y_1 = curr_location.position[1]
    y_2 = new_location.position[1]
    # using distance formula to calculate the distance
    distance = sqrt(((x_2 - x_1) ** 2) + ((y_2 - y_1) ** 2))
    # fuel cost is distance times (1 / pilot skill)
    fuel_needed = distance * (1 / (skills['pilot'] + 1))
    return fuel_needed


class Character:
    """
    A representation of some type of individual in the game.

    Such an individual has a set of important characteristics that are used in
    interactions between it and its peers including skills, money, and location.
    """
    _shared_state = {}

    def __init__(
            self,
            name='Pilot',
            skills=DEFAULT_SKILLS.copy(),
            money=500,
            location=None
    ):
        self._name = name
        self._skills = skills
        self._money = money
        self._location = location
        self._last_location = None
        self._ship = Ship(randchoice(SHIP_TYPES))

    def set_skill(self, skill_name, value):
        if not isinstance(skill_name, str):
            raise TypeError(f"Type of skill name{type(skill_name)} is not str")
        if not skill_name in self._skills:
            raise ValueError(f"Invalid skill {skill_name}")
        self._skills[skill_name] = value

    def travel(self, new_location):
        fuel_needed = get_fuel_cost(self, new_location)
        if self._ship.curr_fuel > fuel_needed:
            self._ship.curr_fuel = self._ship.curr_fuel - fuel_needed
            self.location = new_location
            return True
        return False

    def go_back(self):
        self._location = self._last_location

    @property
    def name(self):
        return self._name

    @property
    def skills(self):
        return self._skills

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, amount):
        if amount < 0:
            raise ValueError("Insufficient funds")
        self._money = amount

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, new_location):
        if new_location not in Universe().regions:
            raise AttributeError("Invalid location")

        self._last_location = self._location
        self._location = new_location

    @property
    def ship(self):
        return self._ship

    @ship.setter
    def ship(self, new_ship):
        if not isinstance(new_ship, Ship):
            raise TypeError("Invalid ship")

        self._ship = new_ship


class Player(Borg, Character):
    """
    The Player is a Character that has only one instance.

    The Character class is instantiable, but is meant for characters that are
    less unique than the Player. There is only one Player.

    It also includes fields and methods for encounters, which are interactions
    specific to the Player - no other Character can get an encounter.
    """
    _shared_state = {}

    def __init__(self): # pylint: disable=super-init-not-called
        Borg.__init__(self)

    @classmethod
    def new(cls, name, skills, money, location):
        # pylint: disable=attribute-defined-outside-init,protected-access
        player = cls()
        player._encounter = None
        player._won = False
        player._lost = False
        player._karma = 0
        Character.__init__(player, name, skills, money, location)

    def change_health(self, amt):
        # pylint: disable=attribute-defined-outside-init
        self._ship.curr_health += amt
        if self._ship.curr_health <= 0:
            self._lost = True
            return False
        return True

    def hurt(self, amt):
        return self.change_health(-amt)

    def kill(self):
        self.hurt(self._ship.curr_health)

    def heal(self, amt):
        return self.change_health(amt)

    def resurrect(self):
        # pylint: disable=attribute-defined-outside-init
        self.heal(self._ship.health)
        self._lost = False

    def buy(self, item, amt=1):
        # pylint: disable=attribute-defined-outside-init
        marketplace = self.location.marketplace
        price = marketplace.prices[item]
        if self._money < price:
            print("Insufficient funds")
            return [False, "Insufficient funds"]

        if self._ship.curr_space < amt:
            print("Insufficient space")
            return [False, "Insufficient cargo space"]

        if not marketplace.change_stock(item, -amt):
            print("Insufficient stock")
            return [False, "Not enough market stock"]

        if marketplace.has_winning_item and marketplace.winning_item == item:
            print("Player wins!")
            self._won = True

        self._ship.change_cargo(item, amt)
        self._money -= price
        return [True]

    def sell(self, item, amt=1):
        marketplace = self.location.marketplace
        skill_level = self._skills['merchant']
        karma_modifier = min(max(self._karma/50, -0.5), 0.5)
        price = round(min(marketplace.prices[item] * (0.5 + (skill_level / 20))
                          * (1 + karma_modifier), marketplace.prices[item]))
        if not self._ship.change_cargo(item, -amt):
            return False

        marketplace.change_stock(item, amt)
        self._money += price
        return True

    def encounter_start(self, npc, amount, item):
        # pylint: disable=attribute-defined-outside-init
        if not isinstance(npc, Character):
            raise TypeError("Cannot enter encounter with non-Character")
        if self.in_encounter:
            raise RuntimeError("Cannot enter encounter when in encounter")
        self._encounter = Encounter(self, npc, amount, item)

    def encounter_end(self):
        # pylint: disable=attribute-defined-outside-init
        self._encounter = None

    @property
    def in_encounter(self):
        return self._encounter is not None

    @property
    def encounter(self):
        return self._encounter

    @property
    def won(self):
        return self._won

    @property
    def lost(self):
        return self._lost

    @property
    def karma(self):
        return self._karma

    @karma.setter
    def karma(self, amt):
        self._karma = int(amt)

class Encounter:
    def __init__(self, player, npc, quantity, item):
        self._player = player
        self._npc = npc
        self._npc_type = npc.name
        self._quantity = quantity
        self._item = item
        self._negotiated = False

    def pay(self):
        success = True
        if self._npc_type == "bandit":
            if self._player.money > self._quantity:
                self._player.money -= self._quantity
                success = 2
            elif self._player.ship.curr_space < self._player.ship.cargo_space:
                self._player.ship.clear_cargo()
                success = 1
            else:
                self._player.hurt(self._npc.skills['fighter'])
                success = 0
        elif self._npc_type == "trader":
            if self._player.money > self._quantity:
                self._player.ship.change_cargo(
                    self._item,
                    self._npc.ship.curr_cargo[self._item]['amt']
                )
                self._player.money -= self._quantity
            else:
                return False
        elif self._npc_type == "police":
            self._player.karma += 1
            self._player.ship.change_cargo(self._item, -self._quantity)
        self._player.encounter_end()
        return success

    def leave(self):
        success = True
        if self._npc_type == "bandit":
            if not self._player.skills['pilot'] > self._npc.skills['pilot']:
                self._player.money = 0
                self._player.hurt(self._npc.skills['fighter'])
                success = False
            self._player.go_back()
        elif self._npc_type == "police":
            self._player.karma -= 1
            if not self._player.skills['pilot'] > self._npc.skills['pilot']:
                self._player.money -= min(self._player.money, randint(100, 300))
                self._player.hurt(self._npc.skills['fighter'])
                self._player.ship.change_cargo(self._item, -self._quantity)
                success = False
            self._player.go_back()

        self._player.encounter_end()
        return success

    def fight(self):
        success = True
        if self._npc_type == "bandit":
            self._player.karma += 1
            if self._player.skills['fighter'] > self._npc.skills['fighter']:
                self._player.money += self._npc.money
            else:
                self._player.money = 0
                self._player.hurt(self._npc.skills['fighter'])
                success = False
        elif self._npc_type == "trader":
            self._player.karma -= 2
            if self._player.skills['fighter'] > self._npc.skills['fighter']:
                self._player.ship.change_cargo(
                    self._item,
                    self._npc.ship.curr_cargo[self._item]['amt']
                )
            else:
                self._player.hurt(self._npc.skills['fighter'])
                success = False
        elif self._npc_type == "police":
            self._player.karma -= 1
            if not self._player.skills['fighter'] > self._npc.skills['fighter']:
                self._player.money -= min(self._player.money, randint(100, 300))
                self._player.hurt(self._npc.skills['fighter'])
                self._player.ship.change_cargo(self._item, -self._quantity)
                self._player.go_back()
                success = False

        self._player.encounter_end()
        return success

    def negotiate(self):
        # pylint: disable=attribute-defined-outside-init
        success = False
        if self._npc_type == "trader" and not self._negotiated:
            if self._player.skills['merchant'] > self._npc.skills['merchant']:
                self._quantity = round(self._quantity / 2)
                success = True
            else:
                self._quantity *= 2
        self._negotiated = True
        return success

    @property
    def npc_type(self):
        return self._npc_type

    @property
    def npc(self):
        return self._npc

    @property
    def quantity(self):
        return self._quantity

    @property
    def item(self):
        return self._item if self._npc_type != "bandit" else ""

    @property
    def negotiated(self):
        return self._negotiated
