/**
 * Notifications JavaScript
 * US-09: Mark read/unread via AJAX without page refresh
 */

function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

// Mark single notification as read (AJAX — no page refresh)
function markRead(notifId) {
    fetch('/notifications/mark-read/' + notifId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            var item = document.getElementById('notif-' + notifId);
            item.classList.remove('notif-unread');
            var btn = item.querySelector('.btn-mark-read');
            if (btn) btn.remove();
            updateBadge();
        }
    });
}

// Mark all as read (AJAX — no page refresh)
function markAllRead() {
    fetch('/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            document.querySelectorAll('.notif-unread').forEach(function(item) {
                item.classList.remove('notif-unread');
            });
            document.querySelectorAll('.btn-mark-read').forEach(function(btn) {
                btn.remove();
            });
            updateBadge();
        }
    });
}

// Update badge count
function updateBadge() {
    fetch('/notifications/unread-count/')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var badge = document.querySelector('.badge');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                } else {
                    badge.remove();
                }
            }
        });
}
