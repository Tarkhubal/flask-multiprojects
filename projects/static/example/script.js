// Simple interactive demo
document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('demo-button');
    const output = document.getElementById('demo-output');
    let clickCount = 0;

    button.addEventListener('click', function() {
        clickCount++;
        const messages = [
            '🎉 Great! The JavaScript is working!',
            '✨ You clicked the button again!',
            '🚀 Static sites are awesome!',
            '💡 You can add any JavaScript functionality here!',
            '🎨 Customize this however you like!'
        ];
        
        const messageIndex = (clickCount - 1) % messages.length;
        output.textContent = messages[messageIndex] + ' (Click #' + clickCount + ')';
        output.style.opacity = '0';
        
        setTimeout(() => {
            output.style.transition = 'opacity 0.5s ease';
            output.style.opacity = '1';
        }, 10);
    });

    // Add a welcome animation
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * (index + 1));
    });
});
