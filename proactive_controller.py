# =====================================
# NAYA PROACTIVE CONTROLLER
# =====================================

from proactive_engine import (
    get_next_proactive_alert
)

from journey_context import (
    update_context
)


# =====================================
# CHECK FOR A PROACTIVE SUGGESTION
# =====================================

def check_for_proactive_suggestion():

    alert = (
        get_next_proactive_alert()
    )

    if not alert:

        return None


    print()

    print(
        "========== PROACTIVE ALERT =========="
    )

    print(
        "Alert:",
        alert.get(
            "alert_name"
        )
    )

    print(
        "Priority:",
        str(
            alert.get(
                "priority",
                "medium"
            )
        ).upper()
    )

    print(
        "Suggestion:",
        alert.get(
            "suggestion"
        )
    )

    print(
        "====================================="
    )

    print()


    return alert


# =====================================
# CONVERT DRIVER APPROVAL INTO ACTION
# =====================================

def get_suggested_action(

    suggestion

):

    suggestion = str(

        suggestion

    ).strip().lower()


    if (
        suggestion
        ==
        "find_petrol_station"
    ):

        return {

            "type":
            "find_nearby",

            "category":
            "petrol pump"

        }


    if (
        suggestion
        ==
        "find_rest_stop"
    ):

        return {

            "type":
            "find_nearby",

            "category":
            "cafe or rest stop"

        }


    if (
        suggestion
        ==
        "turn_on_climate"
    ):

        return {

            "type":
            "climate_on"

        }


    if (
        suggestion
        ==
        "close_sunroof"
    ):

        return {

            "type":
            "close_sunroof"

        }


    if (
        suggestion
        ==
        "lock_doors"
    ):

        return {

            "type":
            "lock_doors"

        }


    return None


# =====================================
# SIMULATION HELPERS
# =====================================

def simulate_low_fuel():

    update_context(

        fuel=15,

        estimated_range=70

    )


    return (

        "Low-fuel condition simulated."

    )


def simulate_critical_fuel():

    update_context(

        fuel=8,

        estimated_range=35

    )


    return (

        "Critical-fuel condition simulated."

    )


def simulate_driver_fatigue():

    update_context(

        driver_state="TIRED"

    )


    return (

        "Driver-fatigue condition simulated."

    )


def simulate_hot_cabin():

    update_context(

        temperature=30,

        ac="OFF"

    )


    return (

        "Hot-cabin condition simulated."

    )


def simulate_rain_with_open_sunroof():

    update_context(

        weather="RAIN",

        sunroof="OPEN"

    )


    return (

        "Rain and open-sunroof "
        "condition simulated."

    )


def simulate_unlocked_moving_vehicle():

    update_context(

        speed=45,

        doors="UNLOCKED"

    )


    return (

        "Moving vehicle with unlocked "
        "doors simulated."

    )


def restore_safe_vehicle_state():

    update_context(

        driver_state="NORMAL",

        speed=0,

        weather="CLEAR",

        temperature=24,

        ac="ON",

        fuel=72,

        estimated_range=410,

        doors="LOCKED",

        sunroof="CLOSED"

    )


    return (

        "Safe vehicle state restored."

    )