function wordRegExp(name) {
    return new RegExp('(\\s|^)' + name + ('(\\s|^'));
}

function toTitleCase(str) {
    return str.replace(
        /\w\S*/g,
        function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
}

function buildForm(json) {
    var encodedForm = "";
    for (key in json) {
        encodedForm += encodeURIComponent(key)+"="+encodeURIComponent(json[key])+"&";
    }
    return encodedForm;
}

function hasClass(target, name) {
    if (target.classList) {
        return target.classList.contains(name);
    } else {
        // matches our classname anywhere in the classname
        // doesn't match if it's a substring, e.g. "hello" won't match "othello"
        return !!target.className.match(wordRegExp(name));
    }
};

function addClass(target, name) {
    if (hasClass(target, name)) {
        return;
    } else if (target.classList) {
        target.classList.add(name);
    } else {
        target.className += " " + name;
    }
};

function removeClass(target, name) {
    if (hasClass(target, name)) {
        if (target.classList) {
            target.classList.remove(name);
        } else {
            var removedName = wordRegExp(name);
            target.className = target.className.replace(removedName, ' ');
        }
    } else {
        return;
    }
};

function getIndex(element) {
    var index = 0;
    var sibling = element;
    while ((sibling = sibling.previousElementSibling) != null) {
        index++;
    }
    return index;
}

function cheat() {
    quickPost({'type': 'cheat'}, cheatHandler);
}

function cheatHandler(response) {
    if (response['success']) {
        updateMoney(response['new_money']);
    }
}

function kill() {
    quickPost({'type': 'kill'}, killHandler);
}

function killHandler(response) {
    if (response['success']) {
        updateHealth(response['new_health']);
    }
}

function setKarma(amt) {
    quickPost({'type': 'set_karma', 'amount': amt}, console.log);
    cachedKarma = amt;
    showInventory(cachedInventory, cachedKarma, cachedPrices);
}

function gameOver() {
    window.location.replace(document.getElementById("game_over_url").value);
}

function post(form, url, func) {
    var request = new XMLHttpRequest();
    request.open('POST', url);
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    request.responseType = "json";
    request.onload = () => func(request.response, request.status);
    request.onerror = () => func(request.response, request.status);
    request.send(form);
}

function quickPost(json, func) {
    json["csrf_token"] = document.getElementById("csrf_token").value;
    var form = buildForm(json);
    var url = document.getElementById("post_location").value;
    post(form, url, func);
}

function postPromise(form, url) {
    return new Promise(function (resolve, reject) {
        var request = new XMLHttpRequest();
        request.open('POST', url);
        request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        request.responseType = "json";
        request.onload = resolve;
        request.onerror = reject;
        request.send();
    });
}

function quickPromise(json) {
    json["csrf_token"] = document.getElementById("csrf_token").value;
    var form = buildForm(json);
    var url = document.getElementById("post_location").value;
    return postPromise(form, url);
}
