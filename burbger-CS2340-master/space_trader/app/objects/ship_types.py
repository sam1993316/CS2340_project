# template for new ship types
# number of digits is a suggestion for order of magnitude
# cargo space should be fairly small
# fuel capacity should be fairly large (the world is big)
# hp should be somewhere in between
BASE_SHIP = {
    'name': "Ship Name",
    'cargo_space': 0,
    'fuel_capacity': 000,
    'health': 00
}
# please don't use this in code elsewhere

SHIP_TYPES = [
    {
        'name': "Ant",
        'cargo_space': 10,
        'fuel_capacity': 600,
        'health': 50
    },
    {
        'name': "Beetle",
        'cargo_space': 15,
        'fuel_capacity': 800,
        'health': 25
    },
    {
        'name': "Wasp",
        'cargo_space': 5,
        'fuel_capacity': 400,
        'health': 75
    }
]
