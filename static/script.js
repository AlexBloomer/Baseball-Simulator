// Variables to store selected team values
let selectedTeam1 = "";
let selectedTeam2 = "";
let numSims = 1;
let first = (second = third = false);
let userLineup1 = [];
let userLineup2 = [];

// Get the dropdown elements and the Run Simulation button
const team1Select = document.getElementById("team1");
const team2Select = document.getElementById("team2");
const numSimsInput = document.getElementById("numSimsInput");
const runSimulationBtn = document.getElementById("runSimulation");
const nextSimulationBtn = document.getElementById("nextSim");
const continueBtn = document.getElementById("continue");
const lineupContainer1 = document.getElementById("lineup1");
const lineupContainer2 = document.getElementById("lineup2");
const simNotRunning = document.querySelectorAll(".simNotRunning");
const simRunning = document.querySelectorAll(".simRunning");

nextSimulationBtn.classList.add("hidden");
simRunning.forEach((item) => {
  item.classList.add("hidden");
});
// Add event listeners for when the selection changes on both dropdowns
team1Select.addEventListener("change", () => {
  selectedTeam1 = team1Select.value; // Update selected team1
  // populateLineup()
  fetch("/get-lineup?team=" + selectedTeam1)
    .then((response) => response.json())
    .then((data) => {
      populateLineup1(data.players);
    }); // Assuming the response gives an array of players
});

team2Select.addEventListener("change", () => {
  selectedTeam2 = team2Select.value; // Update selected team2

  fetch("/get-lineup?team=" + selectedTeam2)
    .then((response) => response.json())
    .then((data) => {
      // console.log("Hello");
      // console.log(data.players[0]);
      populateLineup2(data.players);
    }); // Assuming the response gives an array of players
});

function populateLineup1(players) {
  // Clear the list
  lineupContainer1.innerHTML = "";

  // Add each player to the list
  players.forEach((player, index) => {
    const listItem = document.createElement("li");
    listItem.innerText = `${player}`;
    listItem.setAttribute("code", "id"); // Attach player id as data attribute
    lineupContainer1.appendChild(listItem);
  });

  // Make the lineup sortable
  new Sortable(lineupContainer1, {
    animation: 150, // Smooth dragging effect
  });
}
function populateLineup2(players) {
  // Clear the list
  lineupContainer2.innerHTML = "";

  // Add each player to the list
  players.forEach((player, index) => {
    const listItem = document.createElement("li");
    listItem.innerText = `${player}`;
    listItem.setAttribute("code", "id"); // Attach player id as data attribute
    lineupContainer2.appendChild(listItem);
  });

  // Make the lineup sortable
  new Sortable(lineupContainer2, {
    animation: 150, // Smooth dragging effect
  });
}

function getUserLineup1() {
  // console.log("HELLOOOOOOOOOOOOOOOOOOOOOOOO");
  // console.log(
  //   Array.from(document.querySelectorAll("#lineup1 li")).map(
  //     (li) => li.textContent
  //   )
  // );

  return Array.from(document.querySelectorAll("#lineup1 li")).map(
    (li) => li.textContent
  );
}
function getUserLineup2() {
  // console.log(
  //   Array.from(document.querySelectorAll("#lineup2 li")).map(
  //     (li) => li.textContent
  //   )
  // );
  return Array.from(document.querySelectorAll("#lineup2 li")).map(
    (li) => li.textContent
  );
}

