var cachedInventory = null;
var cachedKarma = 0;

window.addEventListener('load', function () {
    quickPost({"type": "get_player_inventory"},
              function (response) {
                  if (typeof fresh == undefined) {
                      cachedInventory = response["inventory"];
                      showInventory(cachedInventory, cachedKarma, cachedPrices);
                      fresh = true;
                  }
              });
});

window.addEventListener('load', function () {
    quickPost({"type": "get_market_stock"}, updateMarketStock);
});

function updateMarket(oldRegionName) {
    var currentRegion = document.getElementById("current_region");
    var regionName = currentRegion.firstElementChild.textContent;
    if (oldRegionName == regionName) {
        return;
    }
    var oldMarket = document.getElementById(oldRegionName+"_market");
    var activeMarket = document.getElementById(regionName+"_market");
    removeClass(oldMarket, 'show');
    addClass(activeMarket, 'show');
    showInventory(cachedInventory, cachedKarma, cachedPrices);
    quickPost({"type": "get_market_stock"}, updateMarketStock);
}

function updateMarketStock(response) {
    cachedPrices = response["market_prices"];
    showStock(response["market_name"], response["market_stock"],
              response["refuel_price"], response["repair_price"]);
}

function buyItem(event) {
    var item = event.target.getAttribute('item');
    var region = event.target.getAttribute('region');
    quickPost({"type": "buy", "item": item, "from": region}, buyHandler);
}

function buyHandler(response) {
    if (response['game_over']) {
        return gameOver();
    }
    console.log(response);
    var success = response["success"];
    if (success) {
        var regionName = document.getElementById('current_region')
            .firstElementChild.textContent;
        var moneyRemaining = response["money_remaining"];
        updateMoney(moneyRemaining);
        cachedInventory = response["new_inventory"];
        cachedKarma = response["karma"];
        showInventory(cachedInventory, cachedKarma, cachedPrices);
        showStock(regionName, response["new_stock"]);
        return;
    }
    alert(response["code"]);
}

function sellItem(event) {
    var item = event.target.getAttribute('item');
    var region = event.target.getAttribute('region');
    quickPost({"type": "sell", "item": item, "to": region}, sellHandler);
}

function sellHandler(response) {
    if (response['game_over']) {
        return gameOver();
    }
    console.log(response);
    var success = response["success"];
    if (success) {
        var regionName = document.getElementById('current_region')
            .firstElementChild.textContent;
        var moneyRemaining = response["money_remaining"];
        updateMoney(moneyRemaining);
        cachedInventory = response["new_inventory"];
        cachedKarma = response["karma"];
        showInventory(cachedInventory, cachedKarma, cachedPrices);
        showStock(regionName, response["new_stock"]);
        return;
    } else {
        alert(response["code"]);
    }
}

function refuel(event) {
    var amount = document.getElementById('refuel_amount').value;
    quickPost({"type": "refuel", "amount": amount}, refuelHandler);
}

function refuelConsole(amt) {
    quickPost({"type": "refuel", "amount": amt}, refuelHandler);
}

function refuelHandler(response) {
    if (response['game_over']) {
        return gameOver();
    }
    var success = response["success"];
    if (success) {
        var newMoney = response["new_money"];
        var newFuel = response["new_fuel"];
        updateMoney(Number(newMoney));
        updateFuel(Number(newFuel));
    } else {
        alert(response["code"]);
    }
}

function repair(event) {
    var amount = document.getElementById('repair_amount').value;
    quickPost({"type": "repair", "amount": amount}, repairHandler);
}

function repairConsole(amt) {
    quickPost({"type": "repair", "amount": amt}, repairHandler);
}

function repairHandler(response) {
    if (response['game_over']) {
        return gameOver();
    }
    var success = response["success"];
    if (success) {
        var newMoney = response["new_money"];
        var newHealth = response["new_health"];
        updateMoney(Number(newMoney));
        updateHealth(Number(newHealth));
    } else {
        alert(response["code"]);
    }
}

function updateMoney(amt) {
    var money = document.getElementById('money');
    money.textContent = Math.round(amt);
}

function showInventory(inventory, karma, marketPrices) {
    console.log("Updating inventory");
    var inventoryElement = document.getElementById('player_inventory');
    while (inventoryElement.firstChild) {
        inventoryElement.removeChild(inventoryElement.firstChild);
    }
    var container = document.createElement('div');
    addClass(container, "item_container");
    container.appendChild(itemInfoHeader("quantity", "Quantity"));
    container.appendChild(itemInfoHeader("name", "Item"));
    container.appendChild(itemInfoHeader("value", "Value"));
    container.appendChild(itemInfoHeader("sell_price", "Sell Price"));
    container.appendChild(itemInfoHeader("sell", "Sell"));
    inventoryElement.appendChild(container);
    for (var item in inventory) {
        var itemLine = displayInventoryItem(inventory[item], karma, marketPrices);
        if (itemLine) {
            inventoryElement.appendChild(itemLine);
        }
    }
}

