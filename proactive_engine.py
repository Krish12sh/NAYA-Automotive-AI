# =====================================
# NAYA PROACTIVE INTELLIGENCE ENGINE
# =====================================

from journey_context import get_context


# =====================================
# ALERT MEMORY
# =====================================

# This prevents NAYA from repeating
# the same warning continuously.

active_alerts = set()


# =====================================
# CLEAR AN ALERT
# =====================================

def clear_alert(alert_name):

    if alert_name in active_alerts:

        active_alerts.remove(
            alert_name
        )


# =====================================
# CREATE A NEW ALERT
# =====================================

def create_alert(

    alert_name,

    speech,

    suggestion,

    priority="medium"

):

    # Do not repeat an alert
    # that has already been spoken.

    if alert_name in active_alerts:

        return None


    active_alerts.add(

        alert_name

    )


    return {

        "alert_name":
        alert_name,

        "speech":
        speech,

        "suggestion":
        suggestion,

        "priority":
        priority

    }


# =====================================
# CHECK LOW FUEL
# =====================================

def check_low_fuel(context):

    fuel = context.get(

        "fuel",

        100

    )


    # VERY LOW FUEL

    if fuel <= 10:

        return create_alert(

            alert_name=
            "very_low_fuel",

            speech=
            "Your fuel level is critically low "
            "at "

            + str(
                fuel
            )

            + " percent. I recommend finding "
            "a petrol station soon.",

            suggestion=
            "find_petrol_station",

            priority=
            "high"

        )


    # NORMAL LOW FUEL

    if fuel <= 20:

        return create_alert(

            alert_name=
            "low_fuel",

            speech=
            "Your fuel level is "

            + str(
                fuel
            )

            + " percent. Would you like me "
            "to find a nearby petrol station?",

            suggestion=
            "find_petrol_station",

            priority=
            "medium"

        )


    # CLEAR OLD ALERTS WHEN
    # THE FUEL LEVEL IS HEALTHY

    if fuel > 25:

        clear_alert(

            "low_fuel"

        )


        clear_alert(

            "very_low_fuel"

        )


    return None


# =====================================
# CHECK ESTIMATED RANGE
# =====================================

def check_low_range(context):

    estimated_range = context.get(

        "estimated_range",

        500

    )


    if estimated_range <= 50:

        return create_alert(

            alert_name=
            "low_driving_range",

            speech=
            "Your estimated driving range is "
            "only "

            + str(
                estimated_range
            )

            + " kilometres. Would you like "
            "me to search for a nearby "
            "petrol station?",

            suggestion=
            "find_petrol_station",

            priority=
            "high"

        )


    if estimated_range > 70:

        clear_alert(

            "low_driving_range"

        )


    return None


# =====================================
# CHECK DRIVER FATIGUE
# =====================================

def check_driver_state(context):

    driver_state = str(

        context.get(

            "driver_state",

            "NORMAL"

        )

    ).upper()


    tired_states = [

        "TIRED",

        "DROWSY",

        "FATIGUED",

        "SLEEPY"

    ]


    if driver_state in tired_states:

        return create_alert(

            alert_name=
            "driver_fatigue",

            speech=
            "You appear to be tired. "
            "For a safer journey, I recommend "
            "taking a short break. Would you "
            "like me to find a nearby cafe "
            "or rest stop?",

            suggestion=
            "find_rest_stop",

            priority=
            "high"

        )


    if driver_state == "NORMAL":

        clear_alert(

            "driver_fatigue"

        )


    return None


# =====================================
# CHECK CABIN TEMPERATURE
# =====================================

def check_cabin_temperature(context):

    temperature = context.get(

        "temperature",

        24

    )


    ac_status = str(

        context.get(

            "ac",

            "ON"

        )

    ).upper()


    if (

        temperature >= 29

        and

        ac_status == "OFF"

    ):

        return create_alert(

            alert_name=
            "hot_cabin",

            speech=
            "The cabin temperature is currently "

            + str(
                temperature
            )

            + " degrees and the air conditioning "
            "is off. Would you like me to turn "
            "on the climate system?",

            suggestion=
            "turn_on_climate",

            priority=
            "medium"

        )


    if (

        temperature < 27

        or

        ac_status == "ON"

    ):

        clear_alert(

            "hot_cabin"

        )


    return None


# =====================================
# CHECK SUNROOF DURING RAIN
# =====================================

def check_sunroof_weather(context):

    sunroof = str(

        context.get(

            "sunroof",

            "CLOSED"

        )

    ).upper()


    weather = str(

        context.get(

            "weather",

            "CLEAR"

        )

    ).upper()


    rainy_conditions = [

        "RAIN",

        "RAINY",

        "HEAVY RAIN",

        "THUNDERSTORM"

    ]


    if (

        sunroof == "OPEN"

        and

        weather in rainy_conditions

    ):

        return create_alert(

            alert_name=
            "sunroof_rain",

            speech=
            "Rain has been detected while "
            "the sunroof is open. Would you "
            "like me to close it?",

            suggestion=
            "close_sunroof",

            priority=
            "high"

        )


    if (

        sunroof == "CLOSED"

        or

        weather not in rainy_conditions

    ):

        clear_alert(

            "sunroof_rain"

        )


    return None


# =====================================
# CHECK UNLOCKED DOORS
# =====================================

def check_door_safety(context):

    doors = str(

        context.get(

            "doors",

            "LOCKED"

        )

    ).upper()


    vehicle_speed = context.get(

        "speed",

        0

    )


    if (

        doors == "UNLOCKED"

        and

        vehicle_speed > 10

    ):

        return create_alert(

            alert_name=
            "unlocked_while_moving",

            speech=
            "The vehicle is moving while "
            "the doors are unlocked. Would "
            "you like me to lock the doors?",

            suggestion=
            "lock_doors",

            priority=
            "high"

        )


    if (

        doors == "LOCKED"

        or

        vehicle_speed <= 10

    ):

        clear_alert(

            "unlocked_while_moving"

        )


    return None


# =====================================
# RUN ALL PROACTIVE CHECKS
# =====================================

def check_proactive_events():

    context = get_context()


    checks = [

        check_low_fuel,

        check_low_range,

        check_driver_state,

        check_cabin_temperature,

        check_sunroof_weather,

        check_door_safety

    ]


    alerts = []


    for check in checks:

        alert = check(

            context

        )


        if alert:

            alerts.append(

                alert

            )


    # HIGH-PRIORITY ALERTS
    # SHOULD APPEAR FIRST

    priority_order = {

        "high":
        1,

        "medium":
        2,

        "low":
        3

    }


    alerts.sort(

        key=lambda alert:

        priority_order.get(

            alert.get(

                "priority",

                "low"

            ),

            3

        )

    )


    return alerts


# =====================================
# GET THE MOST IMPORTANT ALERT
# =====================================

def get_next_proactive_alert():

    alerts = (

        check_proactive_events()

    )


    if not alerts:

        return None


    return alerts[0]


# =====================================
# RESET ALERT MEMORY
# =====================================

def reset_proactive_alerts():

    active_alerts.clear()