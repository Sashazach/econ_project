document.addEventListener('DOMContentLoaded', () => {
    const winnerName = document.getElementById('winnerName');
    winnerName.textContent = "John Doe"; // Example name

    // Festive color palette
    const colors = [
        '#FF6B6B', // coral
        '#4ECDC4', // turquoise
        '#FFD93D', // yellow
        '#FF8C42', // orange
        '#6C5CE7', // purple
        '#A8E6CF', // mint
        '#FDFFAB', // light yellow
        '#FF99C8'  // pink
    ];

    // Initial confetti burst
    confetti({
        particleCount: 150,
        spread: 100,
        colors: colors,
        origin: { y: 0.6 }
    });

    // Continuous confetti
    const duration = 15 * 1000;
    const animationEnd = Date.now() + duration;

    function randomInRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    (function frame() {
        const timeLeft = animationEnd - Date.now();

        if (timeLeft <= 0) return;

        confetti({
            particleCount: 3,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: colors
        });
        confetti({
            particleCount: 3,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: colors
        });

        requestAnimationFrame(frame);
    }());
});
