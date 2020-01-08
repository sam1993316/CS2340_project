from .techlevel import TechLevel


def get_item_by_name(name):
    for tech_level in ITEMS:
        for item in ITEMS[tech_level]:
            if item['name'] == name:
                return item
    return False

def create_item(name, tech_level, tech_level_value, price):
    item = {
        'name': name,
        'tech_level': tech_level,
        'tech_level_value': tech_level_value,
        'price': price
    }
    ITEMS[tech_level].append(item)
    CLEANUP.append(item)

    return item

def clean_items():
    for item in CLEANUP:
        for tech_level in ITEMS:
            if item in ITEMS[tech_level]:
                ITEMS[tech_level].remove(item)

CLEANUP = []

# base item class
# you can make new ones
BASE_ITEM = {
    'name': "item name",
    'tech_level': TechLevel.PRE_AG,
    'price': 00
}

ITEMS = {
    TechLevel.PRE_AG: [
        {
            'name': "wood",
            'tech_level': TechLevel.PRE_AG,
            'tech_level_value': TechLevel.PRE_AG.value,
            'price': 1
        },
        {
            'name': "stone",
            'tech_level': TechLevel.PRE_AG,
            'tech_level_value': TechLevel.PRE_AG.value,
            'price': 2
        }
    ],
    TechLevel.AGRICULTURE: [
        {
            'name': "food",
            'tech_level': TechLevel.AGRICULTURE,
            'tech_level_value': TechLevel.AGRICULTURE.value,
            'price': 2
        },
        {
            'name': "tools",
            'tech_level': TechLevel.AGRICULTURE,
            'tech_level_value': TechLevel.AGRICULTURE.value,
            'price': 25
        }
    ],
    TechLevel.MEDIEVAL: [
        {
            'name': "metal",
            'tech_level': TechLevel.MEDIEVAL,
            'tech_level_value': TechLevel.MEDIEVAL.value,
            'price': 20
        },
        {
            'name': "leather",
            'tech_level': TechLevel.MEDIEVAL,
            'tech_level_value': TechLevel.MEDIEVAL.value,
            'price': 10
        }
    ],
    TechLevel.RENAISSANCE: [
        {
            'name': "books",
            'tech_level': TechLevel.RENAISSANCE,
            'tech_level_value': TechLevel.RENAISSANCE.value,
            'price': 10
        },
        {
            'name': "paint",
            'tech_level': TechLevel.RENAISSANCE,
            'tech_level_value': TechLevel.RENAISSANCE.value,
            'price': 15
        }
    ],
    TechLevel.INDUSTRIAL: [
        {
            'name': "coal",
            'tech_level': TechLevel.INDUSTRIAL,
            'tech_level_value': TechLevel.INDUSTRIAL.value,
            'price': 5
        },
        {
            'name': "machinery",
            'tech_level': TechLevel.INDUSTRIAL,
            'tech_level_value': TechLevel.INDUSTRIAL.value,
            'price': 25
        }
    ],
    TechLevel.MODERN: [
        {
            'name': "electronics",
            'tech_level': TechLevel.MODERN,
            'tech_level_value': TechLevel.MODERN.value,
            'price': 50
        },
        {
            'name': "batteries",
            'tech_level': TechLevel.MODERN,
            'tech_level_value': TechLevel.MODERN.value,
            'price': 100
        }
    ],
    TechLevel.FUTURISTIC: [
        {
            'name': "fusion cells",
            'tech_level': TechLevel.FUTURISTIC,
            'tech_level_value': TechLevel.FUTURISTIC.value,
            'price': 500
        },
        {
            'name': "holograms",
            'tech_level': TechLevel.FUTURISTIC,
            'tech_level_value': TechLevel.FUTURISTIC.value,
            'price': 200
        }
    ]
}