function simulation_update() {
  // Fetch data from the server
  fetch("/simulation-update")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }
      return response.json(); // Parse the JSON from the response
    })
    .then((data) => {
      // Handle the data returned from the Flask app
      // console.log(data);
      // Update your HTML or do something with the received data
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

nextSimulationBtn.addEventListener("click", () => {
  simNotRunning.forEach((item) => {
    item.classList.remove("hidden");
  });
  simRunning.forEach((item) => {
    item.classList.add("hidden");
  });
  // lineupContainer1.classList.add("lineups");
  // lineupContainer2.classList.add("lineups");
  nextSimulationBtn.classList.add("hidden");
});

// Add event listener for the Run Simulation button
runSimulationBtn.addEventListener("click", () => {
  userLineup1 = getUserLineup1();
  userLineup2 = getUserLineup2();
  // lineupContainer1.innerHTML = "";
  // lineupContainer2.innerHTML = "";
  simNotRunning.forEach((item) => {
    item.classList.add("hidden");
  });
  simRunning.forEach((item) => {
    item.classList.remove("hidden");
  });
  nextSimulationBtn.classList.add("hidden");
  fetchUpdates();
  // document.getElementById("simulationState").innerHTML = `
  //   <p>In Progress</p>
  // `;
  // Check if both teams are selected
  numSims = numSimsInput.value;
  if (selectedTeam1 && selectedTeam2) {
    // Prepare the data to send
    // console.log(team1);
    // console.log(team2);
    const data = {
      team1: selectedTeam1,
      team2: selectedTeam2,
      numSims: numSims,
      lineup1: userLineup1,
      lineup2: userLineup2,
    };

    // Send the data to the Flask app
    fetch("/run-simulation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => response.json())
      .then((results) => {
        // Display the results
        fetchUpdates();
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    // Display a message if teams are not selected
    document.getElementById(
      "results"
    ).innerHTML = `<p>Please select both teams before running the simulation.</p>`;
  }
});

function fetchUpdates() {
  let isFetching = false;

  const intervalId = setInterval(() => {
    if (isFetching) return; // Skip this iteration if a fetch is already in progress
    isFetching = true;

    fetch("/simulation-update")
      .then((response) => response.json())
      .then((data) => {
        updateUI(data);
        if (data.gameOver) {
          clearInterval(intervalId);
        }
      })
      .finally(() => {
        isFetching = false; // Allow next fetch
      })
      .catch((error) => console.error("Fetch error:", error));
  }, 1000); // Adjust interval if necessary

  // const intervalId = setInterval(() => {
  //   fetch("/simulation-update")
  //     .then((response) => response.json())
  //     .then((data) => {
  //       updateUI(data); // Update the UI with the new data

  //       // Check if the game is over
  //       if (data.gameOver) {
  //         clearInterval(intervalId); // Stop polling for updates when the game is over
  //       }
  //     })
  //     .catch((error) => {
  //       console.error("There was a problem with the fetch operation:", error);
  //     });
  // }, 1000); // Poll every second for updates
}

function simulationEnded() {
  fetch("/simulation-ended", {
    method: "POST",
  });
  nextSimulationBtn.classList.remove("hidden");
}

function updateUI(data) {
  let runnerValues = Object.values(data.runners);
  let runnerKeys = Object.keys(data.runners);
  let runnerString = "";
  // console.log(data.team1_total_runs);
  first = runnerValues.includes(1);
  second = runnerValues.includes(2);
  third = runnerValues.includes(3);
  if (first) {
    runnerString += runnerKeys[runnerValues.indexOf(1)] + " on first<br>";
    document.getElementById("first-base").style.backgroundColor = "yellow";
  } else
    document.getElementById("first-base").style.backgroundColor = "lightblue";
  if (second) {
    runnerString += runnerKeys[runnerValues.indexOf(2)] + " on second<br>";
    document.getElementById("second-base").style.backgroundColor = "yellow";
  } else
    document.getElementById("second-base").style.backgroundColor = "lightblue";
  if (third) {
    runnerString += runnerKeys[runnerValues.indexOf(3)] + " on third<br>";
    document.getElementById("third-base").style.backgroundColor = "yellow";
  } else
    document.getElementById("third-base").style.backgroundColor = "lightblue";
  let x = "";
  if (data.topInning) {
    x = "top";
  } else {
    x = "bot";
  }
  // console.log(data.gameOver);
  if (data.gameOver) {
    document.getElementById("first-base").style.backgroundColor = "lightblue";
    document.getElementById("second-base").style.backgroundColor = "lightblue";
    document.getElementById("third-base").style.backgroundColor = "lightblue";
    // document.getElementById(
    //   "simulationState"
    // ).innerHTML = `<p>Simulation Finished</p>`;
    simulationEnded();
  } else if (numSims <= 2) {
    document.getElementById("results").innerHTML = `
        <p>${data.team1_name}: ${data.team1_runs}&nbsp;
        ${x} ${data.inning}&nbsp;
        ${data.team2_name}: ${data.team2_runs}</p>    
        <p>Hitter: ${data.hitter}</p>
        <p>Pitcher: ${data.pitcher}</p>
        <p>Outs: ${data.outs}</p>
        <p>Result: ${data.result}</p>
        <p>${runnerString}</p>
      `;
    document.getElementById("wins").innerHTML = ``;
  }
  if (data.gameOver || numSims > 1) {
    document.getElementById("wins").innerHTML = `
              <h2>Results:</h2>
              <p>${data.team1_name} Wins: ${data.team1_wins}</p>
              <p>${data.team2_name} Wins: ${data.team2_wins}</p>
              <p>${data.team1_name} Total Runs: ${data.team1_total_runs}</p>
              <p>${data.team2_name} Total Runs: ${data.team2_total_runs}</p>                      
          `;
  }
}

continueBtn.addEventListener("click", function () {
  fetch("/continue", { method: "POST" }).then(() => {
    // document.getElementById("continueButton").style.display = "none";
    fetchUpdates(); // Get the next update after continuing
  });
});
