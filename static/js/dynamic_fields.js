/**
 * dynamic_fields.js
 * Manages dynamic addition and removal of Experience and Education fields in profile_form.
 * Styled with Stitch Academic Career Nexus design tokens.
 */

function addExperienceRow(data = {}) {
    const container = document.getElementById('experience-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'entry-row p-4 rounded-xl bg-surface-container-low/60 border border-outline-variant/60 relative flex flex-col gap-3 transition-all';
    div.innerHTML = `
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">Company / Organization *</label>
                <input type="text" name="company[]" value="${escapeHtml(data.company || '')}" placeholder="Tech Solutions Ltd" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all" required>
            </div>
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">Role / Position *</label>
                <input type="text" name="role[]" value="${escapeHtml(data.role || '')}" placeholder="Backend Engineering Intern" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all" required>
            </div>
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">Duration / Dates</label>
                <input type="text" name="experience_duration[]" value="${escapeHtml(data.duration || '')}" placeholder="Jun 2024 - Aug 2024" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all">
            </div>
        </div>
        <div class="flex flex-col gap-1">
            <label class="text-xs font-bold text-on-surface flex items-center justify-between">
                <span>Bullet Points / Achievements</span>
                <span class="text-[11px] font-normal text-on-surface-variant">One bullet per line</span>
            </label>
            <textarea name="description[]" rows="3" placeholder="• Engineered REST APIs using Flask & PostgreSQL, decreasing response latency by 20%&#10;• Collaborated with team on automated CI/CD pipeline deployments" class="w-full p-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all">${escapeHtml(data.description || '')}</textarea>
        </div>
        <div class="flex justify-end">
            <button type="button" class="btn-remove inline-flex items-center gap-1 text-xs font-bold text-rose-600 hover:text-rose-800 transition-colors" onclick="removeEntry(this)">
                <span class="material-symbols-outlined text-[15px]">delete</span>
                <span>Remove Experience</span>
            </button>
        </div>
    `;
    container.appendChild(div);
}

function addEducationRow(data = {}) {
    const container = document.getElementById('education-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'entry-row p-4 rounded-xl bg-surface-container-low/60 border border-outline-variant/60 relative flex flex-col gap-3 transition-all';
    div.innerHTML = `
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">Institution / College *</label>
                <input type="text" name="institution[]" value="${escapeHtml(data.institution || '')}" placeholder="State University" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all" required>
            </div>
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">Degree / Major *</label>
                <input type="text" name="degree[]" value="${escapeHtml(data.degree || '')}" placeholder="B.S. in Computer Science" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all" required>
            </div>
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">Graduation Year / Dates</label>
                <input type="text" name="education_duration[]" value="${escapeHtml(data.duration || '')}" placeholder="2021 - 2025" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all">
            </div>
            <div class="flex flex-col gap-1">
                <label class="text-xs font-bold text-on-surface">GPA / Score</label>
                <input type="text" name="score[]" value="${escapeHtml(data.score || '')}" placeholder="3.85 GPA / 86%" class="w-full h-10 px-3 bg-white rounded-lg border border-outline-variant/70 text-xs sm:text-sm text-on-surface focus:border-primary-container focus:ring-2 focus:ring-primary-container/20 outline-none transition-all">
            </div>
        </div>
        <div class="flex justify-end">
            <button type="button" class="btn-remove inline-flex items-center gap-1 text-xs font-bold text-rose-600 hover:text-rose-800 transition-colors" onclick="removeEntry(this)">
                <span class="material-symbols-outlined text-[15px]">delete</span>
                <span>Remove Education</span>
            </button>
        </div>
    `;
    container.appendChild(div);
}

function removeEntry(button) {
    const row = button.closest('.entry-row');
    if (row) {
        row.remove();
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// On page load, if containers are empty on a new profile form, add one default row
document.addEventListener('DOMContentLoaded', () => {
    const formContainer = document.querySelector('[data-is-new]');
    if (formContainer && formContainer.dataset.isNew === 'true') {
        const expContainer = document.getElementById('experience-container');
        const eduContainer = document.getElementById('education-container');
        if (expContainer && expContainer.children.length === 0) {
            addExperienceRow();
        }
        if (eduContainer && eduContainer.children.length === 0) {
            addEducationRow();
        }
    }
});
