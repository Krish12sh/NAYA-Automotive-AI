import speech_recognition as sr
import pyttsx3
import webbrowser
import urllib.parse
import requests
import time
import pywhatkit

from agent_brain import understand_with_agent

from journey_context import (
    update_context,
    get_context,
    display_context
)

from proactive_controller import (
    check_for_proactive_suggestion,
    get_suggested_action,
    simulate_low_fuel,
    simulate_critical_fuel,
    simulate_driver_fatigue,
    simulate_hot_cabin,
    simulate_rain_with_open_sunroof,
    simulate_unlocked_moving_vehicle,
    restore_safe_vehicle_state
)


# =====================================
# NAYA SETTINGS
# =====================================

DASHBOARD_URL = "http://127.0.0.1:5000"

recognizer = sr.Recognizer()

current_temperature = 24

pending_suggestion = None


# =====================================
# DASHBOARD
# =====================================

def update_dashboard(data):

    try:

        requests.post(

            DASHBOARD_URL + "/api/update",

            json=data,

            timeout=2

        )

    except requests.RequestException:

        print(

            "Dashboard connection unavailable."

        )


# =====================================
# NAYA SPEAKS
# =====================================

def speak(message):

    if not message:

        return

    message = str(message)

    print(

        "\nNAYA:",

        message

    )

    update_dashboard({

        "status":
        "SPEAKING",

        "message":
        message

    })

    try:

        engine = pyttsx3.init()

        engine.setProperty(

            "rate",

            175

        )

        engine.setProperty(

            "volume",

            1.0

        )

        engine.say(

            message

        )

        engine.runAndWait()

        engine.stop()

    except Exception as error:

        print(

            "Voice output error:",

            error

        )


# =====================================
# NAYA LISTENS
# =====================================

def listen(

    timeout=10,

    phrase_time_limit=25

):

    update_dashboard({

        "status":
        "LISTENING",

        "message":
        "I am listening..."

    })

    try:

        with sr.Microphone() as source:

            print(

                "\nListening..."

            )

            recognizer.adjust_for_ambient_noise(

                source,

                duration=0.5

            )

            audio = recognizer.listen(

                source,

                timeout=timeout,

                phrase_time_limit=
                phrase_time_limit

            )

        update_dashboard({

            "status":
            "PROCESSING",

            "message":
            "Understanding your request..."

        })

        print(

            "Recognizing your voice..."

        )

        command = (

            recognizer

            .recognize_google(

                audio,

                language="en-IN"

            )

            .strip()

        )

        print(

            "YOU:",

            command

        )

        return command

    except sr.WaitTimeoutError:

        print(

            "No speech detected."

        )

        return ""

    except sr.UnknownValueError:

        speak(

            "I heard you, but I could not "
            "understand that clearly."

        )

        return ""

    except sr.RequestError:

        speak(

            "Speech recognition is currently "
            "unavailable."

        )

        return ""

    except Exception as error:

        print(

            "Microphone error:",

            error

        )

        return ""


# =====================================
# CLEAN WAKE WORD
# =====================================

def clean_command(command):

    command = str(

        command

    ).strip()

    wake_words = [

        "hey naya",

        "hello naya",

        "hi naya",

        "okay naya",

        "ok naya",

        "naya",

        "hey neya",

        "hello neya",

        "neya",

        "hey naiya",

        "naiya"

    ]

    lower_command = (

        command.lower()

    )

    for wake_word in wake_words:

        if lower_command.startswith(

            wake_word

        ):

            command = command[

                len(wake_word):

            ]

            command = command.lstrip(

                " ,.-"

            )

            break

    return command.strip()


# =====================================
# GOOGLE MAPS NAVIGATION
# =====================================

