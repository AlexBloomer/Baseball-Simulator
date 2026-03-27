let selectedTeam1 = "", selectedTeam2 = "";
let selectedYear1 = 2025, selectedYear2 = 2025;
let numSims = 1;
let userLineup1 = [], userLineup2 = [];

const teamSelect1 = document.getElementById("team1"), teamSelect2 = document.getElementById("team2");
const yearSelect1 = document.getElementById("pickYear1"), yearSelect2 = document.getElementById("pickYear2")
const numSimsInput = document.getElementById("numSimsInput");
const runSimulationBtn = document.getElementById("runSimulation");
const nextSimulationBtn = document.getElementById("nextSim");
const continueBtn = document.getElementById("continue");
const lineupContainer1 = document.getElementById("lineup1"), lineupContainer2 = document.getElementById("lineup2");
const simNotRunning = document.querySelectorAll(".simNotRunning");
const statCards = document.querySelectorAll(".statCards");
const winsEl = document.getElementById("wins");
const firstBase = document.getElementById("first-base"), secondBase = document.getElementById("second-base"), thirdBase = document.getElementById("third-base");
const runnerFirstEl = document.getElementById("runner-first"), runnerSecondEl = document.getElementById("runner-second"), runnerThirdEl = document.getElementById("runner-third");
const simRunning = document.querySelectorAll(".simRunning");
const lineupsHtml = document.querySelector(".lineups");
const scoreLineEl  = document.getElementById('scoreLine');
const playResultEl = document.getElementById('playResult');
const outsDotsEl = document.getElementById('outsDots');
const awayPlayerEl = document.getElementById('awayPlayer'), homePlayerEl= document.getElementById('homePlayer'); 
const tableBody1 = document.getElementById("playerTable1").getElementsByTagName("tbody")[0];
const tableBody2 = document.getElementById("playerTable2").getElementsByTagName("tbody")[0];
const team1Table = document.getElementById("t1Table").getElementsByTagName("tbody")[0];
const team2Table = document.getElementById("t2Table").getElementsByTagName("tbody")[0];
const boxScoreTable = document.getElementById("boxScore").getElementsByTagName("tbody")[0];
const postSimResults = document.getElementById("postSimResults");


postSimResults.classList.add("hidden");
winsEl.classList.add("hidden");
statCards.forEach((item) => {item.classList.add("hidden");});
nextSimulationBtn.classList.add("hidden");
lineupsHtml.classList.add("hidden");
simRunning.forEach((item) => {item.classList.add("hidden");});


loadTeams(selectedYear1, teamSelect1).then((team1) => {
  if (team1 == null) return;
  selectedTeam1 = team1;
  fillLineup(team1, selectedYear1, lineupContainer1);
});
loadTeams(selectedYear2, teamSelect2).then((team2) => {
  if (team2 == null) return;
  selectedTeam2 = team2;
  fillLineup(team2, selectedYear2, lineupContainer2);
});


fetch("/get-years")
  .then(res => res.json())
  .then(data => {
    data.years.forEach(year => {
      let option1 = document.createElement('option');
      option1.value = year;
      option1.text = year;
      let option2 = document.createElement('option');
      option2.value = year;
      option2.text = year;
      yearSelect1.appendChild(option1);
      yearSelect2.appendChild(option2);
    });
    yearSelect1.value = "2025";
    yearSelect2.value = "2025";
  });
  
teamSelect1.addEventListener("change", () => {
  selectedTeam1 = teamSelect1.value;
  fillLineup(selectedTeam1, selectedYear1, lineupContainer1);
});

teamSelect2.addEventListener("change", () => {
  selectedTeam2 = teamSelect2.value;
  fillLineup(selectedTeam2, selectedYear2, lineupContainer2);
});

function fillLineup(teamId, year, lineupContainer){
  lineupsHtml.classList.remove("hidden");
  fetch(`/get-lineup?team=${teamId}&year=${year}`)
  .then((response) => response.json())
  .then((data) => {
    populateLineup(lineupContainer, data.players);
  });
}

yearSelect1.addEventListener("change", () => {
  selectedYear1 = yearSelect1.value;
  loadTeams(selectedYear1, teamSelect1).then((team) => {
    if (team == null) return;
    selectedTeam1 = team;
    fillLineup(team, selectedYear1, lineupContainer1);
  });
});


yearSelect2.addEventListener("change", () => {
  selectedYear2 = yearSelect2.value;
  loadTeams(selectedYear2, teamSelect2).then((team) => {
    if (team == null) return;
    selectedTeam2 = team;
    fillLineup(team, selectedYear2, lineupContainer2);
  });
});


function loadTeams(year, dropdown){
  lineupsHtml.classList.remove("hidden");
  return fetch(`/get-teams?year=${year}`)
    .then(res => res.json())
    .then(data => {
      dropdown.innerHTML = '';
      data.teams.forEach(team => {
        let option = document.createElement('option');
        option.value = team.teamID;
        option.text = team.name;
        dropdown.appendChild(option);
      });
      return dropdown.options[0]?.value ?? null;
    });
}

