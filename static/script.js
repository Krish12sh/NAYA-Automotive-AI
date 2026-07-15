// =====================================
// NAYA DASHBOARD VARIABLES
// =====================================

let previousDestination = "";

let localTemperature = 22;

let nayaMap = null;

let currentMarker = null;

let destinationMarker = null;

let routeLayer = null;

let routeShadow = null;


// Default location:
// Kondapur, Hyderabad

let currentLatitude = 17.4698;

let currentLongitude = 78.3614;


// =====================================
// SAFE TEXT UPDATE
// =====================================

function setText(

    elementID,

    value

) {

    const element =

        document.getElementById(

            elementID

        );


    if (

        element

        &&

        value !== undefined

        &&

        value !== null

    ) {

        element.textContent =

            value;

    }

}


// =====================================
// CLOCK
// =====================================

function updateClock() {

    const now =

        new Date();


    const time =

        now.toLocaleTimeString(

            [],

            {

                hour:

                "2-digit",

                minute:

                "2-digit"

            }

        );


    const date =

        now.toLocaleDateString(

            [],

            {

                weekday:

                "long",

                day:

                "numeric",

                month:

                "long"

            }

        );


    setText(

        "clock",

        time

    );


    setText(

        "date",

        date

    );

}


updateClock();


setInterval(

    updateClock,

    1000

);


// =====================================
// CREATE REAL MAP
// =====================================

function initialiseMap() {

    nayaMap =

        L.map(

            "realMap",

            {

                zoomControl:

                true,

                attributionControl:

                true

            }

        );


    nayaMap.setView(

        [

            currentLatitude,

            currentLongitude

        ],

        13

    );


    L.tileLayer(

        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

        {

            maxZoom:

            19,

            attribution:

            "© OpenStreetMap"

        }

    ).addTo(

        nayaMap

    );


    createCurrentMarker();


    detectRealLocation();

}


// =====================================
// CURRENT LOCATION MARKER
// =====================================

function createCurrentMarker() {

    const locationIcon =

        L.divIcon({

            className:

            "",


            html:

            '<div class="current-map-marker"></div>',


            iconSize:

            [

                24,

                24

            ],


            iconAnchor:

            [

                12,

                12

            ]

        });


    currentMarker =

        L.marker(

            [

                currentLatitude,

                currentLongitude

            ],

            {

                icon:

                locationIcon

            }

        );


    currentMarker

    .addTo(

        nayaMap

    );


    currentMarker

    .bindPopup(

        "Current vehicle location"

    );

}


// =====================================
// GET ACTUAL LAPTOP LOCATION
// =====================================

function detectRealLocation() {

    if (

        !navigator.geolocation

    ) {

        return;

    }


    navigator.geolocation

    .getCurrentPosition(


        function(

            position

        ) {

            currentLatitude =

                position

                .coords

                .latitude;


            currentLongitude =

                position

                .coords

                .longitude;


            currentMarker

            .setLatLng(

                [

                    currentLatitude,

                    currentLongitude

                ]

            );


            nayaMap

            .setView(

                [

                    currentLatitude,

                    currentLongitude

                ],

                14

            );


            findCurrentLocationName();

        },


        function(

            error

        ) {

            console.log(

                "Using Kondapur as prototype location.",

                error

            );

        },


        {

            enableHighAccuracy:

            true,


            timeout:

            10000

        }

    );

}


// =====================================
// CURRENT LOCATION NAME
// =====================================

async function findCurrentLocationName() {

    try {

        const requestURL =

            "https://nominatim.openstreetmap.org/reverse"

            + "?format=json"

            + "&lat="

            + currentLatitude

            + "&lon="

            + currentLongitude;


        const response =

            await fetch(

                requestURL

            );


        const location =

            await response.json();


        const address =

            location.address

            || {};


        const localArea =

            address.suburb

            ||

            address.neighbourhood

            ||

            address.city_district

            ||

            address.city

            ||

            "Current location";


        const city =

            address.city

            ||

            address.town

            ||

            address.state

            ||

            "";


        let locationName =

            localArea;


        if (

            city

            &&

            city !== localArea

        ) {

            locationName +=

                ", "

                + city;

        }


        setText(

            "currentLocationText",

            locationName

        );

    }


    catch(

        error

    ) {

        console.log(

            "Could not find location name."

        );

    }

}


