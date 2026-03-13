document.addEventListener('DOMContentLoaded', function(){
    // Render appointments chart if canvas exists
    const aptCtx = document.getElementById('appointmentsChart');
    if(aptCtx){
        const labels = JSON.parse(aptCtx.dataset.labels || '[]');
        const values = JSON.parse(aptCtx.dataset.values || '[]');
        new Chart(aptCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Appointments',
                    data: values,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13,110,253,0.08)',
                    tension: 0.3,
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // Small animate-in for stat-cards
    document.querySelectorAll('.stat-card').forEach((el, idx)=>{
        el.style.animation = `fadeUp .45s ease ${(idx*0.08).toFixed(2)}s both`;
    });
});

/* Keyframes injected for small fadeUp effect */
const style = document.createElement('style');
style.innerHTML = `@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }`;
document.head.appendChild(style);
