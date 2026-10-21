/**
 * dynamic_fields.js
 * Manages dynamic addition and removal of Experience and Education fields in profile_form.
 */

function addExperienceRow(data = {}) {
    const container = document.getElementById('experience-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'entry-row';
    div.innerHTML = `
        <div class="grid-3">
            <div class="form-group">
                <label>Company *</label>
                <input type="text" name="company[]" value="${escapeHtml(data.company || '')}" placeholder="Tech Solutions Ltd" required>
            </div>
            <div class="form-group">
                <label>Role / Position *</label>
                <input type="text" name="role[]" value="${escapeHtml(data.role || '')}" placeholder="Backend Intern" required>
            </div>
            <div class="form-group">
                <label>Duration</label>
                <input type="text" name="experience_duration[]" value="${escapeHtml(data.duration || '')}" placeholder="Jun 2024 - Aug 2024">
            </div>
        </div>
        <div class="form-group">
            <label>Bullet Points / Description (One bullet per line)</label>
            <textarea name="description[]" rows="3" placeholder="• Developed REST APIs with Flask and PostgreSQL&#10;• Reduced latency by 25% with query optimization">${escapeHtml(data.description || '')}</textarea>
        </div>
        <button type="button" class="btn-remove" onclick="removeEntry(this)">✕ Remove Experience</button>
    `;
    container.appendChild(div);
}

function addEducationRow(data = {}) {
    const container = document.getElementById('education-container');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'entry-row';
    div.innerHTML = `
        <div class="grid-2">
            <div class="form-group">
                <label>Institution *</label>
                <input type="text" name="institution[]" value="${escapeHtml(data.institution || '')}" placeholder="Pune University" required>
            </div>
            <div class="form-group">
                <label>Degree / Major *</label>
                <input type="text" name="degree[]" value="${escapeHtml(data.degree || '')}" placeholder="B.E. Computer Engineering" required>
            </div>
            <div class="form-group">
                <label>Duration / Dates</label>
                <input type="text" name="education_duration[]" value="${escapeHtml(data.duration || '')}" placeholder="2020 - 2024">
            </div>
            <div class="form-group">
                <label>GPA / Score</label>
                <input type="text" name="score[]" value="${escapeHtml(data.score || '')}" placeholder="8.6 CGPA / 85%">
            </div>
        </div>
        <button type="button" class="btn-remove" onclick="removeEntry(this)">✕ Remove Education</button>
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
    const expContainer = document.getElementById('experience-container');
    const eduContainer = document.getElementById('education-container');
    
    // Only auto-add if empty and marked as new profile
    const isNewProfile = document.body.dataset.isNew === 'true';
    if (isNewProfile) {
        if (expContainer && expContainer.children.length === 0) {
            addExperienceRow();
        }
        if (eduContainer && eduContainer.children.length === 0) {
            addEducationRow();
        }
    }
});