// =====================================
// FIND DESTINATION
// =====================================

async function findDestination(

    destination

) {

    const searchQuery =

        destination

        + ", India";


    const requestURL =

        "https://nominatim.openstreetmap.org/search"

        + "?format=json"

        + "&limit=1"

        + "&countrycodes=in"

        + "&q="

        + encodeURIComponent(

            searchQuery

        );


    const response =

        await fetch(

            requestURL

        );


    const result =

        await response.json();


    if (

        result.length === 0

    ) {

        throw new Error(

            "Destination was not found."

        );

    }


    return {

        latitude:

        Number(

            result[0].lat

        ),


        longitude:

        Number(

            result[0].lon

        ),


        completeName:

        result[0].display_name

    };

}


// =====================================
// GET DRIVING ROUTE
// =====================================

async function calculateDrivingRoute(

    destinationLatitude,

    destinationLongitude

) {

    const requestURL =

        "https://router.project-osrm.org/route/v1/driving/"

        + currentLongitude

        + ","

        + currentLatitude

        + ";"

        + destinationLongitude

        + ","

        + destinationLatitude

        + "?overview=full"

        + "&geometries=geojson"

        + "&steps=true";


    const response =

        await fetch(

            requestURL

        );


    const result =

        await response.json();


    if (

        !result.routes

        ||

        result.routes.length === 0

    ) {

        throw new Error(

            "Driving route is unavailable."

        );

    }


    return result.routes[0];

}


// =====================================
// SHOW NAVIGATION
// =====================================

async function showDestination(

    destination

) {

    if (

        !destination

        ||

        !nayaMap

    ) {

        return;

    }


    setText(

        "destinationTitle",

        destination

    );


    setText(

        "etaValue",

        "..."

    );


    setText(

        "navigationInstruction",

        "Calculating the best driving route..."

    );


    try {

        const destinationData =

            await findDestination(

                destination

            );


        const route =

            await calculateDrivingRoute(

                destinationData.latitude,

                destinationData.longitude

            );


        drawRoute(

            route,

            destinationData,

            destination

        );

    }


    catch(

        error

    ) {

        console.error(

            "Navigation error:",

            error

        );


        setText(

            "etaValue",

            "MAP"

        );


        setText(

            "navigationInstruction",

            "Route unavailable. Opening the destination area."

        );


        try {

            const destinationData =

                await findDestination(

                    destination

                );


            nayaMap

            .setView(

                [

                    destinationData.latitude,

                    destinationData.longitude

                ],

                13

            );

        }


        catch(

            secondError

        ) {

            setText(

                "navigationInstruction",

                "NAYA could not find that destination."

            );

        }

    }

}


// =====================================
// DRAW ROUTE
// =====================================