def navigate(destination):

    destination = str(

        destination

    ).strip()

    if not destination:

        speak(

            "Where would you like to go?"

        )

        return

    encoded_destination = (

        urllib.parse.quote(

            destination

        )

    )

    maps_url = (

        "https://www.google.com/maps/dir/"

        "?api=1"

        "&destination="

        + encoded_destination

        + "&travelmode=driving"

    )

    update_context(

        destination=destination,

        navigation_active=True

    )

    update_dashboard({

        "destination":

        "Navigating to "

        + destination,

        "status":

        "NAVIGATING",

        "message":

        "Navigation active to "

        + destination

    })

    webbrowser.open(

        maps_url

    )

    print(

        "ACTION: Navigation →",

        destination

    )


# =====================================
# NEARBY SEARCH
# =====================================

def nearby(category):

    category = str(

        category

    ).strip()

    if not category:

        return

    search_query = (

        urllib.parse.quote(

            category

            + " near me"

        )

    )

    maps_url = (

        "https://www.google.com/maps/search/"

        "?api=1"

        "&query="

        + search_query

    )

    update_dashboard({

        "status":

        "SEARCHING",

        "message":

        "Finding nearby "

        + category

    })

    webbrowser.open(

        maps_url

    )

    print(

        "ACTION: Nearby search →",

        category

    )


# =====================================
# DIRECT YOUTUBE MUSIC
# =====================================

def play_music(music_query):

    music_query = str(

        music_query

    ).strip()

    if not music_query:

        speak(

            "What would you like to hear?"

        )

        return

    update_context(

        current_music=music_query,

        music_status="PLAYING"

    )

    update_dashboard({

        "song":

        music_query.title(),

        "status":

        "PLAYING",

        "message":

        "Playing "

        + music_query

    })

    print(

        "ACTION: Playing →",

        music_query

    )

    try:

        pywhatkit.playonyt(

            music_query

        )

    except Exception as error:

        print(

            "Direct playback error:",

            error

        )

        query = urllib.parse.quote(

            music_query

            + " official music"

        )

        webbrowser.open(

            "https://www.youtube.com/results"

            "?search_query="

            + query

        )


# =====================================
# TEMPERATURE
# =====================================

def set_temperature(temperature):

    global current_temperature

    try:

        temperature = int(

            float(

                temperature

            )

        )

    except (

        TypeError,

        ValueError

    ):

        return

    if temperature < 16:

        temperature = 16

    if temperature > 30:

        temperature = 30

    current_temperature = temperature

    update_context(

        temperature=
        current_temperature,

        ac="ON"

    )

    update_dashboard({

        "temperature":
        current_temperature,

        "ac":
        "ON",

        "status":
        "CLIMATE",

        "message":

        "Cabin set to "

        + str(

            current_temperature

        )

        + " degrees"

    })

    print(

        "ACTION: Temperature →",

        str(

            current_temperature

        )

        + "°C"

    )


def change_temperature(amount):

    set_temperature(

        current_temperature

        + amount

    )


# =====================================
# EXECUTE AN ACTION
# =====================================

