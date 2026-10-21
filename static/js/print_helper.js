/**
 * print_helper.js
 * Handles browser print triggering, auto-print for PDF exports, and preview controls.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Check for Auto-Print trigger (Phase 4 export flow)
    const isAutoPrint = document.body.dataset.autoPrint === 'true' || 
                        new URLSearchParams(window.location.search).get('auto_print') === 'true';

    if (isAutoPrint) {
        // Allow brief delay for CSS fonts and styles to render before opening print dialog
        setTimeout(() => {
            window.print();
        }, 400);
    }

    // 2. Attach click handlers to any print buttons
    const printButtons = document.querySelectorAll('.btn-print, [data-action="print"]');
    printButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            window.print();
        });
    });

    // 3. Theme switcher handling inside preview toolbar
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
        themeSelect.addEventListener('change', (e) => {
            const selectedTheme = e.target.value;
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('theme', selectedTheme);
            window.location.href = currentUrl.toString();
        });
    }
});

// Provide a global print function fallback
function triggerPrint() {
    window.print();
}

