
const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");
const status = document.getElementById("status");
const newChatBtn = document.getElementById("new-chat-btn");  //## add chat button
// Add the file input variables
const fileInput = document.getElementById("file-input");
const fileName = document.getElementById("file-name");

const attachmentPreview = document.getElementById("attachment-preview");
const removeFileBtn = document.getElementById("remove-file-btn");
const attachBtn = document.getElementById("attach-btn");

const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");


const history = [];

newChatBtn.addEventListener("click", () => {
    history.length = 0;

    chatBox.replaceChildren();

    addMessage("Hi! How can I help you today?", "bot");

    status.textContent = "";
//     input.value = "";
//     input.focus();
    input.value = "";
    fileInput.value = "";
    fileName.textContent = "";
    input.focus();
    resetComposer();
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




// form.addEventListener("submit", async (event) => {
//     event.preventDefault();

//     const message = input.value.trim();
//     if (!message) return;

//     addMessage(message, "user");
//     input.value = "";
//     // ####to auto-expanding text area
//     input.style.height = "28px";
//     input.style.overflowY = "hidden";
//     sendBtn.disabled = true;
//     status.textContent = "AI is thinking...";

//     try {
//         const response = await fetch("http://127.0.0.1:8000/chat", {
//         // await fetch("http://127.0.0.1:8000/chat", {
//         // const response = await fetch("https://ai-chatbot-28dv.onrender.com/chat", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             // body: JSON.stringify({ message })
//             body: JSON.stringify({
//             message: message,
//             history: history
// })
//         });

//         const data = await response.json();

//         if (!response.ok) {
//             throw new Error(data.detail || "Request failed");
//         }

//         // addMessage(data.reply, "bot");
//         // status.textContent = "";

//         //////////     store history after AI response            //

//         addMessage(data.reply, "bot");

//         // Save current question and AI response
//         history.push(
//             { role: "user", content: message },
//             { role: "assistant", content: data.reply }
//         );

//         // Keep only the latest 20 messages
//         if (history.length > 20) {
//             history.splice(0, history.length - 20);
//         }

//         status.textContent = "";

//     } catch (error) {
//         status.textContent =
//             "Unable to get an answer. Please try again.";
//         console.error("Chat error:", error);

//     } finally { 
//         sendBtn.disabled = false;
//         input.focus();
//     }
// });


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();
    const file = fileInput.files[0];

    // Allow a message, a file, or both.
    if (!message && !file) return;

    // const displayMessage = file
    //     ? (message
    //         ? `${message}\n📎 ${file.name}`
    //         : `Please analyze the attached file: ${file.name}`)
    //     : message;
    
    const displayMessage = file
        ? (message
            ? `${message}\n📎 ${file.name}`
            : `📎 ${file.name}`)
    : message;


    const formData = new FormData();
    formData.append("message", message);
    formData.append("history", JSON.stringify(history));

    if (file) {
        formData.append("file", file);
    }

    addMessage(displayMessage, "user");
    resetComposer();

    sendBtn.disabled = true;
    status.textContent = "AI is thinking...";

    try {
        const response = await fetch("http://127.0.0.1:8000/chat", {
        // const response = await fetch("https://ai-chatbot-28dv.onrender.com/chat", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Request failed");
        }

        addMessage(data.reply, "bot");

        history.push(
            { role: "user", content: displayMessage },
            { role: "assistant", content: data.reply }
        );

        // Keep only the latest 20 messages.
        if (history.length > 20) {
            history.splice(0, history.length - 20);
        }

        status.textContent = "";

    } catch (error) {
        status.textContent = "Unable to get an answer. Please try again.";
        console.error("Chat error:", error);

    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
});



// const fileInput = document.getElementById("file-input");
// const fileName = document.getElementById("file-name");

// if (fileInput && fileName) {
//     fileInput.addEventListener("change", () => {
//         fileName.textContent = fileInput.files.length
//             ? fileInput.files[0].name
//             : "";
//     });
// }


// fileInput.addEventListener("change", () => {
//     const file = fileInput.files[0];

//     fileName.textContent = file ? file.name : "";
// });


userInput.addEventListener("keydown", (e) => {
    // Enter = send, Shift+Enter = new line
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
        e.preventDefault();          // stops a new line being added
        chatForm.requestSubmit();    // runs your existing submit code
    }
});


const MAX_INPUT_HEIGHT = 180;

function resizeMessageInput() {
    input.style.height = "28px";

    input.style.height =
        Math.min(input.scrollHeight, MAX_INPUT_HEIGHT) + "px";

    input.style.overflowY =
        input.scrollHeight > MAX_INPUT_HEIGHT ? "auto" : "hidden";
}

// Grow the input as the user types or pastes text.
input.addEventListener("input", resizeMessageInput);

// Open the file picker.
attachBtn.addEventListener("click", () => {
    fileInput.click();
});

// Display the selected file.
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (file) {
        fileName.textContent = file.name;
        attachmentPreview.hidden = false;
    } else {
        fileName.textContent = "";
        attachmentPreview.hidden = true;
    }
});

// Remove the selected file.
removeFileBtn.addEventListener("click", () => {
    fileInput.value = "";
    fileName.textContent = "";
    attachmentPreview.hidden = true;
    input.focus();
});

// Reset the composer.
function resetComposer() {
    input.value = "";
    input.style.height = "28px";
    input.style.overflowY = "hidden";

    fileInput.value = "";
    fileName.textContent = "";
    attachmentPreview.hidden = true;
}
