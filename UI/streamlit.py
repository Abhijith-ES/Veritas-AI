import streamlit as st
import requests
import time

# ------------------ Configuration ------------------

BACKEND_BASE_URL = "http://localhost:8000/api"

UPLOAD_ENDPOINT = f"{BACKEND_BASE_URL}/upload"
CHAT_ENDPOINT = f"{BACKEND_BASE_URL}/chat"

st.set_page_config(
    page_title="Veritas AI – Test UI",
    layout="centered",
)

# ------------------ Session State ------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ UI Header ------------------

st.title("🧠 Veritas AI – Test Interface")
st.caption("Document-grounded chatbot (accuracy-first testing UI)")

st.divider()

# ------------------ Document Upload Section ------------------

st.subheader("📄 Upload Documents")

uploaded_files = st.file_uploader(
    "Upload one or more documents (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if uploaded_files:
    if st.button("Upload to Veritas"):
        with st.spinner("Uploading and indexing documents..."):
            for file in uploaded_files:
                files = {
                    "file": (file.name, file.getvalue())
                }

                response = requests.post(
                    UPLOAD_ENDPOINT,
                    files=files,
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success(
                        f"Uploaded `{data['filename']}` "
                        f"({data['chunks_added']} chunks indexed)"
                    )
                else:
                    st.error(
                        f"Failed to upload {file.name}: "
                        f"{response.text}"
                    )

st.divider()

# ------------------ Chat Section ------------------

st.subheader("💬 Chat with Veritas")

query = st.text_input(
    "Ask a question based on the uploaded documents",
    placeholder="e.g. What is the refund policy mentioned in the document?",
)

if st.button("Ask Veritas") and query.strip():

    # Add user message to history
    st.session_state.chat_history.append(
        {"role": "user", "content": query}
    )

    # Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Veritas:** {msg['content']}")

    # Thinking indicator
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("⏳ **Veritas is thinking...**")

    try:
        start_time = time.time()

        response = requests.post(
            CHAT_ENDPOINT,
            json={"query": query},
            timeout=60,
        )

        elapsed = round(time.time() - start_time, 2)

        thinking_placeholder.empty()

        if response.status_code == 200:
            answer = response.json()["answer"]

            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )

            st.markdown(f"**Veritas:** {answer}")
            st.caption(f"⏱ Response time: {elapsed}s")

        else:
            st.error(f"Chat error: {response.text}")

    except requests.exceptions.RequestException as e:
        thinking_placeholder.empty()
        st.error(f"Backend not reachable: {str(e)}")

st.divider()

# ------------------ Footer ------------------

st.caption(
    "⚠️ This is a testing UI. Veritas will refuse to answer "
    "if information is not present in the uploaded documents."
)
