from random import randint
from random import choice as randchoice
from .objects import Game, Player, Universe
from .objects.character import Character
from .objects.items import ITEMS
from .objects.techlevel import TechLevel


def npc_encounter():
    player = Player()
    game = Game()
    index = randint(1, 10 - game.difficulty * 3)
    npc_stats = {
        'pilot': randint(1, 4 + game.difficulty * 2),
        'fighter': randint(1, 4 + game.difficulty * 2),
        'merchant': randint(1, 4 + game.difficulty * 2),
        'engineer': 1 # irrelevant skill for an npc
    }
    npc_money = randint(100, 200 + game.difficulty * 100)
    npc_location = player.location
    if index == 1:
        npc = Character("bandit", npc_stats, npc_money, npc_location)
        demand = randint(100 + game.difficulty * 100, 400 + game.difficulty * 200)
        print(demand)
        player.encounter_start(npc, demand, None)
        return "bandit"
    elif index == 2:
        npc = Character("trader", npc_stats, npc_money, npc_location)
        item = randchoice(ITEMS[TechLevel(randint(0, 6))])
        item_name = item['name']
        amt = randint(1, round(npc.ship.cargo_space / (game.difficulty + 1)))
        amt = min(amt, player.ship.curr_space)
        if amt == 0:
            return False
        npc.ship.change_cargo(
            item_name, # random item
            amt # random amt
        )
        price = (randint(round(item['price'] * (game.difficulty + 1) / 3), item['price'])) * amt
        player.encounter_start(npc, price, item_name)
        return "trader"
    elif index == 3:
        if len(player.ship.curr_cargo) > 0:
            npc = Character("police", npc_stats, npc_money, npc_location)
            while True:
                item_name = randchoice(list(player.ship.curr_cargo.keys()))
                if player.ship.curr_cargo[item_name]['amt'] > 0:
                    break
            item = player.ship.curr_cargo[item_name]['item']
            upper_bound = round(player.ship.curr_cargo[item_name]['amt'] / (game.difficulty + 1))
            if upper_bound <= 1:
                amt = 1
            else:
                amt = randint(1, upper_bound)

            player.encounter_start(npc, amt, item_name)
            return "police"
    return False

def handle_travel_request(form):
    player = Player()
    if player.in_encounter:
        return {'code': "In encounter", 'success': False,
                'fuel_remaining': player.ship.curr_fuel}
    universe = Universe()
    #try:
    if 0 <= int(form['travel_to']) < len(universe.regions):
        location = universe.regions[int(form['travel_to'])]
        success = player.travel(location)
        encounter = npc_encounter()
        if success:
            code = f"{player.ship.curr_fuel} fuel remains"
        else:
            code = "Insufficient fuel"
        encounter_inventory = 0
        response = {
            'code': code,
            'success': success,
            'encounter': encounter,
            'fuel_remaining': player.ship.curr_fuel
        }
        if player.in_encounter:
            if player.encounter.npc_type == "trader":
                encounter_cargo = player.encounter.npc.ship.curr_cargo
                encounter_inventory = encounter_cargo[player.encounter.item]['amt']
                response.update({'encounter_inventory': encounter_inventory})
            response.update({
                'encounter_quantity': player.encounter.quantity,
                'encounter_item': player.encounter.item
            })
    #except KeyError as error:
        #response = "Improper travel request", 400, {'Content-Type': 'text/plain'}

    return response

def handle_buy_request(form):
    player = Player()
    if player.in_encounter:
        return {'success': False, 'code': "In encounter"}
    item = form["item"]
    buy_result = player.buy(item)
    if buy_result[0]:
        print(f"Successfully bought {item}")
        response = {
            'success': True,
            'money_remaining': player.money,
            'new_inventory': player.ship.curr_cargo,
            'new_stock': player.location.marketplace.stock,
            'karma': player.karma
        }
    else:
        print(buy_result[1])
        response = {'success': False, 'code': buy_result[1]}

    return response

def handle_sell_request(form):
    player = Player()
    if player.in_encounter:
        return {'success': False, 'code': "In encounter"}
    item = form["item"]
    if player.sell(item):
        print(f"Successfully sold {item}")
        response = {
            'success': True,
            'money_remaining': player.money,
            'new_inventory': player.ship.curr_cargo,
            'new_stock': player.location.marketplace.stock,
            'karma': player.karma
        }
    else:
        print("Not enough to sell")
        response = {'success': False, 'code': f"Not enough {item}"}

    return response

def handle_refuel_request(form):
    player = Player()
    saved_fuel = player.ship.curr_fuel
    saved_money = player.money
    if player.in_encounter:
        return {
            'success': False,
            'code': "In encounter",
            'new_fuel': saved_fuel,
            'new_money': saved_money
        }
    try:
        fuel_added = int(form["amount"])
        player.money -= fuel_added * player.location.marketplace.fuel_price
        player.ship.curr_fuel += fuel_added
        response = {
            'success': True,
            'code': "Refuel successful",
            'new_fuel': player.ship.curr_fuel,
            'new_money': player.money
        }
    except ValueError as error:
        player.money = saved_money
        player.ship.curr_fuel = saved_fuel
        response = {
            'success': False,
            'code': str(error),
            'new_fuel': saved_fuel,
            'new_money': saved_money
        }

    return response

