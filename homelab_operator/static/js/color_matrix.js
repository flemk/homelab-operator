function percentToColor(percent) {
    percent = Math.max(0, Math.min(1, percent));
    // Gradient from grey (#cccccc) to dark green (#006400)
    const rStart = 204, gStart = 204, bStart = 204; // grey
    const rEnd = 0,   gEnd = 100,  bEnd = 0;   // dark green
    const r = Math.round(rStart + (rEnd - rStart) * percent);
    const g = Math.round(gStart + (gEnd - gStart) * percent);
    const b = Math.round(bStart + (bEnd - bStart) * percent);
    return `rgb(${r}, ${g}, ${b})`;
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.uptime-cell').forEach(function(cell) {
        const percent = parseFloat(cell.dataset.percent);
        cell.style.backgroundColor = percentToColor(percent);
    });
});
