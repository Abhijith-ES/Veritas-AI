const chatBox = document.getElementById("chatBox");
let documentsUploaded = false;

function showAlert() {
    document.getElementById("systemAlert").classList.remove("hidden");
}

function closeAlert() {
    document.getElementById("systemAlert").classList.add("hidden");
}


function showIntroMessage() {
    const introText = `
        <p><strong>Hi, I’m Veritas AI !</strong><br>
            I’m a document-grounded AI assistant that answers questions strictly
            based on the files you upload.<br>
            Upload your documents to get started.
        </p>
    `;

    appendMessage(introText, "bot");
}


function appendMessage(html, sender, isRefusal = false) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message-row", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("message-bubble");

    if (isRefusal) bubble.classList.add("refusal");

    // IMPORTANT: render HTML (for bold, lists, etc.)
    bubble.innerHTML = html;

    wrapper.appendChild(bubble);
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;

    return wrapper;
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const query = input.value.trim();
    if (!query) return;

    // 🚨 Guard: No documents uploaded
    if (!documentsUploaded) {
        showAlert();
        return;
    }

    closeAlert();

    // User bubble
    appendMessage(query, "user");
    input.value = "";

    // Thinking bubble
    const thinkingRow = appendMessage(
        "<em>Veritas is thinking…</em>",
        "bot"
    );

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
        chatBox.removeChild(thinkingRow);

        const answer = data.answer || "";
        const isRefusal =
            answer.toLowerCase().includes("not available");

        appendMessage(answer, "bot", isRefusal);
    })
    .catch(() => {
        chatBox.removeChild(thinkingRow);
        appendMessage(
            "<p>⚠️ Something went wrong. Please try again.</p>",
            "bot",
            true
        );
    });
}

function uploadFiles() {
    const files = document.getElementById("fileInput").files;
    if (!files.length) return;

    const formData = new FormData();
    for (let f of files) {
        formData.append("files", f);
    }

    const status = document.getElementById("uploadStatus");
    const fileList = document.getElementById("uploadedFiles");

    status.innerText = "Uploading…";

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(() => {
        status.innerText = "Documents Uploaded successfully.";
        documentsUploaded = true;

        // Append uploaded files to list
        for (let file of files) {
            const li = document.createElement("li");

            const sizeKB = (file.size / 1024).toFixed(1);
            const size =
                sizeKB > 1024
                    ? (sizeKB / 1024).toFixed(1) + " MB"
                    : sizeKB + " KB";

            li.innerHTML = `
                <span class="file-name">${file.name}</span>
                <span class="file-size">${size}</span>
            `;

            fileList.appendChild(li);
        }

        // Clear file input so same file can be uploaded again if needed
        document.getElementById("fileInput").value = "";
    })
    .catch(() => {
        status.innerText = "Upload failed.";
    });
}


// Shift + Enter to send message (ChatGPT-style)
const inputBox = document.getElementById("userInput");

inputBox.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && event.shiftKey) {
        event.preventDefault(); // stop new line
        sendMessage();
    }
});
window.addEventListener("DOMContentLoaded", () => {
    showIntroMessage();
});
