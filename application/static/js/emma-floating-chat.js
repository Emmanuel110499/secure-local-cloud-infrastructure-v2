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

    const historyRetentionMs =
        24 * 60 * 60 * 1000;

    const maxStoredMessages = 40;

    let conversation = [];

    function persistConversation() {
        conversation = conversation.slice(
            -maxStoredMessages
        );

        localStorage.setItem(
            storageKey,
            JSON.stringify({
                savedAt: Date.now(),
                messages: conversation,
            })
        );
    }

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
        save = true,
        details = null
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

        if (role === "assistant" && details) {
            const detailsBox = document.createElement("div");
            detailsBox.className = "emma-chat-details";

            const badges = document.createElement("div");
            badges.className = "emma-chat-badges";

            const confidence = Number(details.confidence || 0);

            if (confidence > 0) {
                const confidenceBadge = document.createElement("span");
                confidenceBadge.textContent =
                    `Confiance ${Math.round(confidence * 100)} %`;
                badges.appendChild(confidenceBadge);
            }

            const dataBadge = document.createElement("span");
            dataBadge.textContent = details.used_live_data
                ? "Données en direct"
                : "Documentation";
            badges.appendChild(dataBadge);
            detailsBox.appendChild(badges);

            if (Array.isArray(details.sources) && details.sources.length) {
                const sources = document.createElement("small");
                sources.textContent = `Sources : ${details.sources.join(", ")}`;
                detailsBox.appendChild(sources);
            }

            if (Array.isArray(details.suggestions) && details.suggestions.length) {
                const suggestions = document.createElement("div");
                suggestions.className = "emma-chat-followups";

                details.suggestions.slice(0, 3).forEach(suggestion => {
                    const button = document.createElement("button");
                    button.type = "button";
                    button.textContent = suggestion;
                    button.addEventListener("click", () => askAssistant(suggestion));
                    suggestions.appendChild(button);
                });

                detailsBox.appendChild(suggestions);
            }

            bubble.appendChild(detailsBox);
        }

        bubble.appendChild(meta);
        messages.appendChild(bubble);

        if (save) {
            conversation.push({
                text,
                role,
                time,
                details,
            });

            persistConversation();
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
                ) || "null"
            );

            const isFresh = (
                saved
                && Number.isFinite(saved.savedAt)
                && Date.now() - saved.savedAt
                    <= historyRetentionMs
                && Array.isArray(saved.messages)
            );

            conversation = isFresh
                ? saved.messages.slice(-maxStoredMessages)
                : [];

            if (!isFresh) {
                localStorage.removeItem(storageKey);
            }

            conversation.forEach(message => {
                appendMessage(
                    message.text,
                    message.role,
                    message.time,
                    false,
                    message.details || null
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
                "assistant",
                currentTime(),
                true,
                payload
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

    document.querySelectorAll(
        'a[href$="/logout"]'
    ).forEach(link => {
        link.addEventListener("click", () => {
            localStorage.removeItem(storageKey);
        });
    });

    loadConversation();
});
