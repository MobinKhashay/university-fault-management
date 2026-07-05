document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.alert').forEach(function(el) {
        setTimeout(function() { el.style.opacity='0'; setTimeout(function(){el.remove()},300); }, 5000);
    });
});
