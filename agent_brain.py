import json
import urllib.request
import urllib.error

from journey_context import get_context_for_ai


# =====================================
# OLLAMA CONFIGURATION
# =====================================

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL_NAME = "llama3.2:3b"


# =====================================
# NAYA PERSONALITY
# =====================================

SYSTEM_PROMPT = """
You are NAYA, a secure, intelligent, context-aware
automotive AI companion.

You are not only a command assistant.

You can:

- Talk naturally with the driver
- Answer general knowledge questions
- Continue conversations using memory
- Understand informal and imperfect English
- Understand indirect requests
- Understand several requests in one sentence
- Help with navigation
- Control simulated vehicle features
- Play requested music
- Use live journey and vehicle information
- Give concise spoken responses suitable for driving

You should sound calm, intelligent, natural and helpful.

Do not repeatedly introduce yourself.

Do not mention JSON, prompts, action objects,
language models or internal software systems.

Use the live vehicle context when it is relevant.

If live context says:

Current destination:
Hyderabad Airport

and the driver asks:

"Where are we going?"

Answer using Hyderabad Airport.

If live context says:

Cabin temperature:
22 degrees Celsius

and the driver asks:

"What is the temperature?"

Answer that the cabin is set to 22 degrees.

If live context says:

Current music:
Kesariya by Arijit Singh

and the driver asks:

"What song is playing?"

Answer using that information.

Do not invent vehicle information.

If information is unavailable,
say that it is currently unavailable.


AVAILABLE ACTIONS


1. NAVIGATION

Use:

{
    "type": "navigate",
    "destination": "Hyderabad Airport"
}

Use when the driver asks to:

go somewhere

navigate somewhere

drive somewhere

get directions

take them somewhere


2. NEARBY PLACE SEARCH

Use:

{
    "type": "find_nearby",
    "category": "petrol pump"
}

Possible examples:

petrol pump

EV charging station

restaurant

cafe

hospital

parking

ATM

hotel


3. PLAY MUSIC

Use:

{
    "type": "play_music",
    "query": "Kesariya by Arijit Singh"
}

Use for:

songs

artists

albums

playlists

genres

music moods


4. PAUSE MUSIC

Use:

{
    "type": "pause_music"
}


5. SET TEMPERATURE

Use:

{
    "type": "set_temperature",
    "temperature": 22
}

Valid temperature:

16 to 30 degrees Celsius


6. TURN CLIMATE ON

Use:

{
    "type": "climate_on"
}


7. TURN CLIMATE OFF

Use:

{
    "type": "climate_off"
}


8. MAKE THE CABIN COOLER

Use:

{
    "type": "decrease_temperature"
}

Understand phrases such as:

"It is hot in here."

"The cabin feels warm."

"Make it cooler."

"Can you cool the car down?"


9. MAKE THE CABIN WARMER

Use:

{
    "type": "increase_temperature"
}

Understand phrases such as:

"I am cold."

"It is freezing."

"Make it warmer."


10. OPEN WINDOW

Use:

{
    "type": "open_window",
    "window": "driver"
}

Valid values:

driver

passenger

rear_left

rear_right

all


11. CLOSE WINDOW

Use:

{
    "type": "close_window",
    "window": "driver"
}


12. OPEN SUNROOF

Use:

{
    "type": "open_sunroof"
}


13. CLOSE SUNROOF

Use:

{
    "type": "close_sunroof"
}


14. LOCK DOORS

Use:

{
    "type": "lock_doors"
}


15. UNLOCK DOORS

Use:

{
    "type": "unlock_doors"
}


16. VEHICLE STATUS

Use:

{
    "type": "vehicle_status"
}

Use when the driver asks for a complete vehicle report.

For simple questions such as:

"What is my fuel level?"

"What is the cabin temperature?"

"Which song is playing?"

"Where are we going?"

answer directly using live context.

Do not create vehicle_status unless a broader
vehicle report is requested.


IMPORTANT INTELLIGENCE RULES

Understand meaning instead of exact wording.

If the driver is only talking,
respond naturally with no actions.

If the driver asks a general question,
answer naturally with no actions.

If several tasks are requested,
create one action for every task.

Example:

"Take me to Hyderabad Airport,
set the cabin to 22 degrees,
and play Kesariya."

Create:

navigate

set_temperature

play_music


Understand indirect language.

"It is hot in here."

means:

decrease_temperature


"I am freezing."

means:

increase_temperature


Use conversation history.

If the driver says:

"I am travelling to Hyderabad Airport."

and later says:

"Take me there."

understand that "there" means Hyderabad Airport.


Use live vehicle context.

If the current destination is Hyderabad Airport
and the driver asks:

"Where are we going?"

answer using the current destination.


Do not create an action when the user only asks
about the current vehicle state.

Example:

"What is the cabin temperature?"

Answer from live context.

Do not create set_temperature.


Do not falsely claim an action has happened.

The AI creates an action plan.

Another part of NAYA executes the action.

You may say:

"I can start navigation to Kolkata."

"I can set the cabin to 22 degrees."

"I'll prepare that for you."


SECURITY RULES

General conversation:

risk_level = "none"


General questions:

risk_level = "none"


Current-context questions:

risk_level = "none"


Navigation:

risk_level = "low"


Nearby searches:

risk_level = "low"


Music:

risk_level = "low"


Climate:

risk_level = "medium"


Windows:

risk_level = "medium"


Sunroof:

risk_level = "medium"


Locking doors:

risk_level = "medium"


Unlocking doors:

risk_level = "high"

confirmation_required = true


For multiple actions,
use the highest risk level.


OUTPUT FORMAT

Return only valid JSON.

Do not use Markdown.

Do not write anything before the JSON.

Do not write anything after the JSON.

Always return:

{
    "speech": "Natural response for the driver",
    "actions": [],
    "risk_level": "none",
    "confirmation_required": false
}
"""


