const API_URL = "http://localhost:5003";

const form = document.getElementById("emergencyForm");
const message = document.getElementById("message");
const emergencyList = document.getElementById("emergencyList");
const loadButton = document.getElementById("loadEmergencies");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const data = {
        citizen_id: Number(document.getElementById("citizenId").value),
        type: document.getElementById("type").value,
        description: document.getElementById("description").value,
        location: document.getElementById("location").value,
        severity: document.getElementById("severity").value
    };

    try {
        const response = await fetch(`${API_URL}/emergencies`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            message.textContent = result.error || "Failed to report emergency";
            return;
        }

        message.textContent =
            `Emergency reported successfully. ID: ${result.emergency_id}`;

        form.reset();
        loadEmergencies();

    } catch (error) {
        message.textContent =
            "Unable to connect to Emergency Service.";
    }
});


async function loadEmergencies() {
    try {
        const response = await fetch(`${API_URL}/emergencies`);
        const emergencies = await response.json();

        emergencyList.innerHTML = "";

        if (emergencies.length === 0) {
            emergencyList.innerHTML = "<p>No emergencies reported.</p>";
            return;
        }

        emergencies.forEach(emergency => {
            const card = document.createElement("div");
            card.className = "emergency-card";

            card.innerHTML = `
                <p><strong>ID:</strong> ${emergency.emergency_id}</p>
                <p><strong>Citizen ID:</strong> ${emergency.citizen_id}</p>
                <p><strong>Type:</strong> ${emergency.type}</p>
                <p><strong>Description:</strong> ${emergency.description}</p>
                <p><strong>Location:</strong> ${emergency.location}</p>
                <p><strong>Severity:</strong> ${emergency.severity}</p>
                <p><strong>Status:</strong> ${emergency.status}</p>
                <p><strong>Created:</strong> ${emergency.created_at}</p>
            `;

            emergencyList.appendChild(card);
        });

    } catch (error) {
        emergencyList.innerHTML =
            "<p>Unable to connect to Emergency Service.</p>";
    }
}

loadButton.addEventListener("click", loadEmergencies);

loadEmergencies();