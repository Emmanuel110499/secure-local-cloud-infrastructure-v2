document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    document.body.classList.add("emma-soft-page");

    function normalize(value) {
        return String(value || "")
            .replace(/\s+/g, " ")
            .trim()
            .toLowerCase();
    }

    const title = [...document.querySelectorAll("h1")]
        .find(element =>
            normalize(element.textContent)
                .includes("emma_ia")
        );

    if (title) {
        const header =
            title.closest(
                "header, .page-header, .hero, .assistant-header"
            )
            || title.parentElement;

        header?.classList.add(
            "emma-soft-page-header"
        );
    }

    const conversationTitle = [
        ...document.querySelectorAll(
            "h2, h3, h4, strong"
        ),
    ].find(element =>
        normalize(element.textContent)
            .includes("conversation avec emma_ia")
    );

    let shell = conversationTitle?.closest(
        "section, article, .chat-container, "
        + ".assistant-container, .card, .panel"
    );

    if (!shell) {
        const messageText = [
            ...document.querySelectorAll("p"),
        ].find(element =>
            normalize(element.textContent)
                .includes("bonjour, je suis emma_ia")
        );

        shell = messageText?.closest(
            "section, article, .chat-container, "
            + ".assistant-container, .card, .panel"
        );
    }

    shell?.classList.add("emma-soft-shell");

    if (conversationTitle) {
        const chatHeader =
            conversationTitle.closest(
                "header, .chat-header, "
                + ".assistant-chat-header"
            )
            || conversationTitle.parentElement;

        chatHeader?.classList.add(
            "emma-soft-chat-header"
        );

        const identity =
            conversationTitle.closest("div");

        identity?.classList.add(
            "emma-soft-identity"
        );

        const avatar = chatHeader?.querySelector(
            ".avatar, .assistant-avatar, "
            + ".bot-avatar, [class*='icon']"
        );

        avatar?.classList.add(
            "emma-soft-avatar"
        );
    }

    const clearButton = [
        ...document.querySelectorAll("button"),
    ].find(button =>
        normalize(button.textContent)
            .includes("effacer")
    );

    clearButton?.classList.add(
        "emma-soft-clear"
    );

    const messageText = [
        ...document.querySelectorAll("p"),
    ].find(element =>
        normalize(element.textContent)
            .includes("bonjour, je suis emma_ia")
    );

    const messages =
        messageText?.closest(
            ".messages, .chat-messages, "
            + ".conversation-messages, "
            + ".assistant-messages"
        )
        || messageText?.parentElement?.parentElement;

    messages?.classList.add(
        "emma-soft-messages"
    );

    document.querySelectorAll(
        ".message, .chat-message, "
        + ".assistant-message, .message-bubble"
    ).forEach(message => {
        message.classList.add(
            "emma-soft-message"
        );

        if (
            message.classList.contains("user")
            || message.classList.contains("user-message")
            || message.dataset.role === "user"
        ) {
            message.classList.add("is-user");
        }
    });

    if (messageText) {
        const messageCard = messageText.closest(
            ".message, .chat-message, "
            + ".assistant-message, "
            + ".message-bubble, article, .card"
        );

        messageCard?.classList.add(
            "emma-soft-message"
        );
    }

    const input = document.querySelector(
        "textarea, "
        + "input[type='text'][name*='message'], "
        + "input[type='text'][placeholder*='message' i]"
    );

    const composer = input?.closest(
        "form, .chat-input, "
        + ".composer, .message-form"
    );

    composer?.classList.add(
        "emma-soft-composer"
    );

    const sendButton = composer?.querySelector(
        "button[type='submit'], "
        + ".send-button, "
        + "button[aria-label*='envoyer' i]"
    );

    sendButton?.classList.add(
        "emma-soft-send"
    );

    const suggestionButtons = [
        ...document.querySelectorAll(
            "[data-question], "
            + ".suggestion-button, "
            + ".quick-question, "
            + ".prompt-chip"
        ),
    ];

    if (suggestionButtons.length) {
        const suggestions =
            suggestionButtons[0].parentElement;

        suggestions?.classList.add(
            "emma-soft-suggestions"
        );
    }

    /*
     * Remplace aussi le texte si celui-ci est généré
     * dynamiquement par JavaScript.
     */
    document.querySelectorAll("p").forEach(paragraph => {
        const content = normalize(
            paragraph.textContent
        );

        if (
            content.startsWith(
                "bonjour, je suis emma_ia"
            )
        ) {
            paragraph.textContent = "Bonjour, je suis Emma_IA. Que puis-je faire pour vous ?";
        }
    });
});
