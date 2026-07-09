/**
 * Registration Page JavaScript
 * US-01: Dynamic form based on role, real-time password strength check
 */

document.addEventListener('DOMContentLoaded', function() {

    const roleSelect = document.getElementById('role-select');
    const idLabel = document.getElementById('id-label');
    const idInput = document.getElementById('student-id');
    const idCardLabel = document.getElementById('id-card-label');
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('password-confirm');
    const strengthBar = document.getElementById('strength-bar');
    const passwordHint = document.getElementById('password-hint');
    const matchHint = document.getElementById('match-hint');

    // === 1. Dynamic form change based on role ===
    const roleLabels = {
        'student': {
            idLabel: 'شماره دانشجویی',
            idPlaceholder: 'شماره دانشجویی خود را وارد کنید',
            cardLabel: 'تصویر کارت دانشجویی',
        },
        'professor': {
            idLabel: 'شماره استادی',
            idPlaceholder: 'شماره استادی خود را وارد کنید',
            cardLabel: 'تصویر کارت استادی',
        },
        'staff': {
            idLabel: 'شماره کارمندی',
            idPlaceholder: 'شماره کارمندی خود را وارد کنید',
            cardLabel: 'تصویر کارت کارمندی',
        }
    };

    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const role = this.value;
            if (roleLabels[role]) {
                idLabel.innerHTML = roleLabels[role].idLabel + ' <span class="required">*</span>';
                idInput.placeholder = roleLabels[role].idPlaceholder;
                idCardLabel.innerHTML = roleLabels[role].cardLabel + ' <span class="required">*</span>';
            }
        });
    }

    // === 2. Real-time password strength checker ===
    function checkPasswordStrength(password) {
        let score = 0;
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^a-zA-Z0-9]/.test(password)) score++;
        return score;
    }

    const strengthMessages = {
        0: { class: '', hint: 'حداقل ۸ کاراکتر', color: '' },
        1: { class: 'strength-weak', hint: 'خیلی ضعیف', color: '#DC3545' },
        2: { class: 'strength-fair', hint: 'ضعیف', color: '#FF9800' },
        3: { class: 'strength-good', hint: 'متوسط', color: '#FFC107' },
        4: { class: 'strength-strong', hint: 'قوی', color: '#28A745' },
        5: { class: 'strength-strong', hint: 'خیلی قوی', color: '#28A745' },
    };

    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            const info = strengthMessages[strength];

            // Update strength bar
            strengthBar.className = 'strength-bar ' + info.class;

            // Update hint
            passwordHint.textContent = info.hint;
            passwordHint.style.color = info.color;

            // Also check match if confirm has value
            if (confirmInput.value) {
                checkMatch();
            }
        });
    }

    // === 3. Password match checker ===
    function checkMatch() {
        if (!confirmInput.value) {
            matchHint.textContent = '';
            return;
        }
        if (passwordInput.value === confirmInput.value) {
            matchHint.textContent = '✓ رمز عبور مطابقت دارد';
            matchHint.style.color = '#28A745';
            confirmInput.style.borderColor = '#28A745';
        } else {
            matchHint.textContent = '✗ رمز عبور مطابقت ندارد';
            matchHint.style.color = '#DC3545';
            confirmInput.style.borderColor = '#DC3545';
        }
    }

    if (confirmInput) {
        confirmInput.addEventListener('input', checkMatch);
    }

    // === 4. Form validation before submit ===
    const form = document.getElementById('register-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            let valid = true;

            // Check required fields
            const required = form.querySelectorAll('[required], .form-input');
            required.forEach(function(input) {
                if (!input.value && input.type !== 'file') {
                    input.classList.add('error');
                    valid = false;
                } else {
                    input.classList.remove('error');
                }
            });

            // Check password match
            if (passwordInput.value !== confirmInput.value) {
                valid = false;
                matchHint.textContent = '✗ رمز عبور مطابقت ندارد';
                matchHint.style.color = '#DC3545';
            }

            // Check password strength
            if (passwordInput.value.length < 8) {
                valid = false;
                passwordHint.textContent = 'رمز عبور باید حداقل ۸ کاراکتر باشد';
                passwordHint.style.color = '#DC3545';
            }

            if (!valid) {
                e.preventDefault();
            }
        });
    }
});
