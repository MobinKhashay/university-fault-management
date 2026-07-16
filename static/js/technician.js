/**
 * Technician Panel JavaScript
 * US-11: Status toggle, task tabs
 */

// Tab switching
function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(function(el) { el.classList.remove('active'); });
    document.querySelectorAll('.tab-btn').forEach(function(el) { el.classList.remove('active'); });
    document.getElementById('tab-' + tab).classList.add('active');
    event.target.classList.add('active');
}

// Status toggle (AJAX)
function changeStatus(status) {
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
        csrfToken = csrfToken ? csrfToken[1] : '';
    } else {
        csrfToken = csrfToken.value;
    }

    fetch('/technicians/toggle-status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
        },
        body: 'status=' + status,
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            // Update button styles
            document.querySelectorAll('.status-btn').forEach(function(btn) {
                btn.classList.remove('active-green', 'active-orange', 'active-gray');
            });
            var activeBtn = document.querySelector('[data-status="' + status + '"]');
            if (status === 'available') activeBtn.classList.add('active-green');
            else if (status === 'busy') activeBtn.classList.add('active-orange');
            else activeBtn.classList.add('active-gray');
        }
    });
}
