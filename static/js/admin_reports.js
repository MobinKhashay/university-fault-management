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
    body.innerHTML = '<p style="text-align:center;padding:40px;color:#999;">⏳ در حال بارگذاری...</p>';
    modal.style.display = 'flex';

    fetch('/panel/reports/' + reportId + '/detail/')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var statusColor = '#17A2B8';
            if (data.status.indexOf('تعمیر') > -1) statusColor = '#2E75B6';
            if (data.status.indexOf('حل') > -1 || data.status.indexOf('بسته') > -1) statusColor = '#28A745';
            if (data.status.indexOf('انتظار') > -1 || data.status.indexOf('صف') > -1) statusColor = '#FF9800';
            if (data.status.indexOf('معلق') > -1) statusColor = '#E65100';
            if (data.status.indexOf('لغو') > -1) statusColor = '#DC3545';

            var html = '';
            // Header
            html += '<div style="text-align:center;padding-bottom:16px;border-bottom:2px solid #E8F0FE;margin-bottom:16px;">';
            html += '<div style="font-size:42px;margin-bottom:8px;">📋</div>';
            html += '<h2 style="color:#1F4E79;margin:0 0 8px 0;font-size:20px;">گزارش #' + data.id + '</h2>';
            html += '<span style="background:' + statusColor + ';color:white;padding:4px 16px;border-radius:20px;font-size:13px;font-weight:600;">' + data.status + '</span>';
            html += '</div>';

            // Info Grid
            html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">';
            html += '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">عنوان</div><div style="font-size:14px;font-weight:600;color:#333;">' + data.title + '</div></div>';
            html += '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">دسته‌بندی</div><div style="font-size:14px;font-weight:600;color:#333;">' + data.category + '</div></div>';
            html += '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">اولویت</div><div style="font-size:14px;font-weight:600;color:#333;">' + data.priority + '</div></div>';
            html += '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">تاریخ ثبت</div><div style="font-size:14px;font-weight:600;color:#333;">' + data.created_at + '</div></div>';
            html += '</div>';

            // Location
            html += '<div style="background:#F0F4FF;padding:12px;border-radius:10px;margin-bottom:12px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">📍 مکان</div><div style="font-size:14px;color:#333;">' + data.location + '</div></div>';

            // People
            html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">';
            html += '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">👤 گزارش‌دهنده</div><div style="font-size:14px;color:#333;">' + data.reporter + '</div></div>';
            html += '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">🔧 تکنسین</div><div style="font-size:14px;color:#333;">' + data.technician + '</div></div>';
            html += '</div>';

            // Duration
            html += '<div style="background:#FFF8E1;padding:12px;border-radius:10px;margin-bottom:12px;border:1px solid #FFE082;"><div style="font-size:11px;color:#999;margin-bottom:4px;">⏱️ مدت باز</div><div style="font-size:14px;color:#333;">' + data.duration + '</div></div>';

            // Description
            html += '<div style="background:#FFFDE7;padding:14px;border-radius:10px;border:1px solid #FFF9C4;margin-bottom:16px;"><div style="font-size:11px;color:#999;margin-bottom:6px;">📝 توضیحات</div><div style="font-size:14px;color:#333;line-height:1.8;">' + data.description + '</div></div>';

            // Timeline
            if (data.logs && data.logs.length > 0) {
                html += '<div style="border-top:2px solid #E8F0FE;padding-top:16px;">';
                html += '<h4 style="color:#1F4E79;margin-bottom:12px;">📅 خط زمانی</h4>';
                data.logs.forEach(function(log) {
                    html += '<div style="display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #f5f5f5;">';
                    html += '<span style="font-size:12px;color:#999;white-space:nowrap;min-width:110px;">' + log.time + '</span>';
                    html += '<span style="font-size:13px;color:#333;"><strong>' + log.action + '</strong>';
                    if (log.desc) html += ': ' + log.desc;
                    html += '</span></div>';
                });
                html += '</div>';
            }

            body.innerHTML = html;
        })
        .catch(function() {
            body.innerHTML = '<p style="color:red;text-align:center;padding:20px;">خطا در بارگذاری</p>';
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
