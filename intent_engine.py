import re


# =====================================
# NORMALIZE NATURAL ENGLISH
# =====================================

def normalize_text(text):

    text = text.lower().strip()

    replacements = {

        "air conditioner": "ac",

        "air conditioning": "ac",

        "a c": "ac",

        "petrol station": "petrol pump",

        "gas station": "petrol pump",

        "fuel station": "petrol pump",

        "charging point": "charging station",

        "electric charger": "charging station",

        "driver side window": "driver window",

        "driver's window": "driver window",

        "car window": "window",

        "roof window": "sunroof",

        "movie theatre": "cinema",

        "movie theater": "cinema",

        "food place": "restaurant"

    }

    for old_text, new_text in replacements.items():

        text = text.replace(
            old_text,
            new_text
        )


    # Remove punctuation

    text = re.sub(

        r"[^\w\s]",

        " ",

        text

    )


    # Remove repeated spaces

    text = re.sub(

        r"\s+",

        " ",

        text

    )


    return text.strip()


# =====================================
# CHECK KEYWORDS
# =====================================

def has_any(text, keywords):

    return any(

        keyword in text

        for keyword in keywords

    )


# =====================================
# SCORE AN INTENT
# =====================================

def calculate_score(

    text,

    keywords

):

    score = 0

    matched_words = []


    for keyword in keywords:

        if keyword in text:

            score += 1

            matched_words.append(
                keyword
            )


    return score, matched_words


# =====================================
# DETECT USER INTENT
# =====================================

def understand_command(command):

    text = normalize_text(
        command
    )


    # ---------------------------------
    # INTENT KEYWORDS
    # ---------------------------------

    intent_keywords = {


        "navigation": [

            "navigate",

            "navigation",

            "route",

            "directions",

            "direction",

            "drive",

            "take me",

            "go to",

            "get to",

            "way to",

            "road to",

            "guide me",

            "reach",

            "destination",

            "map"

        ],


        "nearby": [

            "nearest",

            "near me",

            "nearby",

            "closest",

            "around me",

            "close to me",

            "find a",

            "find the",

            "search nearby",

            "where is"

        ],


        "music": [

            "play",

            "music",

            "song",

            "songs",

            "listen",

            "hearing",

            "playlist",

            "youtube",

            "put on",

            "feel like listening"

        ],


        "climate": [

            "ac",

            "temperature",

            "climate",

            "cabin",

            "cool",

            "cooler",

            "cooling",

            "hot",

            "cold",

            "warmer",

            "degrees"

        ],


        "sunroof": [

            "sunroof"

        ],


        "doors": [

            "door",

            "doors",

            "lock",

            "unlock",

            "secure"

        ],


        "window": [

            "window",

            "windows",

            "roll down",

            "roll up"

        ],


        "vehicle_status": [

            "vehicle status",

            "car status",

            "vehicle health",

            "car health",

            "vehicle report",

            "car report",

            "fuel level",

            "driving range",

            "how is my car",

            "how is the vehicle"

        ]

    }


    scores = {}


    matched = {}


    for intent, keywords in (

        intent_keywords.items()

    ):

        score, words = (

            calculate_score(

                text,

                keywords

            )

        )


        scores[intent] = score


        matched[intent] = words


    # ---------------------------------
    # EXTRA CONTEXT RULES
    # ---------------------------------


    # Nearby place names

    nearby_places = [

        "petrol pump",

        "charging station",

        "restaurant",

        "hospital",

        "hotel",

        "cinema",

        "atm",

        "bank",

        "parking",

        "pharmacy",

        "mcdonald",

        "burger king",

        "cafe"

    ]


    if (

        has_any(

            text,

            nearby_places

        )

        and

        has_any(

            text,

            [

                "nearest",

                "near",

                "nearby",

                "closest",

                "around"

            ]

        )

    ):

        scores["nearby"] += 4


    # Temperature number

    temperature = None


    numbers = re.findall(

        r"\b\d{1,2}\b",

        text

    )


    for number in numbers:

        value = int(number)


        if 16 <= value <= 30:

            temperature = value

            scores["climate"] += 4

            break


    # Music context

    if (

        "song" in text

        or

        "music" in text

        or

        "playlist" in text

    ):

        scores["music"] += 3


    # Navigation context

    if (

        has_any(

            text,

            [

                "airport",

                "railway station",

                "bus station",

                "office",

                "college",

                "home"

            ]

        )

        and

        has_any(

            text,

            [

                "go",

                "take",

                "route",

                "way",

                "reach",

                "drive"

            ]

        )

    ):

        scores["navigation"] += 4


    # ---------------------------------
    # CHOOSE THE STRONGEST INTENT
    # ---------------------------------

    best_intent = max(

        scores,

        key=scores.get

    )


    confidence = scores[

        best_intent

    ]


    if confidence == 0:

        best_intent = "unknown"


    result = {

        "original_command":

        command,


        "normalized_command":

        text,


        "intent":

        best_intent,


        "confidence":

        confidence,


        "matched_keywords":

        matched.get(

            best_intent,

            []

        ),


        "temperature":

        temperature

    }


    print(

        "\nNAYA LANGUAGE UNDERSTANDING"

    )


    print(

        "Sentence:",

        command

    )


    print(

        "Intent:",

        result["intent"]

    )


    print(

        "Important words:",

        result["matched_keywords"]

    )


    print(

        "Confidence:",

        result["confidence"]

    )


    return result