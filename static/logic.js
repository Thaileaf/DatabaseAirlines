const parseCookie = str =>
    str
        .split(';')
        .map(v => v.split('='))
        .reduce((acc, v) => {
            acc[decodeURIComponent(v[0].trim())] = decodeURIComponent(v[1].trim());
            return acc;
        }, {});







function loadCredentials() {
    if(parseCookie(document.cookie).sessionId === "test") {
        document.getElementsByClassName("credentials")[0].style.setProperty("display", "none");
        document.getElementsByClassName("account")[0].style.setProperty("display", "inline");

    }
}


function logout() {
    // document.cookie = "";
    // document.cookie.split(";").forEach(function(c) { document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); });
    var cookies = document.cookie.split(";");

    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/DatabaseAirline";
    }
    location.reload();
}

function loadFlights() {

    let copy = document.querySelector("flight");
    copy.style.setProperty("display", "inline");


}

var on = false;
function arrivalOn() {
    let arrivals = document.getElementsByClassName("arrival");
    if(!on) {
        for(let i = 0; i < arrivals.length; ++i) {

            arrivals[i].style.setProperty("display", "inline");
        }
        on = true;
    }
    else {
        for(let i = 0; i < arrivals.length; ++i) {

            arrivals[i].style.setProperty("display", "none");
        }
        on = false;
    }
}