def execute_action(action):

    action_type = str(

        action.get(

            "type",

            ""

        )

    ).lower()


    if action_type == "navigate":

        navigate(

            action.get(

                "destination",

                ""

            )

        )


    elif action_type == "find_nearby":

        nearby(

            action.get(

                "category",

                ""

            )

        )


    elif action_type == "play_music":

        play_music(

            action.get(

                "query",

                ""

            )

        )


    elif action_type == "pause_music":

        update_context(

            music_status="PAUSED"

        )

        update_dashboard({

            "song":
            "Paused",

            "status":
            "MEDIA",

            "message":
            "Music paused"

        })


    elif action_type == "set_temperature":

        set_temperature(

            action.get(

                "temperature",

                24

            )

        )


    elif action_type == "climate_on":

        update_context(

            ac="ON"

        )

        update_dashboard({

            "ac":
            "ON",

            "status":
            "CLIMATE",

            "message":
            "Climate system is on"

        })


    elif action_type == "climate_off":

        update_context(

            ac="OFF"

        )

        update_dashboard({

            "ac":
            "OFF",

            "status":
            "CLIMATE",

            "message":
            "Climate system is off"

        })


    elif action_type == "decrease_temperature":

        change_temperature(

            -2

        )


    elif action_type == "increase_temperature":

        change_temperature(

            2

        )


    elif action_type in [

        "open_window",

        "close_window"

    ]:

        window = str(

            action.get(

                "window",

                "driver"

            )

        ).lower()

        state = (

            "OPEN"

            if action_type

            == "open_window"

            else "CLOSED"

        )

        if window == "all":

            update_context(

                driver_window=state,

                passenger_window=state,

                rear_left_window=state,

                rear_right_window=state

            )

        else:

            context_key = (

                window

                + "_window"

            )

            update_context(

                **{

                    context_key:
                    state

                }

            )

        update_dashboard({

            "status":

            "VEHICLE CONTROL",

            "message":

            window.replace(

                "_",

                " "

            ).title()

            + " window "

            + state.lower()

        })


    elif action_type == "open_sunroof":

        update_context(

            sunroof="OPEN"

        )

        update_dashboard({

            "sunroof":
            "OPEN",

            "status":
            "VEHICLE CONTROL",

            "message":
            "Sunroof opened"

        })


    elif action_type == "close_sunroof":

        update_context(

            sunroof="CLOSED"

        )

        update_dashboard({

            "sunroof":
            "CLOSED",

            "status":
            "VEHICLE CONTROL",

            "message":
            "Sunroof closed"

        })


    elif action_type == "lock_doors":

        update_context(

            doors="LOCKED"

        )

        update_dashboard({

            "doors":
            "LOCKED",

            "status":
            "SECURED",

            "message":
            "Doors locked"

        })


    elif action_type == "unlock_doors":

        update_context(

            doors="UNLOCKED"

        )

        update_dashboard({

            "doors":
            "UNLOCKED",

            "status":
            "VEHICLE CONTROL",

            "message":
            "Doors unlocked"

        })


    elif action_type == "vehicle_status":

        context = get_context()

        status_message = (

            "Fuel is at "

            + str(

                context["fuel"]

            )

            + " percent. Estimated range is "

            + str(

                context[

                    "estimated_range"

                ]

            )

            + " kilometres. Cabin temperature is "

            + str(

                context["temperature"]

            )

            + " degrees."

        )

        speak(

            status_message

        )


# =====================================
# SECURITY CONFIRMATION
# =====================================

def request_security_confirmation():

    speak(

        "This is a security-sensitive "
        "vehicle action. Please say "
        "confirm or cancel."

    )

    answer = listen(

        timeout=8,

        phrase_time_limit=5

    ).lower()

    approval_words = [

        "confirm",

        "yes",

        "continue",

        "proceed",

        "approve",

        "do it"

    ]

    return any(

        word in answer

        for word in approval_words

    )


# =====================================
# PROACTIVE SUGGESTION
# =====================================

def run_proactive_check():

    global pending_suggestion

    alert = (

        check_for_proactive_suggestion()

    )

    if not alert:

        return

    pending_suggestion = (

        alert.get(

            "suggestion"

        )

    )

    speak(

        alert.get(

            "speech"

        )

    )


# =====================================
# HANDLE YES OR NO
# =====================================

def handle_pending_suggestion(command):

    global pending_suggestion

    if not pending_suggestion:

        return False

    command = command.lower()

    approval_words = [

        "yes",

        "sure",

        "okay",

        "ok",

        "please do",

        "do it",

        "find one",

        "go ahead",

        "proceed"

    ]

    rejection_words = [

        "no",

        "not now",

        "cancel",

        "don't",

        "do not",

        "later"

    ]

    if any(

        phrase in command

        for phrase in rejection_words

    ):

        speak(

            "Okay. I will not take "
            "that action right now."

        )

        pending_suggestion = None

        return True

    if any(

        phrase in command

        for phrase in approval_words

    ):

        action = (

            get_suggested_action(

                pending_suggestion

            )

        )

        pending_suggestion = None

        if action:

            execute_action(

                action

            )

            speak(

                "Done. I have started "
                "that for you."

            )

        return True

    return False