function showStock(regionName, newStock, refuelPrice, repairPrice) {
    var regionMarket = document.getElementById(regionName + '_market');
    while (regionMarket.firstChild) {
        regionMarket.removeChild(regionMarket.firstChild);
    }
    var container = document.createElement('div');
    addClass(container, "item_container");
    container.appendChild(itemInfoHeader("quantity", "Quantity"));
    container.appendChild(itemInfoHeader("name", "Item"));
    container.appendChild(itemInfoHeader("buy_price", "Buy Price"));
    container.appendChild(itemInfoHeader("buy", "Buy"));
    regionMarket.appendChild(container);
    for (var item in newStock) {
        console.log(item);
        var itemLine = displayMarketItem(newStock[item]);
        console.log(itemLine);
        if (itemLine) {
            regionMarket.appendChild(itemLine);
        }
    }
    if (refuelPrice != null) {
        document.getElementById("refuel_price").textContent = "@ " + refuelPrice + " ea.";
    }
    if (repairPrice != null) {
        document.getElementById("repair_price").textContent = "@ " + repairPrice + " ea.";
    }
}

function displayInventoryItem(item, karma, marketPrices) {
    var amt = item['amt'];
    if (amt > 0) {
        var currentRegion = document.getElementById("current_region");
        var techLevel = Number(currentRegion.getAttribute('techlevel'));
        var techDiff = Math.abs(techLevel - item['item']['tech_level_value']);
        var merchSkill = Number(document.getElementById("merchant").textContent);
        var name = item['item']['name'];
        var value = item['item']['price'];
        var karmaModifier = Math.min(Math.max(karma / 50, -0.5), 0.5);
        var sellPrice = Math.round(Math.min(marketPrices[name]
                                            * (1 + (techDiff * 10 / 6))
                                            * (0.5 + (merchSkill / 20))
                                            * (1 + karmaModifier),
                                            marketPrices[name]));
        sellPrice = "" + sellPrice + " ea.";
        var container = document.createElement('div');
        addClass(container, "item_container");
        container.appendChild(itemInfo("quantity", amt));
        container.appendChild(itemInfo("name", toTitleCase(name)));
        container.appendChild(itemInfo("value", value));
        container.appendChild(itemInfo("sell_price", sellPrice));
        container.appendChild(sellButton(item));
        return container;
    }
}

function displayMarketItem(item) {
    var amt = item['amt'];
    if (amt > 0) {
        var currentRegion = document.getElementById("current_region");
        var techLevel = Number(currentRegion.getAttribute('techlevel'));
        var techDiff = Math.abs(techLevel - item['item']['tech_level_value']);
        var name = toTitleCase(item['item']['name']);
        var buyPrice = Math.round(item['item']['price']
                                  * (1 + (techDiff * 10 / 6)));
        buyPrice = "" + buyPrice + " ea."
        var container = document.createElement('div');
        addClass(container, "item_container");
        container.appendChild(itemInfo("quantity", amt));
        container.appendChild(itemInfo("name", name));
        container.appendChild(itemInfo("buy_price", buyPrice));
        container.appendChild(buyButton(item));
        return container;
    }
}

function itemInfo(cls, content) {
    var out = document.createElement('div');
    addClass(out, "item_info");
    addClass(out, cls);
    out.textContent = content;
    return out;
}

function itemInfoHeader(cls, content) {
    var out = itemInfo(cls, content);
    addClass(out, "header");
    return out;
}

function sellButton(item) {
    var out = document.createElement('button');
    addClass(out, "item_info");
    addClass(out, "sell");
    out.setAttribute('item', item['item']['name']);
    out.region = document.getElementById("current_region")
        .firstElementChild.textContent;
    out.onclick = (event) => sellItem(event);
    out.textContent = "Sell " + item['item']['name'];
    return out;
}

function buyButton(item) {
    var out = document.createElement('button');
    addClass(out, "item_info");
    addClass(out, "buy");
    out.setAttribute('item', item['item']['name']);
    out.region = document.getElementById("current_region")
        .firstElementChild.textContent;
    out.onclick = (event) => buyItem(event);
    out.textContent = "Buy " + item['item']['name'];
    return out;
}
