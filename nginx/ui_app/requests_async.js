async function sendPostRequest() {
    const firstName = document.getElementById("getFirstName").value;
    const lastName = document.getElementById("getLastName").value;
    const role = document.getElementById("role").value;
    const privacyCheck = document.getElementById("privacyCheck").checked;

    if (!firstName || !lastName || !role || !privacyCheck) {
        alert("Please fill in all required fields and agree to the privacy policy.");
        return;
    }
    const data = {
        first_name: firstName,
        last_name: lastName,
        role: role
    };
    try {
        const response = await fetch("http://localhost:8000", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const responseData = await response.json();
            console.log("Team member added:", responseData);
            updateTeamList(responseData.users);
        } else {
            console.error('Failed to add member:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function updateTeamList(teamMembers) {
    const teamList = document.getElementById("teamList");
    teamList.innerHTML = '';

    teamMembers.forEach(member => {
        const listItem = document.createElement("li");
        listItem.innerHTML = `${member.first_name} ${member.last_name}<br>${member.role}`;
        const trashIcon = document.createElement("span");
        trashIcon.classList.add("delete-icon");
        trashIcon.innerHTML = `<i class="fas fa-trash-alt"></i>`;

        trashIcon.onclick = async function () {
            try {
                const response = await fetch(`http://localhost:8000/${member.id}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                });
                if (response.ok) {
                    console.log("User deleted:", member);
                    updateTeamList(await fetchTeamMembers());
                } else {
                    console.error('Failed to delete user:', response.statusText);
                }
            } catch (error) {
                console.error('Error:', error);
            }
        };

        listItem.appendChild(trashIcon);
        teamList.appendChild(listItem);
    });
}
async function fetchTeamMembers() {
    try {
        const response = await fetch("http://localhost:8000");
        if (response.ok) {
            const data = await response.json();
            return data.users;
        } else {
            console.error("Failed to fetch team members:", response.statusText);
        }
    } catch (error) {
        console.error("Error fetching team members:", error);
    }
}

window.addEventListener('load', async function () {
    const teamMembers = await fetchTeamMembers();
    if (teamMembers) {
        updateTeamList(teamMembers);
    } else {
        console.error("Failed to fetch team members");
    }
});

