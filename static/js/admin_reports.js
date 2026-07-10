/**
 * Admin Report Management JavaScript
 * US-17: Action menus, modals, AJAX detail loading
 */

// Toggle action dropdown menu
function toggleMenu(btn) {
    var allDropdowns = document.querySelectorAll('.action-dropdown');
    allDropdowns.forEach(function(d) { d.classList.remove('show'); });

    var dropdown = btn.nextElementSibling;
    dropdown.classList.toggle('show');
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
    if (!e.target.classList.contains('btn-action')) {
        document.querySelectorAll('.action-dropdown').forEach(function(d) {
            d.classList.remove('show');
        });
    }
});

// Close any modal
function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(function(modal) {
    modal.addEventListener('click', function(e) {
        if (e.target === modal) modal.style.display = 'none';
    });
});

// Show report detail modal (AJAX)
function showDetail(reportId) {
    var modal = document.getElementById('detail-modal');
    var body = document.getElementById('detail-body');
    body.innerHTML = '<p style="text-align:center;">در حال بارگذاری...</p>';
    modal.style.display = 'flex';

    fetch('/panel/reports/' + reportId + '/detail/')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var html = '';
            html += '<div class="preview-item"><strong>شماره:</strong> #' + data.id + '</div>';
            html += '<div class="preview-item"><strong>عنوان:</strong> ' + data.title + '</div>';
            html += '<div class="preview-item"><strong>مکان:</strong> ' + data.location + '</div>';
            html += '<div class="preview-item"><strong>دسته‌بندی:</strong> ' + data.category + '</div>';
            html += '<div class="preview-item"><strong>اولویت:</strong> ' + data.priority + '</div>';
            html += '<div class="preview-item"><strong>وضعیت:</strong> ' + data.status + '</div>';
            html += '<div class="preview-item"><strong>گزارش‌دهنده:</strong> ' + data.reporter + '</div>';
            html += '<div class="preview-item"><strong>تکنسین:</strong> ' + data.technician + '</div>';
            html += '<div class="preview-item"><strong>تاریخ ثبت:</strong> ' + data.created_at + '</div>';
            html += '<div class="preview-item"><strong>مدت باز:</strong> ' + data.duration + '</div>';
            html += '<div class="preview-item"><strong>توضیحات:</strong><br>' + data.description + '</div>';

            if (data.logs.length > 0) {
                html += '<hr><h4>خط زمانی:</h4>';
                data.logs.forEach(function(log) {
                    html += '<div class="log-item"><span class="log-time">' + log.time + '</span> — ' + log.action;
                    if (log.desc) html += ': ' + log.desc;
                    html += '</div>';
                });
            }

            body.innerHTML = html;
        })
        .catch(function() {
            body.innerHTML = '<p style="color:red;">خطا در بارگذاری</p>';
        });
}

// Show change technician modal
function showChangeTech(reportId) {
    var modal = document.getElementById('tech-modal');
    var form = document.getElementById('change-tech-form');
    form.action = '/panel/reports/' + reportId + '/change-technician/';
    modal.style.display = 'flex';
}

// Show cancel report modal
function showCancelReport(reportId) {
    var modal = document.getElementById('cancel-modal');
    var form = document.getElementById('cancel-form');
    form.action = '/panel/reports/' + reportId + '/cancel/';
    modal.style.display = 'flex';
}

// Show change priority modal
function showChangePriority(reportId) {
    var modal = document.getElementById('priority-modal');
    var form = document.getElementById('priority-form');
    form.action = '/panel/reports/' + reportId + '/change-priority/';
    modal.style.display = 'flex';
}