function drawRoute(

    route,

    destinationData,

    destination

) {

    removeOldRoute();


    const routeCoordinates =

        route

        .geometry

        .coordinates

        .map(

            function(

                coordinate

            ) {

                return [

                    coordinate[1],

                    coordinate[0]

                ];

            }

        );


    // DARK BORDER UNDER ROUTE


    routeShadow =

        L.polyline(

            routeCoordinates,

            {

                color:

                "#0b0d0e",

                weight:

                14,

                opacity:

                0.9,

                lineJoin:

                "round",

                lineCap:

                "round"

            }

        );


    routeShadow

    .addTo(

        nayaMap

    );


    // GREEN ROUTE


    routeLayer =

        L.polyline(

            routeCoordinates,

            {

                color:

                "#78df35",

                weight:

                7,

                opacity:

                1,

                lineJoin:

                "round",

                lineCap:

                "round"

            }

        );


    routeLayer

    .addTo(

        nayaMap

    );


    // DESTINATION MARKER


    const destinationIcon =

        L.divIcon({

            className:

            "",


            html:

            '<div class="destination-map-marker">'

            + '<span>◆</span>'

            + "</div>",


            iconSize:

            [

                38,

                42

            ],


            iconAnchor:

            [

                19,

                38

            ]

        });


    destinationMarker =

        L.marker(

            [

                destinationData.latitude,

                destinationData.longitude

            ],

            {

                icon:

                destinationIcon

            }

        );


    destinationMarker

    .addTo(

        nayaMap

    );


    destinationMarker

    .bindPopup(

        destination

    );


    // SHOW COMPLETE ROUTE


    nayaMap

    .fitBounds(

        routeLayer

        .getBounds(),

        {

            padding:

            [

                55,

                55

            ]

        }

    );


    updateRouteInformation(

        route

    );

}


// =====================================
// REMOVE PREVIOUS ROUTE
// =====================================

function removeOldRoute() {

    if (

        routeLayer

    ) {

        nayaMap

        .removeLayer(

            routeLayer

        );

    }


    if (

        routeShadow

    ) {

        nayaMap

        .removeLayer(

            routeShadow

        );

    }


    if (

        destinationMarker

    ) {

        nayaMap

        .removeLayer(

            destinationMarker

        );

    }

}


// =====================================
// ROUTE INFORMATION
// =====================================

function updateRouteInformation(

    route

) {

    const distance =

        route.distance

        / 1000;


    const minutes =

        Math.round(

            route.duration

            / 60

        );


    let distanceText;


    if (

        distance < 10

    ) {

        distanceText =

            distance

            .toFixed(

                1

            )

            + " km";

    }


    else {

        distanceText =

            Math.round(

                distance

            )

            + " km";

    }


    const durationText =

        formatDuration(

            minutes

        );


    setText(

        "routeDistance",

        distanceText

    );


    setText(

        "routeDuration",

        durationText

    );


    setText(

        "etaValue",

        durationText

    );


    const routeSummary =

        document

        .getElementById(

            "routeSummary"

        );


    if (

        routeSummary

    ) {

        routeSummary

        .classList

        .add(

            "visible"

        );

    }


    setText(

        "navigationInstruction",

        createNavigationInstruction(

            route

        )

    );

}


// =====================================
// FORMAT DURATION
// =====================================

function formatDuration(

    totalMinutes

) {

    if (

        totalMinutes < 60

    ) {

        return totalMinutes

        + " min";

    }


    const hours =

        Math.floor(

            totalMinutes

            / 60

        );


    const minutes =

        totalMinutes

        % 60;


    return hours

    + " hr "

    + minutes

    + " min";

}


// =====================================
// FIRST ROAD INSTRUCTION
// =====================================

function createNavigationInstruction(

    route

) {

    try {

        const steps =

            route

            .legs[0]

            .steps;


        const roadStep =

            steps.find(

                function(

                    step

                ) {

                    return (

                        step.name

                        &&

                        step.distance

                        > 40

                    );

                }

            );


        if (

            roadStep

        ) {

            return (

                "Continue on "

                + roadStep.name

            );

        }

    }


    catch(

        error

    ) {

        console.log(

            "Road instruction unavailable."

        );

    }


    return (

        "Follow the highlighted route"

    );

}


// =====================================
// NEARBY BUTTONS
// =====================================

function searchNearby(

    placeType

) {

    const destination =

        placeType

        + " near me";


    setText(

        "destinationTitle",

        "Nearby "

        + placeType

    );


    const googleMapsURL =

        "https://www.google.com/maps/search/"

        + encodeURIComponent(

            destination

        );


    window.open(

        googleMapsURL,

        "_blank"

    );

}


// =====================================
// NAYA STATUS
// =====================================

