document.addEventListener('DOMContentLoaded', function() {
    updateStatus();
    setInterval(updateStatus, 5000); // Refresh status every 5 seconds.
    document.getElementById('clearAllHosts').addEventListener('click', function() {
        if (confirm('Are you sure you want to clear all hosts? This action cannot be undone.')) {
            fetch('/clear_hosts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(response => response.json())
              .then(data => {
                  alert(data.message);
                  updateStatus();
              })
              .catch(error => console.error('Error clearing hosts:', error));
        }
    });
});

document.getElementById('addHostForm').onsubmit = function(event) {
    event.preventDefault();
    const newHost = document.getElementById('newHost').value;
    const hostLabel = document.getElementById('hostLabel').value;
    const notificationsEnabled = document.getElementById('notificationsEnabled').checked;

    fetch('/add_host', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            host: newHost,
            label: hostLabel,
            notifications_enabled: notificationsEnabled
        })
    }).then(response => response.json())
      .then(data => {
          alert(data.message);
          updateStatus();
      })
      .catch(error => console.error('Error adding host:', error));

    document.getElementById('newHost').value = '';
    document.getElementById('hostLabel').value = '';
    document.getElementById('notificationsEnabled').checked = true;
};

function updateStatus() {
    fetch('/status').then(response => response.json()).then(data => {
        const statusTableBody = document.getElementById('statusTable').getElementsByTagName('tbody')[0];
        statusTableBody.innerHTML = '';

        Object.entries(data).forEach(([host, info]) => {
            const row = statusTableBody.insertRow();
            row.insertCell(0).innerText = info.label;
            row.insertCell(1).innerText = host;

            const statusCell = row.insertCell(2);
            statusCell.innerText = info.status;
            statusCell.classList.add(info.status === 'OK' ? 'status-ok' : 'status-ko');

            row.insertCell(3).innerText = formatDate(info.last_change);
            row.insertCell(4).innerText = formatDate(info.last_check);

            row.insertCell(5).innerText = formatDuration(info.up_duration);
            row.insertCell(6).innerText = formatDuration(info.down_duration);

            const responseTimeCell = row.insertCell(7);
            responseTimeCell.innerText = info.response_time ? `${info.response_time} ms` : 'N/A';

            const actionsCell = row.insertCell(8);
            const notifButton = createButton(info.notifications_enabled ? 'Notifications: ON' : 'Notifications: OFF', () => toggleNotifications(host));
            actionsCell.appendChild(notifButton);

            const removeButton = createButton('Remove', () => removeHost(host));
            actionsCell.appendChild(removeButton);
        });
    }).catch(error => console.error('Error fetching status:', error));
}

function createButton(text, onClickFunction) {
    const button = document.createElement('button');
    button.innerText = text;
    button.onclick = onClickFunction;
    button.classList.add('action-button');
    return button;
}

function toggleNotifications(host) {
    fetch('/toggle_notifications', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ host })
    }).then(() => updateStatus())
      .catch(error => console.error('Error toggling notifications:', error));
}

function removeHost(host) {
    if (confirm('Are you sure you want to remove this host?')) {
        fetch('/remove_host', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ host })
        }).then(() => updateStatus())
          .catch(error => console.error('Error removing host:', error));
    }
}

function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString();
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours}h ${minutes}m ${secs}s`;
}
