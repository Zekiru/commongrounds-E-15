const button = document.getElementById('darkmode-btn')

function isDark() {
    return document.documentElement.getAttribute(
        'data-theme'
    ) === 'dark';
}

function toggleTheme() {
    const newTheme = isDark() ? 'light' : 'dark';
    const otherTheme = isDark() ? 'dark' : 'light';
    document.documentElement.setAttribute(
        'data-theme', newTheme
    );
    localStorage.setItem('theme', newTheme);
    setButtonText(otherTheme);
}

function setButtonText(text) {
    document.getElementById('darkmode-btn').innerHTML = (
        text[0].toUpperCase() + text.slice(1) + ' Mode'
    );
}

window.onload = function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        setButtonText(isDark() ? 'light' : 'dark');
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
        setButtonText('dark');
    }
};
