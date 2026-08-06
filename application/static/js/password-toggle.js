document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(
        ".password-toggle"
    );

    buttons.forEach((button) => {
        let input = null;

        const targetId = button.dataset.toggleFor;

        if (targetId) {
            input = document.getElementById(targetId);
        } else {
            input = button
                .closest(".field")
                ?.querySelector("input");
        }

        if (!input) {
            return;
        }

        const openIcon = button.querySelector(
            ".password-eye-open"
        );

        const closedIcon = button.querySelector(
            ".password-eye-closed"
        );

        button.addEventListener("click", () => {
            const passwordIsVisible =
                input.type === "text";

            input.type = passwordIsVisible
                ? "password"
                : "text";

            input.classList.toggle(
                "password-visible",
                !passwordIsVisible
            );

            if (openIcon) {
                openIcon.hidden = !passwordIsVisible;
            }

            if (closedIcon) {
                closedIcon.hidden = passwordIsVisible;
            }

            const label = passwordIsVisible
                ? "Afficher le mot de passe"
                : "Masquer le mot de passe";

            button.setAttribute(
                "aria-label",
                label
            );

            button.setAttribute(
                "title",
                label
            );

            input.focus();
        });
    });
});
