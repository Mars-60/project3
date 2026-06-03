const echoPanel = document.getElementById("echoPanel");
const echoLauncher = document.getElementById("echoLauncher");
const closeButton = document.getElementById("closeButton");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendButton = document.getElementById("sendButton");
const chatScroll = document.getElementById("chatScroll");
const messages = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");
const promptCards = document.querySelectorAll(".prompt-card");

let isWaiting = false;

function openEcho() {
    echoPanel.classList.add("open");
    window.setTimeout(() => {
        chatInput.focus();
    }, 180);
}

function closeEcho() {
    echoPanel.classList.remove("open");
}

function scrollToBottom() {
    chatScroll.scrollTop = chatScroll.scrollHeight;
}

function hideWelcome() {
    welcomeScreen.classList.add("hidden");
}

function addMessage(role, text, extraClass = "") {
    hideWelcome();

    const message = document.createElement("div");

    message.className = ["message", role, extraClass].filter(Boolean).join(" ");
    if (role === "assistant") {
    message.innerHTML = marked.parse(text);
} else {
    message.textContent = text;
}

    messages.appendChild(message);
    scrollToBottom();

    return message;
}

function addTypingIndicator() {
    const typing = document.createElement("div");

    typing.className = "message assistant typing";
    typing.innerHTML = "<span></span><span></span><span></span>";

    messages.appendChild(typing);
    scrollToBottom();

    return typing;
}

function autoResizeInput() {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 130) + "px";
}

async function animateAssistantResponse(text) {

    const message = addMessage("assistant", "");

    const cleanText = text || "No answer returned.";

    let displayed = "";

    for (const char of cleanText) {

        displayed += char;

        message.innerHTML = marked.parse(displayed);

        scrollToBottom();

        await new Promise((resolve) => {
            setTimeout(resolve, 8);
        });
    }

    message.innerHTML = marked.parse(cleanText);
}

async function sendQuestion(question) {
    const cleanQuestion = question.trim();

    if (!cleanQuestion || isWaiting) {
        return;
    }

    openEcho();
    addMessage("user", cleanQuestion);

    chatInput.value = "";
    autoResizeInput();
    isWaiting = true;
    sendButton.disabled = true;

    const typing = addTypingIndicator();

    try {
        const response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: cleanQuestion
            })
        });

        const data = await response.json();

        typing.remove();

        if (!response.ok || data.status !== "success") {
            throw new Error(data.message || "Echo could not answer that.");
        }

        await animateAssistantResponse(data.answer);
    } catch (error) {
        typing.remove();
        addMessage("assistant", "Error: " + error.message, "error");
    } finally {
        isWaiting = false;
        sendButton.disabled = false;
        chatInput.focus();
    }
}

echoLauncher.addEventListener("click", () => {
    if (echoPanel.classList.contains("open")) {
        closeEcho();
    } else {
        openEcho();
    }
});

closeButton.addEventListener("click", closeEcho);

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendQuestion(chatInput.value);
});

chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendQuestion(chatInput.value);
    }
});

chatInput.addEventListener("input", autoResizeInput);

promptCards.forEach((card) => {
    card.addEventListener("click", () => {
        sendQuestion(card.textContent);
    });
});
