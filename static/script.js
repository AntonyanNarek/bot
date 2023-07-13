function filterLogs() {
    let levelFilterSelect = document.getElementById('filter-select');
    let levelFilter = levelFilterSelect.value;

    let newFilterSelect = document.getElementById('filter_id_select');
    let newFilter = newFilterSelect.value;

    let logTableBody = document.getElementById('log-table-body');
    let logRows = logTableBody.getElementsByTagName('tr');

    for (let i = 0; i < logRows.length; i++) {
        let logRow = logRows[i];
        let logLevel = logRow.getElementsByClassName('log-level')[0].textContent;
        let logNewField = logRow.getElementsByTagName('td')[4].textContent;

        let levelMatch = levelFilter === 'all' || logLevel === levelFilter;
        let newFieldMatch = newFilter === 'all' || logNewField === newFilter;

        if (levelMatch && newFieldMatch) {
            logRow.style.display = '';
        } else {
            logRow.style.display = 'none';
        }
    }
}


function filterID() {
    let filterSelect = document.getElementById('filter_id_select');
    let selectedFilter = filterSelect.value;

    let logTableBody = document.getElementById('log-table-body');
    let logRows = logTableBody.getElementsByTagName('tr');

    for (let i = 0; i < logRows.length; i++) {
        let logRow = logRows[i];
        let logNewField = logRow.getElementsByTagName('td')[4].textContent;

        if (selectedFilter === 'all' || logNewField === selectedFilter) {
            logRow.style.display = '';
        } else {
            logRow.style.display = 'none';
        }
    }
    filterLogs();
}


function updateLogs() {
    fetch('/logs')
        .then(response => response.json())
        .then(data => {
            let logTableBody = document.getElementById('log-table-body');
            logTableBody.innerHTML = '';

            data.logs.forEach(log => {
                let row = document.createElement('tr');
                row.classList.add('log-' + log[1]);

                let logTime = document.createElement('td');
                logTime.textContent = log[0];
                row.appendChild(logTime);

                let logLevel = document.createElement('td');
                logLevel.classList.add('log-level');
                logLevel.textContent = log[1];
                row.appendChild(logLevel);

                let logFile = document.createElement('td');
                logFile.textContent = log[2];
                row.appendChild(logFile);

                let logFunc = document.createElement('td');
                logFunc.textContent = log[3];
                row.appendChild(logFunc);

                let logId = document.createElement('td');
                logId.textContent = log[4];
                row.appendChild(logId);

                let logMessage = document.createElement('td');
                logMessage.textContent = log[5];
                row.appendChild(logMessage);

                logTableBody.appendChild(row);
            });

            filterLogs();
        });
}

function refreshLogs() {
    updateLogs();
}

function autoRefreshLogs() {
    refreshLogs();
    setTimeout(autoRefreshLogs, 60000); // Обновление каждую минуту (60000 миллисекунд)
}

window.addEventListener('DOMContentLoaded', function () {
    filterLogs();
    autoRefreshLogs();
});
