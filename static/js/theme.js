class ThemeManager {
    constructor() {
        this.themeKey = 'theme-preference';
        this.toggle = document.getElementById('theme-toggle');
        this.icon = this.toggle?.querySelector('.theme-icon');
        this.init();
    }

    init() {
        const savedTheme = this.getSavedTheme();
        this.applyTheme(savedTheme);
        this.setupToggle();
    }

    getSavedTheme() {
        return localStorage.getItem(this.themeKey) || 'dark';
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (this.icon) {
            this.icon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
        localStorage.setItem(this.themeKey, theme);
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }

    setupToggle() {
        if (this.toggle) {
            this.toggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});
