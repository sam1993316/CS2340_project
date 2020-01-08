from random import choice as randchoice
from random import randint
import numpy
from .market import Marketplace
from .techlevel import TechLevel
from .borg import Borg


UNIVERSE_NAMES = [
    "The Arctic Ocean", "The Pacific Ocean", "The Indian Ocean",
    "The Southern Ocean", "The Atlantic Ocean"
]
UNIVERSE_HEIGHT = 1600
UNIVERSE_WIDTH = 1200
REGION_NAMES = [
    "Bahamas", "Kolguyev", "Lombok", "Isla Isabela", "New Ireland", "Sicily",
    "Tasmania", "Old Zealand", "Buton", "Akimiski", "Maui"
]


class Universe(Borg):
    _shared_state = {}

    def __init__(self):
        Borg.__init__(self)

    @classmethod
    def new(cls):
        # pylint: disable=protected-access, attribute-defined-outside-init
        new_universe = cls()
        height = UNIVERSE_HEIGHT
        width = UNIVERSE_WIDTH
        new_universe._map = [[]] * height
        for y_pos in range(0, height):
            new_universe._map[y_pos] = [None] * width
        new_universe._name = randchoice(UNIVERSE_NAMES)
        new_universe._regions = []

        for name in REGION_NAMES:
            make_region = True
            while True:
                region_pos = [randint(0, width - 1), randint(0, height - 1)]
                make_region = True
                for region in new_universe._regions:
                    if region.too_close_to(region_pos):
                        make_region = False
                        break

                if make_region:
                    new_region = (
                        Region(region_pos,
                               randchoice(list(TechLevel)),
                               name)
                    )
                    new_universe._map[region_pos[1]][region_pos[0]] = new_region
                    new_universe._regions.append(new_region)
                    break

        print(new_universe.name)
        return new_universe


    def __contains__(self, target):
        for map_row in self._map:
            if target in map_row:
                return True

        return False

    @property
    def regions(self):
        return self._regions

    @property
    def name(self):
        return self._name

    @property
    def map(self):
        return self._map

    @property
    def width(self):
        return UNIVERSE_WIDTH

    @property
    def height(self):
        return UNIVERSE_HEIGHT


class Region:
    def __init__(
            self,
            pos=[0, 0].copy(),
            tech_level=TechLevel.PRE_AG,
            name="Region"
    ):
        self._position = pos
        self._tech_level = tech_level
        self._name = name
        self._marketplace = Marketplace(self._tech_level)

    def too_close_to(self, pos):
        coord = numpy.subtract(self.position, pos)
        if abs(coord[0]) <= 5 or abs(coord[1]) <= 5:
            return True
        return False

    def vector_to(self, other):
        if not isinstance(other, list):
            return numpy.subtract(other.position, self.position)
        else:
            return numpy.subtract(other, self.position)

    @property
    def position(self):
        return self._position

    @property
    def tech_level(self):
        return self._tech_level

    @property
    def tech_level_name(self):
        return self._tech_level.name.title().replace('_', ' ')

    @property
    def name(self):
        return self._name

    @property
    def marketplace(self):
        return self._marketplace
