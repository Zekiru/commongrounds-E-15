const button = document.getElementById('darkmode-btn');

function isDark() {
    return document.documentElement.getAttribute('data-theme') === 'dark';
}

function updateButtonUI() {
    if (!button) return;
    // We show the name of the mode you will switch TO
    const nextTheme = isDark() ? 'light' : 'dark';
    button.innerHTML = 'Toggle ' + nextTheme.charAt(0).toUpperCase() + nextTheme.slice(1) + ' Mode';
}

function toggleTheme() {
    const newTheme = isDark() ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateButtonUI();
}

updateButtonUI();

button.addEventListener('click', toggleTheme);