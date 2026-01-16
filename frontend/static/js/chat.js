const chatBox = document.getElementById("chatBox");
let documentsUploaded = false;
const API_BASE = "http://127.0.0.1:8000/api";

// ---------------- ALERTS ----------------
function showAlert() {
    document.getElementById("systemAlert").classList.remove("hidden");
}
function closeAlert() {
    document.getElementById("systemAlert").classList.add("hidden");
}

// ---------------- INTRO ----------------
function showIntroMessage() {
    appendMessage(`
        <p><strong>Hi, I’m Veritas AI!</strong><br>
        I answer questions strictly based on uploaded documents.</p>
    `, "bot");
}

// ---------------- CHAT UI ----------------
function appendMessage(html, sender, isRefusal = false) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    if (isRefusal) bubble.classList.add("refusal");

    bubble.innerHTML = html;
    row.appendChild(bubble);
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;

    return row;
}

function sendMessage() {
    const input = document.getElementById("userInput");
    const query = input.value.trim();
    if (!query) return;

    if (!documentsUploaded) {
        showAlert();
        return;
    }

    closeAlert();
    appendMessage(query, "user");
    input.value = "";

    const thinking = appendMessage("<em>Veritas is thinking…</em>", "bot");

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query})
    })
    .then(res => res.json())
    .then(data => {
        chatBox.removeChild(thinking);
        const answer = data.answer || "";
        const isRefusal = answer.toLowerCase().includes("not available");
        appendMessage(answer, "bot", isRefusal);
    })
    .catch(() => {
        chatBox.removeChild(thinking);
        appendMessage("<p>⚠️ Something went wrong.</p>", "bot", true);
    });
}

// ---------------- DRIVE FILES ----------------
async function loadDriveFiles() {
    try {
        const response = await fetch(`${API_BASE}/drive/files`);
        const files = await response.json();

        const select = document.getElementById("driveFileSelect");
        files.forEach(file => {
            const option = document.createElement("option");
            option.value = file.id;
            option.textContent = file.name;
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Failed to load Drive files:", err);
    }
}


function uploadDriveFile() {
    const select = document.getElementById("driveFileSelect");
    const fileId = select.value;
    const fileName = select.options[select.selectedIndex]?.text;

    if (!fileId) {
        alert("Please select a file");
        return;
    }

    const status = document.getElementById("uploadStatus");
    const fileList = document.getElementById("uploadedFiles");

    status.innerText = "Uploading…";

    fetch(`${API_BASE}/upload-from-drive`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            file_id: fileId,
            file_name: fileName
        })
    })
    .then(res => res.json())
    .then(() => {
        status.innerText = "Document uploaded successfully. You Can Now Ask Questions.";
        documentsUploaded = true;

        const li = document.createElement("li");
        li.innerHTML = `<span class="file-name">${fileName}</span>`;
        fileList.appendChild(li);
    })
    .catch(() => {
        status.innerText = "Upload failed.";
    });
}

// ---------------- EVENTS ----------------
document.addEventListener("DOMContentLoaded", () => {
    showIntroMessage();
    loadDriveFiles();
});

document.getElementById("userInput").addEventListener("keydown", e => {
    if (e.key === "Enter" && e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

