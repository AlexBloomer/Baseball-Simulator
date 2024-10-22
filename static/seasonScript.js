const simulateSeasonBtn = document.getElementById("simulateSeason");
const teamSelect = document.getElementById("team");
const lineupContainer = document.getElementById("lineup");
selectedTeam = "";
simEnded = true;

teamSelect.addEventListener("change", () => {
  selectedTeam = teamSelect.value; // Update selected team1
  // populateLineup()
  fetch("/get-lineup?team=" + selectedTeam)
    .then((response) => response.json())
    .then((data) => {
      populateLineup1(data.players);
    }); // Assuming the response gives an array of players
});

function populateLineup1(players) {
  // Clear the list
  lineupContainer.innerHTML = "";

  // Add each player to the list
  players.forEach((player, index) => {
    const listItem = document.createElement("li");
    listItem.innerText = `${player}`;
    listItem.setAttribute("code", "id"); // Attach player id as data attribute
    lineupContainer.appendChild(listItem);
  });

  // Make the lineup sortable
  new Sortable(lineupContainer, {
    animation: 150, // Smooth dragging effect
  });
}

simulateSeasonBtn.addEventListener("click", () => {
  //   console.log("is this running");
  userLineup = Array.from(document.querySelectorAll("#lineup li")).map(
    (li) => li.textContent
  );
  if (selectedTeam) {
    // Prepare the data to send
    // console.log(team1);
    // console.log(team2);
    const data = {
      team: selectedTeam,
      lineup: userLineup,
    };

    // Send the data to the Flask app
    fetch("/simulate-season", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((results) => {
        fetchUpdates();
      })
      .catch((error) => {
        console.error("Error:", error);
      });
    // fetchUpdates();
  } else {
    // Display a message if teams are not selected
    document.getElementById(
      "result"
    ).innerHTML = `<p>Please select both teams before running the simulation.</p>`;
  }
});

function fetchUpdates() {
  let isFetching = false;
  simEnded = false;
  const intervalId = setInterval(() => {
    // console.log("interval running");
    if (isFetching) return; // Skip this iteration if a fetch is already in progress
    isFetching = true;

    fetch("/simulation-update")
      .then((response) => response.json())
      .then((data) => {
        console.log(
          `${data.sim_game}\n${data.team}\n${data.wins}\n${data.losses}`
        );
        if (!data.sim_game) {
          console.log(`Team: ${data.team}`);
          updateUI(data);
        }
        if (data.gameOver) {
          clearInterval(intervalId);
        }
      })
      .finally(() => {
        isFetching = false; // Allow next fetch
      })
      .catch((error) => console.error("Fetch error:", error));
  }, 1000); // Adjust interval if necessary
}

function updateUI(data) {
  document.getElementById("result").innerHTML = `
        Team: ${data.team}<br>
        Wins: ${data.wins}<br>
        Losses: ${data.losses}<br>
    `;
  if (data.end_sim) {
    endsim();
  }
}

function endsim() {
  fetch("/simulation-ended", {
    method: "POST",
  });
  simEnded = true
}
