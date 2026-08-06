document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById(
        "user-menu-button"
    );

    const menu = document.getElementById(
        "user-menu"
    );

    if (!button || !menu) {
        return;
    }

    function closeMenu() {
        menu.hidden = true;
        button.setAttribute(
            "aria-expanded",
            "false"
        );
    }

    function openMenu() {
        menu.hidden = false;
        button.setAttribute(
            "aria-expanded",
            "true"
        );
    }

    button.addEventListener("click", (event) => {
        event.stopPropagation();

        if (menu.hidden) {
            openMenu();
        } else {
            closeMenu();
        }
    });

    menu.addEventListener("click", (event) => {
        event.stopPropagation();
    });

    document.addEventListener("click", closeMenu);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const mobileButton = document.getElementById(
        "mobile-user-menu-button"
    );

    const mobileMenu = document.getElementById(
        "mobile-user-menu"
    );

    if (!mobileButton || !mobileMenu) {
        return;
    }

    function closeMobileUserMenu() {
        mobileMenu.hidden = true;

        mobileButton.setAttribute(
            "aria-expanded",
            "false"
        );
    }

    function openMobileUserMenu() {
        mobileMenu.hidden = false;

        mobileButton.setAttribute(
            "aria-expanded",
            "true"
        );
    }

    mobileButton.addEventListener(
        "click",
        (event) => {
            event.stopPropagation();

            if (mobileMenu.hidden) {
                openMobileUserMenu();
            } else {
                closeMobileUserMenu();
            }
        }
    );

    mobileMenu.addEventListener(
        "click",
        (event) => {
            event.stopPropagation();
        }
    );

    document.addEventListener(
        "click",
        closeMobileUserMenu
    );

    document.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Escape") {
                closeMobileUserMenu();
            }
        }
    );
});


/* MOBILE ACCOUNT MENU CLONE */
document.addEventListener("DOMContentLoaded", () => {
    const desktopMenu =
        document.getElementById("user-menu");

    const mobileMenu =
        document.getElementById("mobile-user-menu");

    if (!desktopMenu || !mobileMenu) {
        return;
    }

    /*
     * Le téléphone reçoit exactement les mêmes options
     * que le menu du compte sur ordinateur.
     */
    mobileMenu.innerHTML =
        desktopMenu.innerHTML;

    mobileMenu.querySelectorAll("[id]").forEach(
        element => element.removeAttribute("id")
    );
});
