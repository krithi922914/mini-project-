let map;


/* =====================================================
   INITIALIZE MAP
===================================================== */

function initializeMap() {

    map = L.map("tourism-map").setView(
        [12.9716, 77.5946],
        12
    );


    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,
            attribution:
                '&copy; OpenStreetMap contributors'
        }
    ).addTo(map);


    loadPlaces();

}


/* =====================================================
   LOAD TOURISM PLACES
===================================================== */

async function loadPlaces() {

    try {

        const response =
            await fetch("/api/places");

        const places =
            await response.json();


        places.forEach(place => {

            let crowdColor;


            if (place.crowd_level < 45) {

                crowdColor = "#20a86b";

            }

            else if (place.crowd_level < 70) {

                crowdColor = "#e6a51d";

            }

            else {

                crowdColor = "#e45757";

            }


            const marker =
                L.circleMarker(
                    [
                        place.latitude,
                        place.longitude
                    ],
                    {
                        radius: 9,
                        fillColor: crowdColor,
                        color: "#ffffff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.9
                    }
                );


            marker.bindPopup(`

                <div style="min-width:210px">

                    <h3 style="
                        margin-bottom:6px;
                        font-size:15px;
                    ">
                        ${place.name}
                    </h3>

                    <p style="
                        color:#777;
                        font-size:11px;
                        margin-bottom:8px;
                    ">
                        ${place.description}
                    </p>

                    <div style="
                        display:flex;
                        gap:8px;
                        flex-wrap:wrap;
                    ">

                        <span>
                            ⭐ ${place.rating}
                        </span>

                        <span>
                            👥 ${place.crowd_level}%
                        </span>

                        <span>
                            ₹${place.entry_fee}
                        </span>

                    </div>

                </div>

            `);


            marker.addTo(map);

        });


    }

    catch(error) {

        console.error(
            "Unable to load tourism data:",
            error
        );

    }

}


/* =====================================================
   OPEN AI PLANNER
===================================================== */

function openPlanner() {

    document
        .getElementById("plannerModal")
        .classList.add("show");

}


/* =====================================================
   CLOSE AI PLANNER
===================================================== */

function closePlanner() {

    document
        .getElementById("plannerModal")
        .classList.remove("show");

}


/* =====================================================
   GENERATE AI RECOMMENDATIONS
===================================================== */

async function generateRecommendations() {

    const category =
        document.getElementById("interest").value;


    const budget =
        document.getElementById("budget").value;


    const availableTime =
        document.getElementById("availableTime").value;


    const crowdPreference =
        document.getElementById("crowdPreference").value;


    const resultContainer =
        document.getElementById(
            "recommendationResults"
        );


    resultContainer.innerHTML = `

        <div style="
            padding:20px;
            text-align:center;
            color:#777;
            font-size:11px;
        ">

            🤖 AI is analysing your preferences...

        </div>

    `;


    try {

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

                        category:
                            category,

                        budget:
                            budget,

                        available_time:
                            availableTime,

                        crowd_preference:
                            crowdPreference

                    })
                }
            );


        const recommendations =
            await response.json();


        if (!recommendations.length) {

            resultContainer.innerHTML = `

                <p>
                    No suitable destinations found.
                </p>

            `;

            return;

        }


        resultContainer.innerHTML = `

            <h3 style="
                font-size:13px;
                margin-bottom:12px;
            ">
                ✨ AI Recommended Destinations
            </h3>

        `;


        recommendations.forEach(
            (place, index) => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "recommendation";


                card.innerHTML = `

                    <div class="
                        recommendation-header
                    ">

                        <h3>
                            ${index + 1}.
                            ${place.name}
                        </h3>

                        <strong style="
                            color:#7057e8;
                            font-size:11px;
                        ">
                            ${place.score}
                        </strong>

                    </div>

                    <p>
                        ${place.description}
                    </p>

                    <div class="
                        recommendation-meta
                    ">

                        <span>
                            ${place.category}
                        </span>

                        <span>
                            ⭐ ${place.rating}
                        </span>

                        <span>
                            👥 ${place.crowd_level}%
                        </span>

                        <span>
                            ₹${place.entry_fee}
                        </span>

                        <span>
                            ${place.visit_time} min
                        </span>

                    </div>

                `;


                resultContainer.appendChild(
                    card
                );

            }
        );


    }

    catch(error) {

        console.error(error);


        resultContainer.innerHTML = `

            <div style="
                color:#e45757;
                padding:10px;
            ">

                Something went wrong while
                generating recommendations.

            </div>

        `;

    }

}


/* =====================================================
   START
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    initializeMap
);