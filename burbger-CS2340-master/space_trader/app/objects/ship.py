from .items import get_item_by_name

class Ship:
    def __init__(self, ship_type):
        self._ship_type = ship_type.copy()
        self._curr_health = ship_type['health']
        self._curr_space = ship_type['cargo_space']
        self._curr_fuel = ship_type['fuel_capacity']
        self._curr_cargo = dict()

    def change_cargo(self, item, delta):
        if self.curr_space - delta > self.cargo_space:
            print("Insufficient space")
            return False

        if item in self._curr_cargo:
            if self._curr_cargo[item]['amt'] + delta < 0:
                print("Insufficient cargo")
                return False
            self._curr_cargo[item]['amt'] += delta
        elif delta >= 0:
            self._curr_cargo[item] = dict()
            self._curr_cargo[item]['amt'] = delta
            self._curr_cargo[item]['item'] = get_item_by_name(item)
        else:
            print("No cargo")
            return False

        self._curr_space -= delta
        return True

    def clear_cargo(self):
        self._curr_cargo = dict()

    @property
    def curr_health(self):
        return self._curr_health

    @curr_health.setter
    def curr_health(self, health):
        if health < 0:
            health = 0

        if health > self.health:
            raise ValueError("Can't repair that much")

        self._curr_health = health

    @property
    def curr_space(self):
        return self._curr_space

    @property
    def cargo_space(self):
        return self._ship_type['cargo_space']

    @property
    def curr_fuel(self):
        return self._curr_fuel

    @curr_fuel.setter
    def curr_fuel(self, fuel):
        if fuel < 0:
            raise ValueError("Insufficient fuel")

        if fuel > self.fuel_capacity:
            raise ValueError("Can't refuel that much")

        self._curr_fuel = round(fuel)

    @property
    def curr_cargo(self):
        return self._curr_cargo

    @property
    def fuel_capacity(self):
        return self._ship_type['fuel_capacity']

    @property
    def health(self):
        return self._ship_type['health']

    @property
    def name(self):
        return self._ship_type['name']
