// Variables to store selected team values
let selectedTeam = "";
let selectedTeam2 = "";
let numSims = 1;
let first = (second = third = false);
let userLineup1 = [];
let userLineup2 = [];

// Get the dropdown elements and the Run Simulation button
const teamSelect = document.getElementById("team1");
const team2Select = document.getElementById("team2");
const numSimsInput = document.getElementById("numSimsInput");
const runSimulationBtn = document.getElementById("runSimulation");
const nextSimulationBtn = document.getElementById("nextSim");
const continueBtn = document.getElementById("continue");
const lineupContainer1 = document.getElementById("lineup1");
const lineupContainer2 = document.getElementById("lineup2");
const simNotRunning = document.querySelectorAll(".simNotRunning");
const simRunning = document.querySelectorAll(".simRunning");
const lineupsHtml = document.querySelector(".lineups");
// ---- NEW: bridge old IDs to the new UI ----
const scoreLineEl  = document.getElementById('scoreLine') 
const playResultEl = document.getElementById('playResult') 
                   || document.getElementById('result') 
                   || document.querySelector('.result');

const outsEl = document.querySelector('.outs')
const awayPlayerEl = document.getElementById('awayPlayer') 
const homePlayerEl= document.getElementById('homePlayer') 
const outsDotsEl = document.getElementById('outsDots');


lineupsHtml.classList.add("hidden");
let simEnded = false;
const tableBody1 = document
  .getElementById("playerTable1")
  .getElementsByTagName("tbody")[0];
const tableBody2 = document
  .getElementById("playerTable2")
  .getElementsByTagName("tbody")[0];
const boxScoreTable = document
  .getElementById("boxScore")
  .getElementsByTagName("tbody")[0];

nextSimulationBtn.classList.add("hidden");
simRunning.forEach((item) => {
  item.classList.add("hidden");
});
// Add event listeners for when the selection changes on both dropdowns
teamSelect.addEventListener("change", () => {
  selectedTeam = teamSelect.value; // Update selected team1
  lineupsHtml.classList.remove("hidden");

  // populateLineup()
  fetch("/get-lineup?team=" + selectedTeam)
    .then((response) => response.json())
    .then((data) => {
      populateLineup1(data.players);
    }); // Assuming the response gives an array of players
});

team2Select.addEventListener("change", () => {
  selectedTeam2 = team2Select.value; // Update selected team2
  lineupsHtml.classList.remove("hidden");

  fetch("/get-lineup?team=" + selectedTeam2)
    .then((response) => response.json())
    .then((data) => {
      // console.log("Hello");
      // console.log(data.players[0]);
      populateLineup2(data.players);
    }); // Assuming the response gives an array of players
});

function ensureRows(tbody, rowCount, colCount) {
  // add rows if missing
  while (tbody.rows.length < rowCount) {
    const tr = tbody.insertRow();
    for (let i = 0; i < colCount; i++) tr.insertCell();
  }
  // trim extra rows (fresh sim)
  while (tbody.rows.length > rowCount) {
    tbody.deleteRow(-1);
  }
}

// convenience: count columns from the table header
function getColCount(tableId) {
  const thead = document.querySelector(`#${tableId} thead tr`);
  return thead ? thead.children.length : 0;
}


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
  return Array.from(document.querySelectorAll("#lineup1 li")).map(
    (li) => li.textContent
  );
}
function getUserLineup2() {
  return Array.from(document.querySelectorAll("#lineup2 li")).map(
    (li) => li.textContent
  );
}

function updateBoxScoreRows(data){
  if (!boxScoreTable) return;

  let row = boxScoreTable.rows[0];
  if (row){
    row.cells[0].textContent = data.team1_box_score["Team"];
    for (let i = 1; i <= 9; i++) row.cells[i].textContent = data.team1_box_score[String(i)];
    row.cells[10].textContent = data.team1_box_score["R"];
    row.cells[11].textContent = data.team1_box_score["H"];
    row.cells[12].textContent = data.team1_box_score["E"];
  }

  row = boxScoreTable.rows[1];
  if (row){
    row.cells[0].textContent = data.team2_box_score["Team"];
    for (let i = 1; i <= 9; i++) row.cells[i].textContent = data.team2_box_score[String(i)];
    row.cells[10].textContent = data.team2_box_score["R"];
    row.cells[11].textContent = data.team2_box_score["H"];
    row.cells[12].textContent = data.team2_box_score["E"];
  }
}

