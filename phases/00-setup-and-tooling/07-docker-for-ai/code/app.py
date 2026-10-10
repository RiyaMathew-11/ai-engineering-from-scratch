from flask import Flask, jsonify

app = Flask(__name__)
@app.get("/")
def index():
    return jsonify(status="ok")

app.run(host="0.0.0.0", port=5000)