# =====================================
# CONVERSATION MEMORY
# =====================================

conversation_history = [

    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }

]


# =====================================
# CLEAN JSON
# =====================================

def clean_json_text(text):

    cleaned_text = text.strip()

    if cleaned_text.startswith(
        "```json"
    ):

        cleaned_text = (
            cleaned_text[7:]
        )

    elif cleaned_text.startswith(
        "```"
    ):

        cleaned_text = (
            cleaned_text[3:]
        )

    if cleaned_text.endswith(
        "```"
    ):

        cleaned_text = (
            cleaned_text[:-3]
        )

    return cleaned_text.strip()


# =====================================
# VALIDATE ACTIONS
# =====================================

def validate_actions(actions):

    if not isinstance(
        actions,
        list
    ):

        return []

    allowed_actions = [

        "navigate",

        "find_nearby",

        "play_music",

        "pause_music",

        "set_temperature",

        "climate_on",

        "climate_off",

        "increase_temperature",

        "decrease_temperature",

        "open_window",

        "close_window",

        "open_sunroof",

        "close_sunroof",

        "lock_doors",

        "unlock_doors",

        "vehicle_status"

    ]

    validated_actions = []

    for action in actions:

        if not isinstance(
            action,
            dict
        ):

            continue

        action_type = (
            action.get(
                "type"
            )
        )

        if (
            action_type
            not in
            allowed_actions
        ):

            continue

        validated_actions.append(
            action
        )

    return validated_actions


# =====================================
# VALIDATE COMPLETE RESPONSE
# =====================================

def validate_response(result):

    if not isinstance(
        result,
        dict
    ):

        raise ValueError(
            "AI response is not a JSON object."
        )

    speech = result.get(
        "speech",
        ""
    )

    if not isinstance(
        speech,
        str
    ):

        speech = str(
            speech
        )

    actions = validate_actions(

        result.get(
            "actions",
            []
        )

    )

    risk_level = result.get(
        "risk_level",
        "none"
    )

    valid_risk_levels = [

        "none",

        "low",

        "medium",

        "high"

    ]

    if (
        risk_level
        not in
        valid_risk_levels
    ):

        risk_level = "none"

    confirmation_required = bool(

        result.get(

            "confirmation_required",

            False

        )

    )

    # =================================
    # ENFORCE SECURITY IN CODE
    # =================================

    for action in actions:

        if (
            action.get(
                "type"
            )
            ==
            "unlock_doors"
        ):

            risk_level = "high"

            confirmation_required = True

    return {

        "speech":
        speech.strip(),

        "actions":
        actions,

        "risk_level":
        risk_level,

        "confirmation_required":
        confirmation_required

    }


# =====================================
# MAIN NAYA AI FUNCTION
# =====================================

def understand_with_agent(
    user_message
):

    live_context = (
        get_context_for_ai()
    )

    contextual_message = f"""
CURRENT LIVE VEHICLE INFORMATION

{live_context}


DRIVER'S NEW MESSAGE

{user_message}
""".strip()

    conversation_history.append(

        {

            "role": "user",

            "content":
            contextual_message

        }

    )

    request_data = {

        "model":
        MODEL_NAME,

        "messages":
        conversation_history,

        "stream":
        False,

        "format":
        "json",

        "options": {

            "temperature":
            0.25

        }

    }

    encoded_data = json.dumps(

        request_data

    ).encode(
        "utf-8"
    )

    request = urllib.request.Request(

        OLLAMA_URL,

        data=encoded_data,

        headers={

            "Content-Type":
            "application/json"

        },

        method="POST"

    )

    try:

        with urllib.request.urlopen(

            request,

            timeout=120

        ) as response:

            ollama_result = json.loads(

                response
                .read()
                .decode(
                    "utf-8"
                )

            )

        raw_reply = (

            ollama_result

            .get(
                "message",
                {}
            )

            .get(
                "content",
                ""
            )

        )

        cleaned_reply = (
            clean_json_text(
                raw_reply
            )
        )

        parsed_reply = json.loads(
            cleaned_reply
        )

        final_result = (
            validate_response(
                parsed_reply
            )
        )

        conversation_history.append(

            {

                "role":
                "assistant",

                "content":
                json.dumps(
                    final_result
                )

            }

        )

        return final_result

    except urllib.error.URLError:

        return {

            "speech":

            "I cannot connect to my local "
            "AI brain. Please make sure "
            "Ollama is running.",

            "actions":
            [],

            "risk_level":
            "none",

            "confirmation_required":
            False

        }

    except json.JSONDecodeError:

        return {

            "speech":

            "I understood your request, "
            "but I could not create a "
            "reliable response.",

            "actions":
            [],

            "risk_level":
            "none",

            "confirmation_required":
            False

        }

    except Exception as error:

        return {

            "speech":

            "I had a problem while "
            "understanding the request. "

            + str(
                error
            ),

            "actions":
            [],

            "risk_level":
            "none",

            "confirmation_required":
            False

        }


# =====================================
# RESET CONVERSATION
# =====================================

def reset_conversation():

    conversation_history.clear()

    conversation_history.append(

        {

            "role":
            "system",

            "content":
            SYSTEM_PROMPT

        }

    )