# =====================================
# DEMO COMMANDS
# =====================================

def handle_demo_command(command):

    command = command.lower()


    if "simulate low fuel" in command:

        speak(

            simulate_low_fuel()

        )

        run_proactive_check()

        return True


    if (

        "simulate critical fuel"

        in command

    ):

        speak(

            simulate_critical_fuel()

        )

        run_proactive_check()

        return True


    if (

        "simulate driver fatigue"

        in command

        or

        "simulate tired driver"

        in command

    ):

        speak(

            simulate_driver_fatigue()

        )

        run_proactive_check()

        return True


    if "simulate hot cabin" in command:

        speak(

            simulate_hot_cabin()

        )

        run_proactive_check()

        return True


    if (

        "simulate rain"

        in command

    ):

        speak(

            simulate_rain_with_open_sunroof()

        )

        run_proactive_check()

        return True


    if (

        "simulate unlocked doors"

        in command

    ):

        speak(

            simulate_unlocked_moving_vehicle()

        )

        run_proactive_check()

        return True


    if (

        "restore normal state"

        in command

        or

        "restore safe state"

        in command

    ):

        speak(

            restore_safe_vehicle_state()

        )

        return True


    if (

        "show live context"

        in command

        or

        "show vehicle context"

        in command

    ):

        display_context()

        speak(

            "I displayed the live vehicle "
            "context in the terminal."

        )

        return True


    return False


# =====================================
# PROCESS DRIVER REQUEST
# =====================================

def process_command(command):

    command = clean_command(

        command

    )

    if not command:

        return


    if handle_pending_suggestion(

        command

    ):

        return


    if handle_demo_command(

        command

    ):

        return


    update_dashboard({

        "status":

        "THINKING",

        "message":

        "NAYA is reasoning..."

    })

    print(

        "\nNAYA AI IS THINKING..."

    )

    result = (

        understand_with_agent(

            command

        )

    )

    speech = str(

        result.get(

            "speech",

            ""

        )

    )

    actions = result.get(

        "actions",

        []

    )

    confirmation_required = bool(

        result.get(

            "confirmation_required",

            False

        )

    )

    print(

        "\n========== AI PLAN =========="

    )

    print(

        "Speech:",

        speech

    )

    print(

        "Actions:",

        actions

    )

    print(

        "Risk:",

        result.get(

            "risk_level",

            "none"

        )

    )

    print(

        "================================"

    )


    if confirmation_required:

        if not request_security_confirmation():

            speak(

                "The sensitive action "
                "has been cancelled."

            )

            return


    for action in actions:

        execute_action(

            action

        )

        time.sleep(

            0.3

        )


    if speech:

        speak(

            speech

        )


    display_context()


    run_proactive_check()


# =====================================
# START NAYA
# =====================================

if __name__ == "__main__":

    update_dashboard({

        "status":
        "READY",

        "message":
        "NAYA is ready"

    })

    speak(

        "NAYA automotive AI companion "
        "is ready."

    )

    while True:

        try:

            command = listen()

            if not command:

                continue

            lower_command = (

                command.lower()

            )

            stop_phrases = [

                "stop naya",

                "exit naya",

                "goodbye naya",

                "shut down naya",

                "go offline naya"

            ]

            if any(

                phrase in lower_command

                for phrase in stop_phrases

            ):

                speak(

                    "Goodbye Krish. "
                    "Drive safely."

                )

                update_dashboard({

                    "status":
                    "OFFLINE",

                    "message":
                    "NAYA is offline"

                })

                break

            process_command(

                command

            )

            time.sleep(

                0.7

            )

        except KeyboardInterrupt:

            print(

                "\nNAYA stopped manually."

            )

            break

        except Exception as error:

            print(

                "NAYA runtime error:",

                error

            )

            time.sleep(

                2

            )