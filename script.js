const tabs = document.querySelectorAll(".tab");

const categoryInput = document.getElementById("category");
const budgetInput = document.getElementById("budget");
const preferencesInput = document.getElementById("preferences");
const extraInput = document.getElementById("extra");

const preferenceLabel =
    document.getElementById("preference-label");

const extraLabel =
    document.getElementById("extra-label");

const imageField =
    document.getElementById("image-field");

const imageInput =
    document.getElementById("outfit-image");

const form = document.getElementById("planner-form");

const submitButton =
    document.getElementById("submit-btn");

const resultSection =
    document.getElementById("result-section");

const resultBox =
    document.getElementById("result");

const copyButton =
    document.getElementById("copy-btn");


const plannerSettings = {
    home: {
        preferenceLabel: "Room and Style Preferences",
        preferencePlaceholder:
            "Example: Small bedroom, modern style",

        extraLabel: "Items and Quantities",
        extraPlaceholder:
            "Example: 2 lights, 1 fan, curtains"
    },

    party: {
        preferenceLabel: "Event Type and Preferences",
        preferencePlaceholder:
            "Example: Birthday party, outdoor venue",

        extraLabel: "Guest Count and Venue Details",
        extraPlaceholder:
            "Example: 30 guests, vegetarian food"
    },

    jewelry: {
        preferenceLabel: "Occasion and Jewelry Style",
        preferencePlaceholder:
            "Example: Wedding, traditional jewelry",

        extraLabel: "Outfit Colors and Preferences",
        extraPlaceholder:
            "Example: Maroon saree, gold accessories"
    }
};


// Switch between Home, Party and Jewelry.
tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        tabs.forEach((item) => {
            item.classList.remove("active");
        });

        tab.classList.add("active");

        const category = tab.dataset.category;
        const settings = plannerSettings[category];

        categoryInput.value = category;

        preferenceLabel.textContent =
            settings.preferenceLabel;

        preferencesInput.placeholder =
            settings.preferencePlaceholder;

        extraLabel.textContent =
            settings.extraLabel;

        extraInput.placeholder =
            settings.extraPlaceholder;

        imageField.classList.toggle(
            "hidden",
            category !== "jewelry"
        );

        resultSection.classList.add("hidden");
    });
});


// Escape HTML before displaying generated text.
function escapeHTML(value) {
    const characters = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    };

    return value.replace(/[&<>"']/g, (character) => {
        return characters[character];
    });
}


// Display basic Markdown-style headings and lists.
function formatResult(text) {
    const safeText = escapeHTML(text);

    return safeText
        .replace(/^### (.*)$/gm, "<h3>$1</h3>")
        .replace(/^## (.*)$/gm, "<h3>$1</h3>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\n/g, "<br>");
}


// Submit the selected planner.
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const category = categoryInput.value;
    const budget = Number(budgetInput.value);

    const preferences = preferencesInput.value.trim();
    const extra = extraInput.value.trim();

    if (
        !Number.isFinite(budget) ||
        budget <= 0 ||
        !preferences
    ) {
        alert("Enter a valid budget and your preferences.");
        return;
    }

    if (
        category === "jewelry" &&
        imageInput.files.length > 0
    ) {
        const image = imageInput.files[0];

        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];

        if (!allowedTypes.includes(image.type)) {
            alert("Upload a JPG, PNG, or WEBP image.");
            return;
        }

        if (image.size > 5 * 1024 * 1024) {
            alert("Image size must be less than 5 MB.");
            return;
        }
    }

    submitButton.disabled = true;
    submitButton.textContent = "Generating your plan...";

    resultSection.classList.remove("hidden");

    resultBox.textContent =
        "Please wait. Preparing your recommendations...";

    try {
        let response;

        if (category === "jewelry") {
            const formData = new FormData();

            formData.append("budget", String(budget));
            formData.append("preferences", preferences);
            formData.append("extra", extra);

            if (imageInput.files.length > 0) {
                formData.append(
                    "outfit_image",
                    imageInput.files[0]
                );
            }

            response = await fetch("/generate-jewelry", {
                method: "POST",
                body: formData
            });

        } else {
            const endpoint =
                category === "home"
                    ? "/generate-home"
                    : "/generate-party";

            response = await fetch(endpoint, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    budget,
                    preferences,
                    extra
                })
            });
        }

        const data = await response.json();

        if (!response.ok || data.error) {
            throw new Error(
                data.error || "Could not generate recommendations."
            );
        }

        resultBox.innerHTML = formatResult(
            data.result || "No recommendations returned."
        );

    } catch (error) {
        resultBox.textContent =
            "Error: " + error.message +
            " Please check that the backend server is running.";

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Generate My Plan →";
    }
});


// Copy recommendations.
copyButton.addEventListener("click", async () => {
    try {
        await navigator.clipboard.writeText(
            resultBox.innerText
        );

        copyButton.textContent = "Copied!";

        setTimeout(() => {
            copyButton.textContent =
                "Copy Recommendations";
        }, 1500);

    } catch (error) {
        alert(
            "Please select the recommendation text and copy it manually."
        );
    }
});