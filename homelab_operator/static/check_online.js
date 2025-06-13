/**
 * Checks the server status and updates the status dot class.
 * @param {string} endpoint - The URL to check.
 * @param {string} dotId - The DOM element ID of the status dot.
 */
async function check_online(endpoint, dotId) {
    try {
        const response = await fetch(endpoint, { method: 'GET' });
        const dot = document.getElementById(dotId);

        if (!dot) return;

        // Remove all possible status classes first
        dot.classList.remove('success-dot', 'error-dot', 'warning-dot', 'unknown-dot');

        if (response.status === 200) {
            dot.classList.add('success-dot'); // Online
        } else if (response.status === 503) {
            dot.classList.add('error-dot');   // Offline
        } else if (response.status === 400 || response.status === 403) {
            dot.classList.add('unknown-dot'); // Unknown
        } else {
            dot.classList.add('warning-dot'); // Bad request
            const body = await response.text();

            dot.classList.add('tooltip');
            tooltiptext = document.createElement('span');
            tooltiptext.className = 'tooltiptext';
            dot.appendChild(tooltiptext);
            tooltiptext.innerHTML = body;
        }
        dot.classList.remove('loading-dot');
    } catch (error) {
        const dot = document.getElementById(dotId);
        if (dot) {
            dot.classList.remove('success-dot', 'error-dot', 'warning-dot', 'unknown-dot');
            dot.classList.add('unknown-dot'); // Network error
        }
    }
}

// Example usage:
// <div id="status-dot" class="indicator-dot unknown-dot">&nbsp;</div>
// checkServerStatus('/api/status', 'status-dot');