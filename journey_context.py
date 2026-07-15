# =====================================
# NAYA LIVE JOURNEY CONTEXT
# =====================================

journey_context = {

    # =================================
    # DRIVER
    # =================================

    "driver_name":
        "Krish",

    "driver_state":
        "NORMAL",


    # =================================
    # NAVIGATION
    # =================================

    "current_location":
        "Current vehicle location",

    "destination":
        None,

    "navigation_active":
        False,


    # =================================
    # VEHICLE MOVEMENT
    # =================================

    "speed":
        0,


    # =================================
    # WEATHER
    # =================================

    "weather":
        "CLEAR",


    # =================================
    # CLIMATE
    # =================================

    "temperature":
        24,

    "ac":
        "ON",


    # =================================
    # FUEL AND RANGE
    # =================================

    "fuel":
        72,

    "estimated_range":
        410,


    # =================================
    # VEHICLE SECURITY
    # =================================

    "doors":
        "LOCKED",


    # =================================
    # WINDOWS
    # =================================

    "driver_window":
        "CLOSED",

    "passenger_window":
        "CLOSED",

    "rear_left_window":
        "CLOSED",

    "rear_right_window":
        "CLOSED",


    # =================================
    # SUNROOF
    # =================================

    "sunroof":
        "CLOSED",


    # =================================
    # MEDIA
    # =================================

    "current_music":
        None,

    "music_status":
        "STOPPED"

}


# =====================================
# UPDATE JOURNEY CONTEXT
# =====================================

def update_context(**changes):

    for key, value in changes.items():

        if key in journey_context:

            journey_context[key] = value

        else:

            print(

                "UNKNOWN CONTEXT VALUE:",

                key

            )


    return journey_context.copy()


# =====================================
# GET COMPLETE CONTEXT
# =====================================

def get_context():

    return journey_context.copy()


# =====================================
# GET ONE CONTEXT VALUE
# =====================================

def get_context_value(

    key,

    default=None

):

    return journey_context.get(

        key,

        default

    )


# =====================================
# CREATE LIVE CONTEXT FOR NAYA AI
# =====================================

def get_context_for_ai():

    destination = (

        journey_context[

            "destination"

        ]

        or

        "No destination selected"

    )


    current_music = (

        journey_context[

            "current_music"

        ]

        or

        "No music playing"

    )


    return f"""
LIVE VEHICLE AND JOURNEY CONTEXT

Driver:
{journey_context["driver_name"]}

Driver state:
{journey_context["driver_state"]}

Current location:
{journey_context["current_location"]}

Current destination:
{destination}

Navigation active:
{journey_context["navigation_active"]}

Vehicle speed:
{journey_context["speed"]} kilometres per hour

Weather:
{journey_context["weather"]}

Cabin temperature:
{journey_context["temperature"]} degrees Celsius

Air conditioning:
{journey_context["ac"]}

Fuel level:
{journey_context["fuel"]} percent

Estimated driving range:
{journey_context["estimated_range"]} kilometres

Door status:
{journey_context["doors"]}

Driver window:
{journey_context["driver_window"]}

Passenger window:
{journey_context["passenger_window"]}

Rear-left window:
{journey_context["rear_left_window"]}

Rear-right window:
{journey_context["rear_right_window"]}

Sunroof:
{journey_context["sunroof"]}

Current music:
{current_music}

Music status:
{journey_context["music_status"]}
""".strip()


# =====================================
# DISPLAY CONTEXT IN TERMINAL
# =====================================

def display_context():

    print()

    print(

        "========== NAYA LIVE CONTEXT =========="

    )


    for key, value in (

        journey_context.items()

    ):

        readable_key = (

            key

            .replace(

                "_",

                " "

            )

            .title()

        )


        print(

            readable_key

            + ":",

            value

        )


    print(

        "======================================="

    )

    print()


# =====================================
# RESET CONTEXT
# =====================================

def reset_context():

    journey_context.update({

        "driver_name":
            "Krish",

        "driver_state":
            "NORMAL",

        "current_location":
            "Current vehicle location",

        "destination":
            None,

        "navigation_active":
            False,

        "speed":
            0,

        "weather":
            "CLEAR",

        "temperature":
            24,

        "ac":
            "ON",

        "fuel":
            72,

        "estimated_range":
            410,

        "doors":
            "LOCKED",

        "driver_window":
            "CLOSED",

        "passenger_window":
            "CLOSED",

        "rear_left_window":
            "CLOSED",

        "rear_right_window":
            "CLOSED",

        "sunroof":
            "CLOSED",

        "current_music":
            None,

        "music_status":
            "STOPPED"

    })


    return journey_context.copy()