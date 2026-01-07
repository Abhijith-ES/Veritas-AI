from flask import Flask, render_template, request, jsonify
import requests
import markdown
from config import CHAT_ENDPOINT, UPLOAD_ENDPOINT

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    responses = []

    for file in files:
        resp = requests.post(
            UPLOAD_ENDPOINT,
            files={"file": (file.filename, file.stream)},
        )

        if resp.status_code != 200:
            return jsonify({"error": resp.text}), 500

        responses.append(resp.json())

    return jsonify({"status": "success", "files": responses})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"answer": "<p>Please enter a question.</p>"})

    resp = requests.post(CHAT_ENDPOINT, json={"query": query})

    if resp.status_code != 200:
        return jsonify(
            {"answer": "<p>⚠️ Backend error. Please try again.</p>"}
        )

    backend_response = resp.json()
    answer_md = backend_response.get("answer", "")

    # Convert Markdown → HTML
    answer_html = markdown.markdown(
        answer_md,
        extensions=["extra", "nl2br"]
    )

    return jsonify({"answer": answer_html})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
