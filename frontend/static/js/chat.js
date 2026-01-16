const chatBox = document.getElementById("chatBox");
const API_BASE = "http://127.0.0.1:8000/api";

let documentsUploaded = false;

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
        Please connect your Google Drive and upload a document to begin.</p>
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

    fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ query })
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

// ---------------- DRIVE CONFIG ----------------
async function configureDrive() {
    const fileInput = document.getElementById("serviceAccountFile");
    const folderInput = document.getElementById("folderIdInput");
    const status = document.getElementById("driveStatus");

    if (!fileInput.files.length || !folderInput.value.trim()) {
        status.innerText = "Please provide JSON file and folder ID.";
        return;
    }

    const formData = new FormData();
    formData.append("service_account", fileInput.files[0]);
    formData.append("folder_id", folderInput.value.trim());

    status.innerText = "Connecting to Google Drive…";

    try {
        const res = await fetch(`${API_BASE}/drive/configure`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) throw new Error();

        status.innerText = "Drive connected successfully.";
        loadDriveFiles();
    } catch {
        status.innerText = "Failed to connect Drive. Check credentials.";
    }
}

// ---------------- DRIVE FILES ----------------
async function loadDriveFiles() {
    try {
        const response = await fetch(`${API_BASE}/drive/files`);
        const files = await response.json();

        const select = document.getElementById("driveFileSelect");
        select.innerHTML = `<option value="">-- Select a file --</option>`;

        files.forEach(file => {
            const option = document.createElement("option");
            option.value = file.id;
            option.textContent = file.name;
            select.appendChild(option);
        });

        select.disabled = false;
        document.getElementById("uploadBtn").disabled = false;

    } catch (err) {
        console.error("Failed to load Drive files:", err);
    }
}

// ---------------- UPLOAD ----------------
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

    status.innerText = "Uploading and indexing document…";

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
        status.innerText = "Document uploaded successfully. You can now ask questions.";
        documentsUploaded = true;

        document.getElementById("userInput").disabled = false;
        document.getElementById("sendBtn").disabled = false;

        const li = document.createElement("li");
        li.innerHTML = `<span class="file-name">${fileName}</span>`;
        fileList.appendChild(li);
    })
    .catch(() => {
        status.innerText = "Upload failed.";
    });
}

// ---------------- INIT ----------------
document.addEventListener("DOMContentLoaded", () => {
    showIntroMessage();
    enableShiftEnterSend();
});

// ---------------- SHIFT + ENTER SEND ----------------
function enableShiftEnterSend() {
    const input = document.getElementById("userInput");

    if (!input) return;

    input.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && e.shiftKey) {
            e.preventDefault();   // prevent newline
            sendMessage();
        }
    });
}