function renumberLineup(container) {
  Array.from(container.children).forEach((li, index) => {
    li.querySelector(".badge").textContent = index + 1;
  });
}


function ensureRows(tbody, rowCount, colCount) {
  while (tbody.rows.length < rowCount) {
    const tr = tbody.insertRow();
    for (let i = 0; i < colCount; i++) tr.insertCell();
  }
  while (tbody.rows.length > rowCount) {
    tbody.deleteRow(-1);
  }
}

function getColCount(tableId) {
  const thead = document.querySelector(`#${tableId} thead tr`);
  return thead ? thead.children.length : 0;
}

function populateLineup(container, players) {
  container.innerHTML = "";
  index = 1;
  players.forEach((player) => {
    const listItem = document.createElement("li");
    const name = document.createElement("span");
    name.classList.add("name")
    name.textContent = player.Player;
    const num = document.createElement("span");
    num.className = "badge"
    num.textContent = index;
    listItem.append(num)
    listItem.append(name)
    container.appendChild(listItem);
    index++;
  });
  new Sortable(container, {
    animation: 150,
    onEnd: () => renumberLineup(container)
  });
}

function getUserLineup(selector) {
  return Array.from(document.querySelectorAll(selector)).map((li) => li.querySelector(".name").textContent);
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
}

nextSimulationBtn.addEventListener("click", () => {
  hidePostSimBase();
  simNotRunning.forEach((item) => {item.classList.remove("hidden");});
  simRunning.forEach((item) => {item.classList.add("hidden");});
});

