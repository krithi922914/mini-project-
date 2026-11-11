// ======================================================
// MAP
// ======================================================

const map = L.map("map").setView(
    [12.9716, 77.5946],
    12
);


L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,

        attribution:
            "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// ======================================================
// MARKERS
// ======================================================

let markers = [];


// ======================================================
// LOAD ALL TOURISM PLACES
// ======================================================

async function loadPlaces() {

    try {

        const response =
            await fetch("/api/places");

        const places =
            await response.json();


        places.forEach(place => {

            addMarker(place);

        });

    }

    catch(error) {

        console.error(
            "Unable to load places:",
            error
        );

    }

}


function addMarker(place) {

    const marker =
        L.marker([
            place.latitude,
            place.longitude
        ]).addTo(map);


    marker.bindPopup(`

        <strong>
            ${place.name}
        </strong>

        <br>

        ${place.category}

        <br>

        ⭐ ${place.rating}

        <br>

        👥 Crowd:
        ${place.crowd_level}%

        <br>

        ₹${place.price}

    `);


    markers.push(marker);

}


// ======================================================
// GET USER INTERESTS
// ======================================================

function getInterests() {

    const checkboxes =
        document.querySelectorAll(
            ".interest:checked"
        );


    return Array.from(
        checkboxes
    ).map(
        checkbox => checkbox.value
    );

}


// ======================================================
// GENERATE RECOMMENDATIONS
// ======================================================

async function getRecommendations() {

    const interests =
        getInterests();


    const budget =
        Number(
            document.getElementById(
                "budget"
            ).value
        );


    const availableTime =
        Number(
            document.getElementById(
                "time"
            ).value
        );


    const crowdPreference =
        document.getElementById(
            "crowd"
        ).value;


    const results =
        document.getElementById(
            "results"
        );


    // ----------------------------------------------
    // Validation
    // ----------------------------------------------

    if (interests.length === 0) {

        alert(
            "Please select at least one interest."
        );

        return;

    }


    // ----------------------------------------------
    // Loading state
    // ----------------------------------------------

    results.innerHTML = `

        <div class="empty">

            <div>🧠</div>

            <h3>
                SmartTour AI is thinking...
            </h3>

            <p>
                Analysing your interests,
                budget, time and crowd preference.
            </p>

        </div>

    `;


    try {

        // ------------------------------------------
        // SEND DATA TO FLASK
        // ------------------------------------------

        const response =
            await fetch(
                "/api/recommend",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        interests:
                            interests,

                        budget:
                            budget,

                        available_time:
                            availableTime,

                        crowd_preference:
                            crowdPreference

                    })

                }
            );


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.error
            );

        }


        // ------------------------------------------
        // DISPLAY RESULTS
        // ------------------------------------------

        displayRecommendations(
            data.recommendations
        );


    }

    catch(error) {

        console.error(error);


        results.innerHTML = `

            <div class="empty">

                <div>❌</div>

                <h3>
                    AI error
                </h3>

                <p>
                    ${error.message}
                </p>

            </div>

        `;

    }

}


// ======================================================
// DISPLAY RECOMMENDATIONS
// ======================================================

function displayRecommendations(
    recommendations
) {

    const results =
        document.getElementById(
            "results"
        );


    if (
        !recommendations ||
        recommendations.length === 0
    ) {

        results.innerHTML = `

            <div class="empty">

                <div>🔎</div>

                <h3>
                    No recommendations found
                </h3>

                <p>
                    Try increasing your budget
                    or available time.
                </p>

            </div>

        `;

        return;

    }


    results.innerHTML = "";


    // Remove old markers

    markers.forEach(
        marker =>
            map.removeLayer(marker)
    );


    markers = [];


    // ----------------------------------------------
    // Display cards
    // ----------------------------------------------

    recommendations.forEach(
        (place, index) => {


            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "recommendation";


            let reasonsHTML =
                "";


            place.reasons.forEach(
                reason => {

                    reasonsHTML += `
                        <li>
                            ${reason}
                        </li>
                    `;

                }
            );


            card.innerHTML = `

                <div
                    class="recommendation-top"
                >

                    <h3>
                        ${index + 1}.
                        ${place.name}
                    </h3>

                    <span class="ai-score">
                        AI ${place.ai_score}%
                    </span>

                </div>


                <span class="category">
                    ${place.category}
                </span>


                <p
                    class="
                        recommendation-description
                    "
                >
                    ${place.description}
                </p>


                <div class="metadata">

                    <span>
                        ⭐ ${place.rating}
                    </span>

                    <span>
                        👥 ${place.crowd_level}%
                    </span>

                    <span>
                        ₹${place.price}
                    </span>

                    <span>
                        ⏱ ${place.visit_time} min
                    </span>

                </div>


                <div class="reasons">

                    <strong>
                        Why AI recommended this:
                    </strong>

                    <ul>
                        ${reasonsHTML}
                    </ul>

                </div>

            `;


            results.appendChild(
                card
            );


            // ------------------------------------------
            // MAP MARKER
            // ------------------------------------------

            addRecommendationMarker(
                place,
                index
            );

        }
    );


    // ----------------------------------------------
    // Fit map around recommendations
    // ----------------------------------------------

    if (recommendations.length > 0) {

        const bounds =
            recommendations.map(
                place => [
                    place.latitude,
                    place.longitude
                ]
            );


        map.fitBounds(
            bounds,
            {
                padding: [40, 40]
            }
        );

    }

}


// ======================================================
// RECOMMENDATION MAP MARKER
// ======================================================

function addRecommendationMarker(
    place,
    index
) {

    const marker =
        L.marker([
            place.latitude,
            place.longitude
        ]).addTo(map);


    marker.bindPopup(`

        <strong>
            #${index + 1}
            ${place.name}
        </strong>

        <br>

        AI Score:
        ${place.ai_score}%

        <br>

        ⭐ ${place.rating}

        <br>

        👥 Crowd:
        ${place.crowd_level}%

    `);


    markers.push(marker);

}


// ======================================================
// INITIAL LOAD
// ======================================================

loadPlaces();