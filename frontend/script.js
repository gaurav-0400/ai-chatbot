
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");
const status = document.getElementById("status");
const newChatBtn = document.getElementById("new-chat-btn");  //## add chat button

const history = [];

newChatBtn.addEventListener("click", () => {
    history.length = 0;

    chatBox.replaceChildren();

    addMessage("Hi! How can I help you today?", "bot");

    status.textContent = "";
    input.value = "";
    input.focus();
});

// function addMessage(text, sender) {
//     const message = document.createElement("div");
//     message.className = `message ${sender}`;
//     message.textContent = text;
//     chatBox.appendChild(message);
//     chatBox.scrollTop = chatBox.scrollHeight;
// }


function addMessage(text, sender) {
    const message = document.createElement("div");
    message.className = `message ${sender}`;

    if (sender === "bot") {
        // Convert Markdown to HTML, then sanitize it
        const html = marked.parse(text || "");
        message.innerHTML = DOMPurify.sanitize(html);

        // Highlight code blocks
        // message.querySelectorAll("pre code").forEach((block) => {
        //     hljs.highlightElement(block);
        if (typeof hljs !== "undefined") {
        message.querySelectorAll("pre code").forEach((block) => {
        hljs.highlightElement(block);
        });
        }

    }else {
        // Always treat user messages as plain text
        message.textContent = text;
    }

    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
}




form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";
    sendBtn.disabled = true;
    status.textContent = "AI is thinking...";

    try {
        // const response = await fetch("http://127.0.0.1:8000/chat", {
        // await fetch("http://127.0.0.1:8000/chat", {
        const response = await fetch("https://ai-chatbot-28dv.onrender.com/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            // body: JSON.stringify({ message })
            body: JSON.stringify({
            message: message,
            history: history
})
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Request failed");
        }

        // addMessage(data.reply, "bot");
        // status.textContent = "";

        //////////     store history after AI response            //

        addMessage(data.reply, "bot");

        // Save current question and AI response
        history.push(
            { role: "user", content: message },
            { role: "assistant", content: data.reply }
        );

        // Keep only the latest 20 messages
        if (history.length > 20) {
            history.splice(0, history.length - 20);
        }

        status.textContent = "";

    } catch (error) {
        status.textContent =
            "Unable to get an answer. Please try again.";
        console.error("Chat error:", error);

    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
});
