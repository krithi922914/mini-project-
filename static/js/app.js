
document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const destinationResults =
        document.getElementById("destination-results");

    const destinationSearch =
        document.getElementById("destination-search");

    const searchButton =
        document.getElementById("search-button");

    const recommendationForm =
        document.getElementById("recommendation-form");

    const recommendationResults =
        document.getElementById("recommendation-results");

    const hiddenGemsResults =
        document.getElementById("hidden-gems-results");

    const routeSelect =
        document.getElementById("route-destinations");

    const optimizeRouteButton =
        document.getElementById("optimize-route-button");

    const routeResults =
        document.getElementById("route-results");

    const feedbackForm =
        document.getElementById("feedback-form");

    const feedbackStatus =
        document.getElementById("feedback-status");

    const feedbackDestination =
        document.getElementById("feedback-destination");

    const feedbackAction =
        document.getElementById("feedback-action");

    const feedbackRating =
        document.getElementById("feedback-rating");

    let allDestinations = [];
    let map = null;
    let markers = [];

    // =====================================================
    // HELPER FUNCTIONS
    // =====================================================

    function escapeHTML(value) {
        return String(value ?? "").replace(
            /[&<>"']/g,
            character => ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            })[character]
        );
    }

    async function fetchJSON(url, options = {}) {

        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });

        if (!response.ok) {
            throw new Error(
                `Request failed: ${response.status}`
            );
        }

        return await response.json();
    }

    function getLatitude(place) {
        return Number(
            place.latitude ?? place.lat ?? 0
        );
    }

    function getLongitude(place) {
        return Number(
            place.longitude ?? place.lon ?? place.lng ?? 0
        );
    }

    function validCoordinates(place) {

        const lat = getLatitude(place);
        const lon = getLongitude(place);

        return Number.isFinite(lat)
            && Number.isFinite(lon)
            && lat !== 0
            && lon !== 0
            && Math.abs(lat) <= 90
            && Math.abs(lon) <= 180;
    }

    function getCrowdColor(level) {

        const colors = {
            low: "#16a34a",
            medium: "#d97706",
            high: "#dc2626"
        };

        return colors[
            String(level || "medium").toLowerCase()
        ] || "#64748b";
    }

    function getCrowdIndicator(level) {

        const crowd = String(
            level || "medium"
        ).toLowerCase();

        const color = getCrowdColor(crowd);

        return `
            <div style="
                display:inline-block;
                background:${color}18;
                color:${color};
                border:1px solid ${color};
                padding:7px 12px;
                border-radius:20px;
                margin-top:10px;
                font-weight:bold;
                font-size:13px;
            ">
                Crowd Level: ${escapeHTML(crowd.toUpperCase())}
            </div>
            <p style="font-size:11px;color:#888;">
                Crowd information: Simulated demo data
            </p>
        `;
    }

    function showMessage(container, message) {

        if (!container) return;

        container.textContent = message;
    }

    // =====================================================
    // DESTINATION CARDS
    // =====================================================

    function displayDestinations(
        destinations,
        container
    ) {

        if (!container) return;

        container.replaceChildren();

        if (
            !Array.isArray(destinations)
            || destinations.length === 0
        ) {

            showMessage(
                container,
                "No destinations found."
            );

            return;
        }

        destinations.forEach(place => {

            const card = document.createElement("div");

            card.className = "destination-card";

            const name = escapeHTML(
                place.name || "Destination"
            );

            const category = escapeHTML(
                place.category || "Tourism"
            );

            const description = escapeHTML(
                place.description || ""
            );

            const price = Number(place.price || 0);

            const rating = Number(place.rating || 0);

            const aiScore = Number(place.ai_score || 0);

            card.innerHTML = `
                <div class="destination-card-content">

                    <h3>${name}</h3>

                    <p>${category}</p>

                    <p>${description}</p>

                    <div class="destination-details">

                        <span>₹${price}</span>

                        <span>
                            ⭐ ${rating.toFixed(1)}
                        </span>

                        ${
                            place.ai_score !== undefined
                            ? `<span>🤖 ${aiScore.toFixed(1)}%</span>`
                            : ""
                        }

                    </div>

                    ${getCrowdIndicator(place.crowd_level)}

                </div>
            `;

            container.appendChild(card);
        });
    }

    // =====================================================
    // LOAD DESTINATIONS
    // =====================================================

    async function loadDestinations() {

        try {

            const data = await fetchJSON(
                "/api/places"
            );

            allDestinations = Array.isArray(data)
                ? data
                : data.places || [];

            displayDestinations(
                allDestinations,
                destinationResults
            );

            populateRouteDestinations();

            updateFeedbackDestinations();

            initializeMap();

        } catch (error) {

            console.error(
                "Destination loading error:",
                error
            );

            showMessage(
                destinationResults,
                "Unable to load destinations."
            );
        }
    }

    // =====================================================
    // DESTINATION SEARCH
    // =====================================================

    function searchDestinations() {

        if (!destinationSearch) return;

        const query = destinationSearch.value
            .trim()
            .toLowerCase();

        const filtered = allDestinations.filter(place => {

            const searchable = [
                place.name,
                place.category,
                place.description
            ].join(" ").toLowerCase();

            return searchable.includes(query);
        });

        displayDestinations(
            filtered,
            destinationResults
        );
    }

    if (searchButton) {

        searchButton.addEventListener(
            "click",
            searchDestinations
        );
    }

    if (destinationSearch) {

        destinationSearch.addEventListener(
            "input",
            searchDestinations
        );
    }

    // =====================================================
    // AI RECOMMENDATION PLANNER
    // =====================================================

    if (recommendationForm) {

        recommendationForm.addEventListener(
            "submit",
            async event => {

                event.preventDefault();

                showMessage(
                    recommendationResults,
                    "Generating AI recommendations..."
                );

                try {

                    const formData = new FormData(
                        recommendationForm
                    );

                    const interestsValue =
                        formData.get("interests") || "";

                    const interests = String(
                        interestsValue
                    )
                        .split(",")
                        .map(item => item.trim())
                        .filter(Boolean);

                    const budget = Number(
                        formData.get("budget") || 1000
                    );

                    const availableTime = Number(
                        formData.get("available_time") || 180
                    );

                    const crowdPreference = String(
                        formData.get("crowd_preference") || "low"
                    ).toLowerCase();

                    const data = await fetchJSON(
                        "/api/recommend",
                        {
                            method: "POST",

                            body: JSON.stringify({

                                interests: interests,

                                budget: budget,

                                available_time: availableTime,

                                crowd_preference: crowdPreference

                            })
                        }
                    );

                    const recommendations =
                        data.recommendations || [];

                    displayDestinations(
                        recommendations,
                        recommendationResults
                    );

                } catch (error) {

                    console.error(error);

                    showMessage(
                        recommendationResults,
                        "Unable to generate recommendations. Please try again."
                    );
                }
            }
        );
    }

    // =====================================================
    // HIDDEN GEMS
    // =====================================================

    async function loadHiddenGems() {

        if (!hiddenGemsResults) return;

        try {

            const data = await fetchJSON(
                "/api/hidden-gems"
            );

            const gems = Array.isArray(data)
                ? data
                : data.hidden_gems || [];

            displayDestinations(
                gems,
                hiddenGemsResults
            );

        } catch (error) {

            console.error(
                "Hidden Gems error:",
                error
            );

            showMessage(
                hiddenGemsResults,
                "Unable to load Hidden Gems."
            );
        }
    }

    // =====================================================
    // INTERACTIVE MAP
    // =====================================================

    function initializeMap() {

        const mapElement = document.getElementById("map");

        if (!mapElement || !window.L) return;

        if (!map) {

            map = L.map("map").setView(
                [12.9716, 77.5946],
                11
            );

            L.tileLayer(
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                {
                    maxZoom: 19,
                    attribution:
                        "&copy; OpenStreetMap contributors"
                }
            ).addTo(map);
        }

        markers.forEach(marker => map.removeLayer(marker));

        markers = [];

        allDestinations.forEach(place => {

            if (!validCoordinates(place)) return;

            const crowd = escapeHTML(
                String(place.crowd_level || "medium").toUpperCase()
            );

            const popup = `
                <b>${escapeHTML(place.name)}</b>
                <br>
                Category: ${escapeHTML(place.category)}
                <br>
                Crowd Level: ${crowd}
                <br>
                <small>Simulated demo data</small>
            `;

            const marker = L.marker([
                getLatitude(place),
                getLongitude(place)
            ])
                .addTo(map)
                .bindPopup(popup);

            markers.push(marker);
        });
    }

    // =====================================================
    // ROUTE DESTINATION SELECTOR
    // =====================================================

    function populateRouteDestinations() {

        if (!routeSelect) return;

        routeSelect.replaceChildren();

        allDestinations.forEach(place => {

            if (!validCoordinates(place)) return;

            const option = document.createElement("option");

            option.value = place.name;

            option.textContent = place.name;

            routeSelect.appendChild(option);
        });
    }

    // =====================================================
    // ROUTE OPTIMIZATION
    // =====================================================

    if (optimizeRouteButton) {

        optimizeRouteButton.addEventListener(
            "click",
            async () => {

                if (!routeSelect || !routeResults) return;

                const selected = Array.from(
                    routeSelect.selectedOptions
                ).map(option => option.value);

                if (selected.length < 2) {

                    showMessage(
                        routeResults,
                        "Please select at least two destinations."
                    );

                    return;
                }

                showMessage(
                    routeResults,
                    "Optimizing your route..."
                );

                try {

                    const data = await fetchJSON(
                        "/api/optimize-route",
                        {
                            method: "POST",

                            body: JSON.stringify({
                                destinations: selected
                            })
                        }
                    );

                    if (!data.success) {

                        throw new Error(
                            data.message || "Route optimization failed."
                        );
                    }

                    const route =
                        data.optimized_route || [];

                    routeResults.replaceChildren();

                    const heading = document.createElement("h3");

                    heading.textContent =
                        "Your Optimized Route";

                    routeResults.appendChild(heading);

                    const list = document.createElement("ol");

                    route.forEach(place => {

                        const item = document.createElement("li");

                        const name = typeof place === "string"
                            ? place
                            : place.name;

                        item.textContent = name || "Destination";

                        list.appendChild(item);
                    });

                    routeResults.appendChild(list);

                    const distance = document.createElement("p");

                    distance.textContent =
                        `Approximate distance: ${
                            Number(data.total_distance_km || 0).toFixed(2)
                        } km`;

                    routeResults.appendChild(distance);

                    const note = document.createElement("small");

                    note.textContent =
                        data.distance_type ||
                        "Approximate straight-line distance";

                    routeResults.appendChild(note);

                    const crowdNote = document.createElement("p");

                    crowdNote.textContent =
                        "Crowd levels are displayed separately; this route is ordered by approximate distance.";

                    routeResults.appendChild(crowdNote);

                } catch (error) {

                    console.error(
                        "Route optimization error:",
                        error
                    );

                    showMessage(
                        routeResults,
                        error.message || "Unable to optimize route."
                    );
                }
            }
        );
    }

    // =====================================================
    // FEEDBACK DESTINATION OPTIONS
    // =====================================================

    function updateFeedbackDestinations() {

        if (!feedbackDestination) return;

        feedbackDestination.replaceChildren();

        allDestinations.forEach(place => {

            const option = document.createElement("option");

            option.value = place.name;

            option.textContent = place.name;

            feedbackDestination.appendChild(option);
        });
    }

    // =====================================================
    // USER FEEDBACK
    // =====================================================

    if (feedbackForm) {

        feedbackForm.addEventListener(
            "submit",
            async event => {

                event.preventDefault();

                try {

                    const destination =
                        feedbackDestination?.value;

                    const action =
                        feedbackAction?.value;

                    const rating = Number(
                        feedbackRating?.value || 0
                    );

                    if (!destination || !action) {

                        throw new Error(
                            "Please select a destination and feedback type."
                        );
                    }

                    if (action === "rating" && (
                        rating < 1 || rating > 5
                    )) {

                        throw new Error(
                            "Please select a rating between 1 and 5."
                        );
                    }

                    await fetchJSON(
                        "/api/feedback",
                        {
                            method: "POST",

                            body: JSON.stringify({

                                destination_name: destination,

                                action: action,

                                rating: action === "rating"
                                    ? rating
                                    : null

                            })
                        }
                    );

                    showMessage(
                        feedbackStatus,
                        "Thank you! Your feedback was submitted successfully."
                    );

                    feedbackForm.reset();

                } catch (error) {

                    console.error(
                        "Feedback error:",
                        error
                    );

                    showMessage(
                        feedbackStatus,
                        error.message || "Unable to submit feedback."
                    );
                }
            }
        );
    }

    // =====================================================
    // START APPLICATION
    // =====================================================

    loadDestinations();

    loadHiddenGems();

});