def handle_repair_request(form):
    player = Player()
    saved_health = player.ship.curr_health
    saved_money = player.money
    if player.in_encounter:
        return {
            'success': False,
            'code': "In encounter",
            'new_health': saved_health,
            'new_money': saved_money
        }
    try:
        health_added = int(form["amount"])
        player.money -= (health_added
                         * player.location.marketplace.repair_price
                         * (10 / player.skills['engineer']))
        player.heal(health_added)
        response = {
            'success': True,
            'code': "Repair successful",
            'new_health': player.ship.curr_health,
            'new_money': player.money
        }
    except ValueError as error:
        player.money = saved_money
        player.ship.curr_health = saved_health
        response = {
            'success': False,
            'code': str(error),
            'new_health': saved_health,
            'new_money': saved_money
        }

    return response

def handle_encounter_pay_request(_):
    player = Player()
    if player.in_encounter:
        print("Paid off encounter")
        success = player.encounter.pay()
        return {
            'success': success,
            'money_remaining': player.money,
            'new_inventory': player.ship.curr_cargo,
            'health_remaining': player.ship.curr_health,
            'market_prices': player.location.marketplace.prices
        }
    return "Invalid command", 422, {'Content-Type': 'text/plain'}

def handle_encounter_leave_request(_):
    player = Player()
    if player.in_encounter:
        print("Attempted to flee encounter")
        success = player.encounter.leave()
        return {
            'success': success,
            'money_remaining': player.money,
            'new_inventory': player.ship.curr_cargo,
            'health_remaining': player.ship.curr_health,
            'market_prices': player.location.marketplace.prices
        }
    return "Invalid command", 422, {'Content-Type': 'text/plain'}

def handle_encounter_fight_request(_):
    player = Player()
    if player.in_encounter:
        print("Attempted to fight off encounter")
        success = player.encounter.fight()
        return {
            'success': success,
            'money_remaining': player.money,
            'new_inventory': player.ship.curr_cargo,
            'health_remaining': player.ship.curr_health,
            'market_prices': player.location.marketplace.prices
        }
    return "Invalid command", 422, {'Content-Type': 'text/plain'}

def handle_encounter_negotiate_request(_):
    player = Player()
    if player.in_encounter:
        print("Attempted to negotiate in encounter")
        negotiated = player.encounter.negotiated
        success = player.encounter.negotiate()
        valid = player.encounter.npc_type == "trader"
        return {
            'success': success,
            'valid': valid,
            'negotiated': negotiated,
            'new_price': player.encounter.quantity
        }
    return "Invalid command", 422, {'Content-Type': 'text/plain'}

def handle_get_player_location(_):
    player = Player()
    universe = Universe()
    index = universe.regions.index(player.location)
    return {'index': index, 'market_prices': player.location.marketplace.prices}

def handle_get_player_inventory(_):
    player = Player()
    return {'inventory': player.ship.curr_cargo}

def handle_get_encounter(_):
    player = Player()
    encounter_inventory = 0
    if player.in_encounter and player.encounter.npc_type == "trader":
        encounter_cargo = player.encounter.npc.ship.curr_cargo
        encounter_inventory = encounter_cargo[player.encounter.item]['amt']
        return {
            'in_encounter': player.in_encounter,
            'encounter_type': player.encounter.npc_type,
            'encounter_quantity': player.encounter.quantity,
            'encounter_item': player.encounter.item,
            'encounter_inventory': encounter_inventory
        }
    return {'in_encounter': False}

def handle_get_market_stock(_):
    player = Player()
    return {
        'market_stock': player.location.marketplace.stock,
        'market_name': player.location.name,
        'market_prices': player.location.marketplace.prices,
        'refuel_price': player.location.marketplace.fuel_price,
        'repair_price': player.location.marketplace.repair_price
                        * (10 / player.skills['engineer'])
    }

def handle_cheat_request(_):
    player = Player()
    player.money += 10000
    return {'success': True, 'new_money': player.money}

def handle_kill_request(_):
    player = Player()
    player.kill()
    return {'success': True, 'new_health': player.ship.curr_health}

def handle_set_karma_request(form):
    player = Player()
    player.karma = form['amount']
    print(f"Karma changed to {form['amount']}")
    return {'success': True}

request_types = {
    "travel": handle_travel_request,
    "buy": handle_buy_request,
    "sell": handle_sell_request,
    "refuel": handle_refuel_request,
    "repair": handle_repair_request,
    "encounter_pay": handle_encounter_pay_request,
    "encounter_leave": handle_encounter_leave_request,
    "encounter_fight": handle_encounter_fight_request,
    "encounter_negotiate": handle_encounter_negotiate_request,
    "get_player_location": handle_get_player_location,
    "get_player_inventory": handle_get_player_inventory,
    "get_encounter": handle_get_encounter,
    "get_market_stock": handle_get_market_stock,
    "cheat": handle_cheat_request,
    "kill": handle_kill_request,
    "set_karma": handle_set_karma_request
}
