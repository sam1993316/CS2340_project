var encounterType = "";
var encounterItem = "";
var encounterAmount = 0
var encounterStock = {};

window.addEventListener('load',
                        function () {
                            quickPost({"type": "get_encounter"}, updateEncounter);
                        });

function updateHealth(amt) {
    healthCounter = document.getElementById("curr_health");
    healthCounter.textContent = Math.round(amt);
}

function encounter(type, amt, item, stock) {
    // we got an encounter!
    showEncounter(type, amt, item, stock);
    if (type == "bandit") {
        banditEncounter(amt);
    } else if (type == "trader") {
        traderEncounter(amt, item, stock);
    } else if (type == "police") {
        policeEncounter(amt, item);
    } else {
        // we didn't really get an encounter, pretend it never happened
        alert("Invalid encounter type, proceeding");
        quickPost({"type": "get_player_location"}, updateLocation);
    }
}

function banditEncounter(amt) {
    alert("A bandit has crossed your path, demanding you pay " + amt + " credits.");
    encounterType = "bandit";
    encounterAmount = amt;
}

function policeEncounter(amt, item) {
    alert("The police want to seize " + amt + " of your " + item + ".");
    encounterType = "police";
    encounterItem = item;
    encounterAmount = amt;
}

function traderEncounter(amt, item, stock) {
    alert("A trader wants to sell " + item + " to you for " + amt + " credits!");
    encounterType = "trader";
    encounterItem = item;
    encounterAmount = amt;
    encounterStock = stock;
}

function pay() {
    quickPost({"type": "encounter_pay"}, payHandler);
}

function payHandler(response, status) {
    var success = response['success'];
    if (encounterType == "bandit") {
        if (success == 2) {
            alert("You pay the bandit " + encounterAmount + " credits and continue on your way.");
        } else if (success == 1) {
            alert("You can't afford to pay the bandit! They take all of your items instead and let you go.");
        } else {
            alert("You have nothing of value to the bandit! Frustrated, they attack your ship!");
        }
    } else if (encounterType == "police") {
        alert("You hand over " + encounterAmount + " " + encounterItem + " and are allowed to pass.");
    } else {
        if (success) {
            alert("You pay " + encounterAmount + " and receive " + encounterStock + " " + encounterItem + ".");
        } else {
            alert("You can't afford to pay the merchant that much!");
            return;
        }
    }
    exitEncounter(response);
}

function leave() {
    quickPost({"type": "encounter_leave"}, leaveHandler);
}

function leaveHandler(response, status) {
    if (response['success']) {
        if (encounterType == "bandit") {
            alert("You manage to flee back from where you came and arrive unscathed!");
        } else if (encounterType == "police") {
            alert("The police are unable to keep up as you flee! You make it back unharmed.");
        } else {
            alert("You leave the merchant and their wares.");
        }
    } else {
        if (encounterType == "bandit") {
            alert("You fail to flee from the bandit! They make off with all your credits...");
        } else if (encounterType == "police") {
            alert("The police are able to catch up to you, confiscate your " + encounterItem + ", and fine you for fleeing!");
        } else {
            alert("You leave the merchant and their wares.");
        }
    }
    exitEncounter(response);
}

function fight() {
    quickPost({"type": "encounter_fight"}, fightHandler);
}

function fightHandler(response, status) {
    if (response['success']) {
        if (encounterType == "bandit") {
            alert("The bandit flees after taking a beating. You salvage some credits from their ship!");
        } else if (encounterType == "police") {
            alert("You send the police packing and protect your items from confiscation!");
        } else {
            alert("Instead of paying for it, you fight the merchant and steal their " + encounterItem + "!");
        }
    } else {
        if (encounterType == "bandit") {
            alert("The bandit puts up too much of a fight for you, and takes all your credits for the trouble.");
        } else if (encounterType == "police") {
            alert("The police fight back and take the " + encounterItem + " they came for by force, plus a fine for resisting!");
        } else {
            alert("You try to rob the merchant, but they're too much for you to handle and your ship takes a few hits.");
        }
    }
    exitEncounter(response);
}

function negotiate() {
    quickPost({"type": "encounter_negotiate"}, negotiateHandler);
}

function negotiateHandler(response, status) {
    if (response['valid']) {
        if (response['success']) {
            alert("You haggle the merchant down to " + response['new_price'] + " - half their original price!");
        } else if (response['negotiated']) {
            alert("The merchant refuses to hear your attempts at negotiation again.");
        } else {
            alert("The merchant takes offense at your poor attempts at persuasion and raises their price to " + response['new_price'] + "!");
        }
    } else {
        alert("You can't negotiate in this encounter!");
    }
    showEncounter(encounterType, response['new_price'], encounterItem, encounterStock);
}

function exitEncounter(response) {
    if (response['game_over']) {
        return gameOver();
    }
    updateMoney(Number(response['money_remaining']));
    updateHealth(Number(response['health_remaining']));
    cachedInventory = response['new_inventory'];
    cachedPrices = response['market_prices'];
    showInventory(cachedInventory, cachedKarma, cachedPrices);
    quickPost({"type": "get_player_location"}, updateLocation);
    hideEncounter();
}

function updateEncounter(response) {
    if (response['in_encounter']) {
        showEncounter(response['encounter_type'],
                      response['encounter_quantity'],
                      response['encounter_item'],
                      response['encounter_inventory']);
        encounterType = response['encounter_type'],
        encounterAmount = response['encounter_quantity'];
        encounterItem = response['encounter_item'];
        encounterStock = response['encounter_inventory'];
    } else {
        hideEncounter();
    }
}

function hideEncounter() {
    var encounters = document.getElementById("encounters");
    var markets = document.getElementById("markets");
    addClass(encounters, "hidden");
    removeClass(markets, "hidden");
}

function showEncounter(type, amt, item, stock) {
    console.log("Showing encounters");
    var encounters = document.getElementById("encounters");
    var markets = document.getElementById("markets");
    removeClass(encounters, "hidden");
    addClass(markets, "hidden");

    var icon = document.getElementById("encounter_img");
    var typeLabel = document.getElementById("encounter_type");
    var description = document.getElementById("encounter_description");
    typeLabel.textContent = toTitleCase(type);
    if (type == "bandit") {
        icon.src = document.getElementById("bandana_img").src;
        description.textContent = "A bandit is demanding " + amt + " credits for your safe passage! What do you do?";
    } else if (type == "police") {
        icon.src = document.getElementById("helmet_img").src;
        description.textContent = "The police believe you have " + amt + " stolen " + item + " and demand you cough up. What do you do?";
    } else {
        icon.src = document.getElementById("tophat_img").src;
        description.textContent = "A trader is offering you " + stock + " " + item + " for " + amt + " credits. What do you do?";
    }
}
