from flask import Flask, render_template, jsonify

app = Flask(__name__)


# Current NAYA information
naya_state = {

    "status": "READY",

    "message": 'Say "Hey NAYA" to begin',

    "destination": "Where would you like to go?",

    "song": "Your Drive Mix",

    "temperature": 22,

    "ac": "ON",

    "doors": "LOCKED",

    "sunroof": "CLOSED"
}


# Open the dashboard
@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# Send NAYA information to dashboard
@app.route("/api/status")
def get_status():

    return jsonify(
        naya_state
    )
@app.route(
    "/api/update",
    methods=["POST"]
)
def update_status():

    from flask import request

    new_information = request.get_json()

    if new_information:

        naya_state.update(
            new_information
        )

    return jsonify({

        "success": True,

        "state": naya_state
    })
    

if __name__ == "__main__":

    print(
        "NAYA futuristic infotainment "
        "is starting..."
    )

    print(
        "Open: http://127.0.0.1:5000"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )