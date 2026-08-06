document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const launcher =
        document.getElementById("emma-chat-launcher");

    const panel =
        document.getElementById("emma-chat-panel");

    const closeButton =
        document.getElementById("emma-chat-close");

    const clearButton =
        document.getElementById("emma-chat-clear");

    const messages =
        document.getElementById("emma-chat-messages");

    const form =
        document.getElementById("emma-chat-form");

    const input =
        document.getElementById("emma-chat-input");

    const sendButton =
        document.getElementById("emma-chat-send");

    const chips = [
        ...document.querySelectorAll(
            ".emma-chat-chip"
        ),
    ];

    if (
        !launcher
        || !panel
        || !messages
        || !form
        || !input
        || !sendButton
    ) {
        return;
    }

    const storageKey =
        "emma_floating_conversation_v1";

    let conversation = [];

    function currentTime() {
        return new Date().toLocaleTimeString(
            "fr-FR",
            {
                hour: "2-digit",
                minute: "2-digit",
            }
        );
    }

    function scrollToBottom() {
        messages.scrollTop =
            messages.scrollHeight;
    }

    function appendMessage(
        text,
        role = "assistant",
        time = currentTime(),
        save = true
    ) {
        const bubble =
            document.createElement("div");

        bubble.className =
            `emma-chat-message ${role}`;

        const content =
            document.createElement("div");

        content.textContent = text;

        const meta =
            document.createElement("span");

        meta.className =
            "emma-chat-message-meta";

        meta.textContent =
            role === "user"
                ? `Vous · ${time}`
                : `Emma_IA · ${time}`;

        bubble.appendChild(content);
        bubble.appendChild(meta);
        messages.appendChild(bubble);

        if (save) {
            conversation.push({
                text,
                role,
                time,
            });

            localStorage.setItem(
                storageKey,
                JSON.stringify(conversation)
            );
        }

        scrollToBottom();

        return bubble;
    }

    function appendWelcome() {
        appendMessage(
            "Bonjour, je suis Emma_IA. "
            + "Que puis-je faire pour vous ?",
            "assistant"
        );
    }

    function showTyping() {
        const typing =
            document.createElement("div");

        typing.className =
            "emma-chat-message "
            + "emma-chat-typing";

        typing.id =
            "emma-chat-typing";

        typing.innerHTML =
            "<span></span>"
            + "<span></span>"
            + "<span></span>";

        messages.appendChild(typing);
        scrollToBottom();

        return typing;
    }

    function loadConversation() {
        messages.innerHTML = "";

        try {
            const saved = JSON.parse(
                localStorage.getItem(
                    storageKey
                ) || "[]"
            );

            conversation =
                Array.isArray(saved)
                    ? saved
                    : [];

            conversation.forEach(message => {
                appendMessage(
                    message.text,
                    message.role,
                    message.time,
                    false
                );
            });
        } catch (error) {
            conversation = [];

            localStorage.removeItem(
                storageKey
            );
        }

        if (!conversation.length) {
            appendWelcome();
        }
    }

    function openChat() {
        panel.classList.add("is-open");
        document.body.classList.add(
            "emma-chat-is-open"
        );
        panel.setAttribute("aria-hidden", "false");

        launcher.setAttribute(
            "aria-expanded",
            "true"
        );

        window.setTimeout(
            () => input.focus(),
            180
        );

        scrollToBottom();
    }

    function closeChat() {
        panel.classList.remove("is-open");
        document.body.classList.remove(
            "emma-chat-is-open"
        );
        panel.setAttribute("aria-hidden", "true");

        launcher.setAttribute(
            "aria-expanded",
            "false"
        );

        launcher.focus();
    }

    async function askAssistant(question) {
        const cleaned =
            String(question || "").trim();

        if (!cleaned) {
            return;
        }

        appendMessage(
            cleaned,
            "user"
        );

        input.value = "";
        input.disabled = true;
        sendButton.disabled = true;

        const typing = showTyping();

        try {
            const response = await fetch(
                "/api/assistant",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",
                        Accept:
                            "application/json",
                    },
                    body: JSON.stringify({
                        question: cleaned,
                    }),
                }
            );

            const payload =
                await response.json()
                .catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    payload.error
                    || "Réponse indisponible."
                );
            }

            typing.remove();

            appendMessage(
                payload.answer
                || payload.response
                || "Je n’ai pas pu générer une réponse.",
                "assistant"
            );
        } catch (error) {
            typing.remove();

            appendMessage(
                error.message
                || "Impossible de contacter Emma_IA.",
                "assistant"
            );
        } finally {
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
        }
    }

    launcher.addEventListener(
        "click",
        () => {
            if (
                panel.classList.contains(
                    "is-open"
                )
            ) {
                closeChat();
            } else {
                openChat();
            }
        }
    );

    closeButton?.addEventListener(
        "click",
        closeChat
    );

    clearButton?.addEventListener(
        "click",
        () => {
            conversation = [];
            messages.innerHTML = "";

            localStorage.removeItem(
                storageKey
            );

            appendWelcome();
            input.focus();
        }
    );

    form.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            await askAssistant(
                input.value
            );
        }
    );

    input.addEventListener(
        "keydown",
        async event => {
            if (
                event.key === "Enter"
                && !event.shiftKey
            ) {
                event.preventDefault();

                await askAssistant(
                    input.value
                );
            }
        }
    );

    chips.forEach(chip => {
        chip.addEventListener(
            "click",
            async () => {
                openChat();

                await askAssistant(
                    chip.dataset.question
                    || chip.textContent
                );
            }
        );
    });

    document.addEventListener(
        "keydown",
        event => {
            if (
                event.key === "Escape"
                && panel.classList.contains(
                    "is-open"
                )
            ) {
                closeChat();
            }
        }
    );

    loadConversation();
});
