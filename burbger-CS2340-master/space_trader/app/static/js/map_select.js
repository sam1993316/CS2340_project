var lastSelected = null;
var selectedIndex = 0;
var cachedPrices = null;

window.addEventListener('load',
                        function () {
                            document.getElementById("travel_button").disabled = true;
                        });

function regionSelected(event) {
    if (lastSelected !== null) {
        removeClass(lastSelected, "selected");
    }
    addClass(event.target, "selected");
    lastSelected = event.target;
    selectedIndex = getIndex(event.target.parentElement);
    // set target region up
    var currentRegion = document.getElementById("selected_region");
    var regionContainer = currentRegion.parentNode;
    var newRegion = event.target.nextElementSibling.cloneNode(true);
    var travelButton = document.getElementById("travel_button");
    var travelButtonContainer = travelButton.parentNode;
    var locationName = document.getElementById("location_name");
    newRegion.id = "selected_region";
    addClass(newRegion, "show");
    addClass(newRegion, "selected");
    if (event.target.id == "active") {
        travelButton.disabled = true;
    } else {
        travelButton.disabled = false;
    }
    locationName.textContent = newRegion.firstElementChild.textContent;
    regionContainer.removeChild(currentRegion);
    regionContainer.appendChild(newRegion);
    regionContainer.appendChild(travelButtonContainer);
    updateFuelCost();
}

function attemptTravel(event) {
    quickPost({"type": "travel", "travel_to": selectedIndex}, travelHandler);
}

function travelHandler(response) {
    if (response['game_over']) {
        return gameOver();
    }
    var success = response['success'];
    var encounter_type = response['encounter'];
    var encounter_quantity = response['encounter_quantity'];
    var encounter_item = response['encounter_item'];
    var encounter_inventory = response['encounter_inventory'];
    var code = response['code'];
    var fuelRemaining = response['fuel_remaining'];
    if (success) {
        if (encounter_type) {
            // handle encounter and put the update on hold
            encounter(encounter_type, encounter_quantity, encounter_item, encounter_inventory);
        } else {
            // just update
            quickPost({"type": "get_player_location"}, updateLocation);
            cachedPrices = response['market_prices'];
        }
        console.log("Travel success! " + code);
    } else {
        alert("Failed to travel: " + code);
    }
    updateFuel(fuelRemaining);
    updateFuelCost();
}

function updateLocation(response, status) {
    var parent = document.getElementById("map").children[response["index"]];
    var newElement = parent.children[0];
    var newRegion = parent.children[1].cloneNode(true);

    var currentElement = document.getElementById("active");
    var currentRegion = document.getElementById("current_region");

    var regionContainer = currentRegion.parentNode;
    var travelButton = document.getElementById("travel_button");

    if (newElement === currentElement) {
        return;
    }

    newElement.id = "active";
    newRegion.id = "current_region";
    addClass(newRegion, "active");
    addClass(newRegion, "show");
    regionContainer.appendChild(newRegion);

    currentElement.removeAttribute("id");
    regionContainer.removeChild(currentRegion);

    travelButton.disabled = hasClass(newElement, "selected");
    cachedPrices = response['market_prices'];
    updateMarket(currentRegion.firstElementChild.textContent);
}

function updateFuel(amt) {
    fuelCounter = document.getElementById("curr_fuel");
    fuelCounter.textContent = Math.round(amt);
}

function getFuel() {
    return Number(document.getElementById("curr_fuel").textContent);
}

function updateFuelCost() {
    var activeLocation = document.getElementById("active");
    var x0 = getComputedStyle(activeLocation).getPropertyValue('--x-pos');
    var x1 = getComputedStyle(lastSelected).getPropertyValue('--x-pos');
    var y0 = getComputedStyle(activeLocation).getPropertyValue('--y-pos');
    var y1 = getComputedStyle(lastSelected).getPropertyValue('--y-pos');
    var dist = Math.sqrt(Math.pow(x1 - x0, 2) + Math.pow(y1 - y0, 2));
    var pilotSkill = Number(document.getElementById("pilot").textContent);
    var fuelCost = dist * (1 / (pilotSkill + 1));
    document.getElementById("fuel_cost").textContent = Math.round(fuelCost);
    if (fuelCost > getFuel()) {
        document.getElementById("travel_button").disabled = true;
    }
}