function renderOuts(outs = 0){
  if (!outsDotsEl) return;
  const dots = outsDotsEl.querySelectorAll('.dot');
  dots.forEach((dot, i) => dot.classList.toggle('on', i < outs));
  outsDotsEl.setAttribute('aria-label', `Outs: ${outs}`);
  console.log(outs);
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
  if (!nextSimulationBtn.classList.contains("hidden")) {
    nextSimulationBtn.classList.add("hidden");
    console.log("hiding");
  } else console.log("already hidden");

  console.log(nextSimulationBtn.classList.contains("hidden"));
  simNotRunning.forEach((item) => {
    item.classList.remove("hidden");
  });
  simRunning.forEach((item) => {
    item.classList.add("hidden");
  });
  // lineupContainer1.classList.add("lineups");
  // lineupContainer2.classList.add("lineups");
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
  // if (!nextSimulationBtn.classList.contains("hidden")) {
  //   nextSimulationBtn.classList.add("hidden");
  // }
  fetchUpdates();
  // document.getElementById("simulationState").innerHTML = `
  //   <p>In Progress</p>
  // `;
  // Check if both teams are selected
  numSims = numSimsInput.value;
  if (numSims < 3) {
    console.log("under 3 sims ");
    simRunning.forEach((item) => {
      item.classList.remove("hidden");
    });
  }
  if (selectedTeam && selectedTeam2) {
    // Prepare the data to send
    // console.log(team1);
    // console.log(team2);
    const data = {
      team1: selectedTeam,
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
      const msgTarget = playResultEl || scoreLineEl;
      if (msgTarget) msgTarget.textContent = 'Please select both teams before running the simulation.';

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
        if (data.sim_game) {
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
  if (!simEnded) {
    nextSimulationBtn.classList.remove("hidden");
    simEnded = true;
  }
}

function updateUI(data) {
  if (
    !data.gameOver ||
    (numSims > 2 && data.current_simulation_number == numSims)
  ) {
    simEnded = false;
  }
  if (!data.gameOver && numSims < 3) {
    const cols1 = getColCount('playerTable1');   // should be 10 if you keep AVG & OPS
    const cols2 = getColCount('playerTable2');

    const rows1 = data.team1_hitters_results?.length || 0;
    const rows2 = data.team2_hitters_results?.length || 0;

    ensureRows(tableBody1, rows1, cols1);
    ensureRows(tableBody2, rows2, cols2);
    data.team1_hitters_names.forEach((name, index) => {
      const row = tableBody1.rows[index];
      if (row) {
        row.cells[0].textContent = data.team1_hitters_results[index]["Name"];
        row.cells[1].textContent =
          data.team1_hitters_results[index]["Position"];
        row.cells[2].textContent = data.team1_hitters_results[index]["AB"];
        row.cells[3].textContent = data.team1_hitters_results[index]["R"];
        row.cells[4].textContent = data.team1_hitters_results[index]["H"];
        row.cells[5].textContent = data.team1_hitters_results[index]["RBI"];
        row.cells[6].textContent = data.team1_hitters_results[index]["BB"];
        row.cells[7].textContent = data.team1_hitters_results[index]["K"];
        row.cells[8].textContent = data.team1_hitters_results[index]["AVG"];
        row.cells[9].textContent = data.team1_hitters_results[index]["OPS"];
      }
    });
    data.team2_hitters_names.forEach((name, index) => {
      const row = tableBody2.rows[index];
      if (row) {
        row.cells[0].textContent = data.team2_hitters_results[index]["Name"];
        row.cells[1].textContent =
          data.team2_hitters_results[index]["Position"];
        row.cells[2].textContent = data.team2_hitters_results[index]["AB"];
        row.cells[3].textContent = data.team2_hitters_results[index]["R"];
        row.cells[4].textContent = data.team2_hitters_results[index]["H"];
        row.cells[5].textContent = data.team2_hitters_results[index]["RBI"];
        row.cells[6].textContent = data.team2_hitters_results[index]["BB"];
        row.cells[7].textContent = data.team2_hitters_results[index]["K"];
        row.cells[8].textContent = data.team2_hitters_results[index]["AVG"];
        row.cells[9].textContent = data.team2_hitters_results[index]["OPS"];
      }
    });

    let row = boxScoreTable.rows[0];
    row.cells[0].textContent = data.team1_box_score["Team"];
    row.cells[1].textContent = data.team1_box_score["1"];
    row.cells[2].textContent = data.team1_box_score["2"];
    row.cells[3].textContent = data.team1_box_score["3"];
    row.cells[4].textContent = data.team1_box_score["4"];
    row.cells[5].textContent = data.team1_box_score["5"];
    row.cells[6].textContent = data.team1_box_score["6"];
    row.cells[7].textContent = data.team1_box_score["7"];
    row.cells[8].textContent = data.team1_box_score["8"];
    row.cells[9].textContent = data.team1_box_score["9"];
    row.cells[10].textContent = data.team1_box_score["R"];
    row.cells[11].textContent = data.team1_box_score["H"];
    row.cells[12].textContent = data.team1_box_score["E"];
    row = boxScoreTable.rows[1];
    row.cells[0].textContent = data.team2_box_score["Team"];
    row.cells[1].textContent = data.team2_box_score["1"];
    row.cells[2].textContent = data.team2_box_score["2"];
    row.cells[3].textContent = data.team2_box_score["3"];
    row.cells[4].textContent = data.team2_box_score["4"];
    row.cells[5].textContent = data.team2_box_score["5"];
    row.cells[6].textContent = data.team2_box_score["6"];
    row.cells[7].textContent = data.team2_box_score["7"];
    row.cells[8].textContent = data.team2_box_score["8"];
    row.cells[9].textContent = data.team2_box_score["9"];
    row.cells[10].textContent = data.team2_box_score["R"];
    row.cells[11].textContent = data.team2_box_score["H"];
    row.cells[12].textContent = data.team2_box_score["E"];
  }
  let runnerValues = Object.values(data.runners);
  let runnerKeys = Object.keys(data.runners);
  let runnerString = "";
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
    renderOuts(0);
    document.getElementById("first-base").style.backgroundColor = "lightblue";
    document.getElementById("second-base").style.backgroundColor = "lightblue";
    document.getElementById("third-base").style.backgroundColor = "lightblue";
    console.log("over");
    // document.getElementById(
      //   "simulationState"
      // ).innerHTML = `<p>Simulation Finished</p>`;
      simulationEnded();
    } else if (numSims <= 2) {
      if (playResultEl) playResultEl.textContent = data.resultString || "";
      const half = data.topInning ? "top" : "bot";
      const scoreText = `${data.team1_name}: ${data.team1_runs}  ${half} ${data.inning}  ${data.team2_name}: ${data.team2_runs}`;
      if (scoreLineEl){
        if (scoreLineEl.id === 'scoreLine'){
          scoreLineEl.textContent = scoreText;
        } else {
          scoreLineEl.innerHTML = `
            <p>${scoreText}</p>
          `;
        }
      }

      // --- outs & runners (new .outs or old #below) ---
      if (outsEl){
        if (outsEl.classList && outsEl.classList.contains('outs')){
          // console.log("hello");
          // renderOuts(data.outs);
          // outsEl.textContent = `Outs: ${data.outs}`;
          // If you have a separate runners area, update it here too (e.g. #runners)
          const runnersEl = document.getElementById('runners');
          if (runnersEl) runnersEl.innerHTML = runnerString;
        } else {
          outsEl.innerHTML = `
            <p>Outs: ${data.outs}</p>
            <p style="min-height: 7em; white-space: pre-line;">${runnerString}</p>
          `;
        }
      }

      // --- hitter & pitcher cards (new #hitterInfo/#pitcherInfo or old #AwayPlayer/#HomePlayer) ---
      if (data.topInning){
        if (awayPlayerEl) awayPlayerEl.innerHTML = `${data.hitter}`;
        // if (hitterInfoEl) hitterInfoEl.innerHTML = `Hitter: ${data.hitter}<br>On Deck: ${data.onDeckHitter}`;
        if (homePlayerEl) homePlayerEl.innerHTML = `${data.pitcher}`;
      } else {
        // if (hitterInfoEl) hitterInfoEl.innerHTML = `Hitter: ${data.hitter}<br>On Deck: ${data.onDeckHitter}`;
        if (awayPlayerEl) awayPlayerEl.innerHTML = `${data.pitcher}`;
        if (homePlayerEl) homePlayerEl.innerHTML = `${data.hitter}`;
      }
      renderOuts(data.outs);
      document.getElementById("wins").innerHTML = ``;
  }
  updateBoxScoreRows(data);

  if (data.gameOver || numSims > 1) {
    console.log("Updating text");
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

function openSeasonPage() {
  fetch("/season", {
    method: "POST",
  });
}
