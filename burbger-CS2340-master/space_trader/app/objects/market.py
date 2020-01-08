from random import choice as randchoice
from random import randint
from .items import ITEMS, get_item_by_name, create_item
from .techlevel import TechLevel

# hack hack hack
def keyify(some_dict):
    return some_dict['name']

class Marketplace:
    # creates a marketplace depending on the TechLevel
    def __init__(self, tech_level):
        self._prices = dict()
        self._tech_level = TechLevel(tech_level)
        self.calc_prices()
        self._stock = dict()
        self._fuel_price = 8 - tech_level
        self._repair_price = (8 - tech_level) * 3
        self._winning_item = ""
        for _ in range(randint(2, 4)):
            # choose a random tech level lower than or equal to ours
            item_level = ITEMS[TechLevel(randint(0, tech_level.value))]
            # choose a random item from that tech level
            item = randchoice(item_level)
            quantity = randint(5, 10)
            key = keyify(item)
            if key in self._stock:
                self._stock[key]['amt'] += quantity
            else:
                self._stock[key] = dict()
                self._stock[key]['amt'] = quantity
                self._stock[key]['item'] = item

    def calc_prices(self):
        for tech_level in ITEMS:
            for item in ITEMS[tech_level]:
                key = keyify(item)
                self._prices[key] = self.calc_price(item)

    def calc_price(self, item):
        tech_diff = abs(self._tech_level - item['tech_level'])
        return item['price'] * (1 + (tech_diff * 10 / 6))

    def change_stock(self, item, delta):
        if item in self._stock:
            if self._stock[item]['amt'] + delta >= 0:
                self._stock[item]['amt'] += delta
                return True
            return False

        if delta >= 0:
            self._stock[item] = dict()
            self._stock[item]['amt'] = delta
            self._stock[item]['item'] = get_item_by_name(item)
            return True
        return False

    def add_winning_item(self, region, player):
        print(f"Region {region.name} gets the winning item")
        item_name = f"{player.name}'s Universe"
        create_item(item_name, region.tech_level,
                    region.tech_level.value, 10000)
        self.change_stock(item_name, 1)
        self._winning_item = item_name

    @property
    def stock(self):
        return self._stock

    @property
    def prices(self):
        self.calc_prices()
        return self._prices

    @property
    def fuel_price(self):
        return self._fuel_price

    @property
    def repair_price(self):
        return self._repair_price

    @property
    def has_winning_item(self):
        return self._winning_item != ""

    @property
    def winning_item(self):
        return self._winning_item
