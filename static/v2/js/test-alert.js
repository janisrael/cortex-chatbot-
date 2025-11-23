// Test alert function
function testShowAlert() {
    console.log('Testing alert display...');
    const alertElement = document.getElementById('llmSuccess');
    console.log('Alert element:', alertElement);
    if (alertElement) {
        console.log('Alert classes:', alertElement.className);
        console.log('Alert display before:', window.getComputedStyle(alertElement).display);
        alertElement.textContent = 'TEST MESSAGE - If you see this, alerts work!';
        alertElement.style.display = 'block';
        console.log('Alert display after:', window.getComputedStyle(alertElement).display);
    } else {
        console.error('Alert element not found!');
    }
}

// Run test after page loads
setTimeout(testShowAlert, 2000);