runSimulationBtn.addEventListener("click", () => {
  hidePostSimBase();
  userLineup1 = getUserLineup("#lineup1 li");
  userLineup2 = getUserLineup("#lineup2 li");
  simNotRunning.forEach((item) => {item.classList.add("hidden");});

  numSims = Number(numSimsInput.value);
  if (numSims == 1) {
    simRunning.forEach((item) => {item.classList.remove("hidden");});
  }
  if (selectedTeam1 && selectedTeam2) {
    const data = {
      team1: selectedTeam1,
      team2: selectedTeam2,
      numSims: numSims,
      lineup1: userLineup1,
      lineup2: userLineup2,
      year1: selectedYear1,
      year2: selectedYear2
    };

    fetch("/run-simulation", {
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
  } else {
      const msgTarget = playResultEl || scoreLineEl;
      if (msgTarget) msgTarget.textContent = 'Please select both teams before running the simulation.';

    }
});

function fillHitterTable(tbody, results){
  results.forEach((result, index) => {
      const row = tbody.rows[index];
      if (row) {
        row.cells[0].textContent = result["Name"];
        row.cells[1].textContent = result["Position"];
        row.cells[2].textContent = result["AB"];
        row.cells[3].textContent = result["R"];
        row.cells[4].textContent = result["H"];
        row.cells[5].textContent = result["RBI"];
        row.cells[6].textContent = result["BB"];
        row.cells[7].textContent = result["K"];
        row.cells[8].textContent = result["AVG"];
        row.cells[9].textContent = result["OPS"];
      }
    });
}

function setRunner(baseEl, runnerEl, onBase, name){
  if (onBase){
    runnerEl.textContent = name;
    runnerEl.classList.remove("hidden")
    baseEl.style.backgroundColor = "yellow";
  }
  else {
    runnerEl.textContent = '';
    runnerEl.classList.add("hidden")
    baseEl.style.backgroundColor = "lightblue";
  }
}

function oneGame(data){
  if (!data.simOver) {
    statCards.forEach((item) => {item.classList.add("hidden");});

    const cols1 = getColCount('playerTable1'); 
    const cols2 = getColCount('playerTable2');
    const rows1 = data.team1_hitters_results?.length || 0;
    const rows2 = data.team2_hitters_results?.length || 0;
    ensureRows(tableBody1, rows1, cols1);
    ensureRows(tableBody2, rows2, cols2);
    fillHitterTable(tableBody1, data.team1_hitters_results);
    fillHitterTable(tableBody2, data.team2_hitters_results);
    let runnerValues = Object.values(data.runners), runnerKeys = Object.keys(data.runners);
    setRunner(firstBase, runnerFirstEl, runnerValues.includes(1), runnerKeys[runnerValues.indexOf(1)]);
    setRunner(secondBase, runnerSecondEl, runnerValues.includes(2), runnerKeys[runnerValues.indexOf(2)]);
    setRunner(thirdBase, runnerThirdEl, runnerValues.includes(3), runnerKeys[runnerValues.indexOf(3)]);

    if (playResultEl) playResultEl.textContent = data.resultString || "";
    const half = data.topInning ? "top" : "bot";
    const scoreText = `${data.team1_name}: ${data.team1_runs}  ${half} ${data.inning}  ${data.team2_name}: ${data.team2_runs}`;
    scoreLineEl.textContent = scoreText;
    if (data.topInning){
      if (awayPlayerEl) awayPlayerEl.innerHTML = `${data.hitter}`;
      if (homePlayerEl) homePlayerEl.innerHTML = `${data.pitcher}`;
    } else {
      if (awayPlayerEl) awayPlayerEl.innerHTML = `${data.pitcher}`;
      if (homePlayerEl) homePlayerEl.innerHTML = `${data.hitter}`;
    }

    renderOuts(data.outs);
    updateBoxScoreRows(data);
    winsEl.innerHTML = "";
  }
  else{
    renderOuts(0);
    firstBase.style.backgroundColor = "lightblue";
    secondBase.style.backgroundColor = "lightblue";
    thirdBase.style.backgroundColor = "lightblue";
    runnerFirstEl.textContent = "";
    runnerSecondEl.textContent = "";
    runnerThirdEl.textContent = "";
    runnerFirstEl.classList.add("hidden");
    runnerSecondEl.classList.add("hidden");
    runnerThirdEl.classList.add("hidden");
    showSingleSimResults(data);
    winsEl.innerHTML = `
    <h2>${data.team1_wins > data.team2_wins ? data.team1_name : data.team2_name} Wins!</h2>                    
    `;
    simulationEnded();
    
  }
}

function multipleGames(data){
  console.log(data);
  console.log(data.simOVer);
  statCards.forEach((item) => {
    item.classList.remove("hidden");
  });
  winsEl.classList.remove("hidden");
  winsEl.innerHTML = `
            <h3>Results:</h3>
            <p>${data.team2_name} Wins: ${data.team2_wins}</p>
            <p>${data.team1_name} Wins: ${data.team1_wins}</p>
            <p>${data.team1_name} Total Runs: ${data.team1_total_runs}</p>
            <p>${data.team2_name} Total Runs: ${data.team2_total_runs}</p>                      
        `;

  document.getElementById("t1Title").textContent = data.team1_name;
  document.getElementById("t2Title").textContent = data.team2_name;
  const cols1 = getColCount('t1Table');
  const cols2 = getColCount('t2Table');

  const rows1 = data.team1_hitters_results?.length || 0;
  const rows2 = data.team2_hitters_results?.length || 0;

  ensureRows(team1Table, rows1, cols1);
  ensureRows(team2Table, rows2, cols2);
  fillHitterTable(team1Table, data.team1_hitters_results);
  fillHitterTable(team2Table, data.team2_hitters_results);

  if(data.simOver){
    showMultiSimResults(data);
    simulationEnded();
    return;
  }
}

function fetchUpdates() {
  let isFetching = false;

  const intervalId = setInterval(() => {
    if (isFetching) return;
    isFetching = true;

    fetch("/simulation-update")
      .then((response) => response.json())
      .then((data) => {
        if (data.sim_game) {
          updateUI(data);
        }
        if (data.simOver) {
          clearInterval(intervalId);
        }
      })
      .finally(() => {
        isFetching = false;
      })
      .catch((error) => console.error("Fetch error:", error));
  }, 1000);
}

function showPostSimBase() {
  postSimResults.classList.remove("hidden");
  winsEl.classList.remove("hidden");
  nextSimulationBtn.classList.remove("hidden");
}

function hidePostSimBase() {
  postSimResults.classList.add("hidden");
  winsEl.classList.add("hidden");
  statCards.forEach((item) => {item.classList.add("hidden");});
  nextSimulationBtn.classList.add("hidden");
}

function showSingleSimResults(data) {
  showPostSimBase();
  statCards.forEach((item) => {item.classList.add("hidden");});

  winsEl.innerHTML = `
    <h2>${data.team1_runs > data.team2_runs ? data.team1_name : data.team2_name} Wins!</h2>
    <p>${data.team1_name}: ${data.team1_runs}</p>
    <p>${data.team2_name}: ${data.team2_runs}</p>
  `;
}

function showMultiSimResults(data) {
  showPostSimBase();
  statCards.forEach((item) => {item.classList.add("hidden");});

  winsEl.innerHTML = `
    <h3>Results:</h3>
    <p>${data.team1_name} Wins: ${data.team1_wins}</p>
    <p>${data.team2_name} Wins: ${data.team2_wins}</p>
    <p>${data.team1_name} Total Runs: ${data.team1_total_runs}</p>
    <p>${data.team2_name} Total Runs: ${data.team2_total_runs}</p>
  `;
}


function simulationEnded() {
  fetch("/simulation-ended", {
    method: "POST",
  });
  nextSimulationBtn.classList.remove("hidden");

}

function updateUI(data) {
  if(numSims == 1) oneGame(data)
  else multipleGames(data)
}

continueBtn.addEventListener("click", function () {
  fetch("/continue", { method: "POST" });
});