function updateNayaStatus(

    status,

    message

) {

    const currentStatus =

        String(

            status

            ||

            "READY"

        )

        .toUpperCase();


    setText(

        "nayaState",

        currentStatus

    );


    setText(

        "nayaMessage",

        message

        ||

        "How can I help with your drive?"

    );

}


// =====================================
// FLASK LIVE DATA
// =====================================

async function updateNayaDashboard() {

    try {

        const response =

            await fetch(

                "/api/status",

                {

                    cache:

                    "no-store"

                }

            );


        if (

            !response.ok

        ) {

            throw new Error(

                "Dashboard unavailable."

            );

        }


        const data =

            await response.json();


        updateNayaStatus(

            data.status,

            data.message

        );


        // TEMPERATURE


        if (

            data.temperature

            !== undefined

        ) {

            localTemperature =

                Number(

                    data.temperature

                );


            setText(

                "temperature",

                localTemperature

                + "°"

            );

        }


        // AC


        if (

            data.ac

        ) {

            setText(

                "acValue",

                data.ac

                + " · "

                + localTemperature

                + "°"

            );

        }


        // DOORS


        if (

            data.doors

        ) {

            setText(

                "doorsValue",

                data.doors

            );


            if (

                data.doors

                === "LOCKED"

            ) {

                setText(

                    "securityValue",

                    "PROTECTED"

                );

            }


            else {

                setText(

                    "securityValue",

                    "UNLOCKED"

                );

            }

        }


        // SUNROOF


        if (

            data.sunroof

        ) {

            setText(

                "sunroofValue",

                data.sunroof

            );

        }


        // DRIVER WINDOW


        if (

            data.driver_window

        ) {

            setText(

                "windowValue",

                data.driver_window

            );

        }


        // FUEL


        if (

            data.fuel

            !== undefined

        ) {

            setText(

                "fuelValue",

                data.fuel

                + "%"

            );

        }


        // RANGE


        if (

            data.range

            !== undefined

        ) {

            setText(

                "rangeValue",

                data.range

                + " km"

            );

        }


        // MUSIC


        if (

            data.song

        ) {

            setText(

                "songTitle",

                data.song

            );

        }


        // DESTINATION


        if (

            data.destination

            &&

            data.destination

            !== previousDestination

        ) {

            previousDestination =

                data.destination;


            let destination =

                data.destination;


            destination =

                destination

                .replace(

                    "Navigating to ",

                    ""

                );


            destination =

                destination

                .replace(

                    "Finding nearby ",

                    ""

                );


            destination =

                destination

                .trim();


            showDestination(

                destination

            );

        }

    }


    catch(

        error

    ) {

        updateNayaStatus(

            "CONNECTING",

            "Waiting for the NAYA vehicle system..."

        );

    }

}


// =====================================
// TEMPERATURE BUTTONS
// =====================================

function changeTemperature(

    amount

) {

    localTemperature +=

        amount;


    if (

        localTemperature < 16

    ) {

        localTemperature = 16;

    }


    if (

        localTemperature > 30

    ) {

        localTemperature = 30;

    }


    setText(

        "temperature",

        localTemperature

        + "°"

    );


    setText(

        "acValue",

        "ON · "

        + localTemperature

        + "°"

    );

}


// =====================================
// ASK NAYA BUTTON
// =====================================

function focusNaya() {

    updateNayaStatus(

        "LISTENING",

        "I am ready. Tell me where you would like to go."

    );

}


// =====================================
// SIMULATED LIVE SPEED
// =====================================

function updateVehicleSpeed() {

    const newSpeed =

        47

        +

        Math.floor(

            Math.random()

            * 5

        );


    setText(

        "speed",

        newSpeed

    );

}


// =====================================
// START EVERYTHING
// =====================================

initialiseMap();


updateNayaDashboard();


setInterval(

    updateNayaDashboard,

    1000

);


setInterval(

    updateVehicleSpeed,

    2200

);