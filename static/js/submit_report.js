/**
 * Submit Report Page JavaScript
 * US-06: Dynamic location loading, duplicate detection, preview modal
 */

document.addEventListener('DOMContentLoaded', function() {

    const facultySelect = document.getElementById('faculty-select');
    const buildingSelect = document.getElementById('building-select');
    const locationSelect = document.getElementById('location-select');
    const floorRoomRow = document.getElementById('floor-room-row');
    const locationIdInput = document.getElementById('location-id');
    const categorySelect = document.getElementById('category-select');
    const descInput = document.getElementById('description-input');
    const charCount = document.getElementById('char-count');
    const imagesInput = document.getElementById('images-input');
    const imagePreview = document.getElementById('image-preview');
    const videoInput = document.getElementById('video-input');
    const previewBtn = document.getElementById('preview-btn');
    const previewModal = document.getElementById('preview-modal');
    const previewBody = document.getElementById('preview-body');
    const modalClose = document.getElementById('modal-close');
    const modalCancel = document.getElementById('modal-cancel');
    const modalSubmit = document.getElementById('modal-submit');
    const reportForm = document.getElementById('report-form');

    // === 1. Dynamic Location Loading (AJAX) ===

    // Faculty → Load Buildings
    if (facultySelect) {
        facultySelect.addEventListener('change', function() {
            const facultyId = this.value;
            buildingSelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
            buildingSelect.disabled = true;
            floorRoomRow.style.display = 'none';
            locationIdInput.value = '';

            if (!facultyId) {
                buildingSelect.innerHTML = '<option value="">ابتدا دانشکده را انتخاب کنید</option>';
                return;
            }

            fetch('/reports/ajax/buildings/?faculty_id=' + facultyId)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    buildingSelect.innerHTML = '<option value="">ساختمان را انتخاب کنید</option>';
                    data.buildings.forEach(function(b) {
                        buildingSelect.innerHTML += '<option value="' + b.id + '">' + b.name + '</option>';
                    });
                    buildingSelect.disabled = false;
                })
                .catch(function() {
                    buildingSelect.innerHTML = '<option value="">خطا در بارگذاری</option>';
                });
        });
    }

    // Building → Load Locations (floors/rooms)
    if (buildingSelect) {
        buildingSelect.addEventListener('change', function() {
            const buildingId = this.value;
            locationIdInput.value = '';

            if (!buildingId) {
                floorRoomRow.style.display = 'none';
                return;
            }

            fetch('/reports/ajax/locations/?building_id=' + buildingId)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.locations.length > 0) {
                        locationSelect.innerHTML = '<option value="">طبقه و اتاق را انتخاب کنید</option>';
                        data.locations.forEach(function(loc) {
                            var label = '';
                            if (loc.floor) label += 'طبقه ' + loc.floor;
                            if (loc.room) label += ' - اتاق ' + loc.room;
                            if (!label) label = 'بدون مشخصات';
                            locationSelect.innerHTML += '<option value="' + loc.id + '">' + label + '</option>';
                        });
                        floorRoomRow.style.display = 'grid';
                    } else {
                        floorRoomRow.style.display = 'none';
                        // Use building as location directly
                        locationIdInput.value = buildingId;
                    }
                });
        });
    }

    // Location selected → set hidden input + check duplicate
    if (locationSelect) {
        locationSelect.addEventListener('change', function() {
            locationIdInput.value = this.value;
            checkDuplicate();
        });
    }

    // === 2. Category change → check duplicate ===
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            checkDuplicate();
        });
    }

    function checkDuplicate() {
        var locId = locationIdInput.value;
        var catId = categorySelect ? categorySelect.value : '';
        var warningDiv = document.getElementById('duplicate-warning');
        var dupList = document.getElementById('duplicate-list');

        if (!locId || !catId) {
            warningDiv.style.display = 'none';
            return;
        }

        fetch('/reports/ajax/check-duplicate/?location_id=' + locId + '&category_id=' + catId)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.duplicates.length > 0) {
                    dupList.innerHTML = '';
                    data.duplicates.forEach(function(d) {
                        dupList.innerHTML += '<li><a href="javascript:void(0)" onclick="showReportPreview(' + d.id + ')" style="color:#1F4E79;font-weight:600;">گزارش #' + d.id + ' — ' + d.title + '</a> <span style="color:#999;">(' + d.created_at + ' | وضعیت: ' + d.status + ')</span></li>';                    });
                    warningDiv.style.display = 'block';
                } else {
                    warningDiv.style.display = 'none';
                }
            });
    }

    // === 3. Character Counter ===
    if (descInput && charCount) {
        descInput.addEventListener('input', function() {
            var len = this.value.length;
            charCount.textContent = len;
            var counter = charCount.parentElement;
            if (len >= 20) {
                counter.className = 'char-counter valid';
            } else {
                counter.className = 'char-counter invalid';
            }
        });
    }

    // === 4. Image Preview ===
    if (imagesInput) {
        imagesInput.addEventListener('change', function() {
            imagePreview.innerHTML = '';
            var files = Array.from(this.files).slice(0, 3);

            if (this.files.length > 3) {
                alert('حداکثر ۳ تصویر مجاز است. فقط ۳ تصویر اول انتخاب شد.');
            }

            files.forEach(function(file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var img = document.createElement('img');
                    img.src = e.target.result;
                    imagePreview.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
    }

    // === 5. Video Size Check ===
    if (videoInput) {
        videoInput.addEventListener('change', function() {
            if (this.files[0] && this.files[0].size > 10 * 1024 * 1024) {
                alert('حجم ویدیو نباید بیشتر از ۱۰ مگابایت باشد.');
                this.value = '';
            }
        });
    }

    // === 6. Preview Modal ===
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            var title = document.querySelector('[name="title"]').value || '—';
            var desc = descInput ? descInput.value : '—';
            var faculty = facultySelect ? facultySelect.options[facultySelect.selectedIndex].text : '—';
            var building = buildingSelect ? buildingSelect.options[buildingSelect.selectedIndex].text : '—';
            var location = locationSelect && locationSelect.value ? locationSelect.options[locationSelect.selectedIndex].text : '';
            var category = categorySelect ? categorySelect.options[categorySelect.selectedIndex].text : '—';
            var priority = document.getElementById('priority-select');
            var priorityText = priority ? priority.options[priority.selectedIndex].text : '—';
            var priorityVal = priority ? priority.value : 'normal';

            var locationText = faculty;
            if (building && building !== '—') locationText += ' — ' + building;
            if (location) locationText += ' — ' + location;

            var priorityColor = '#6C757D';
            if (priorityVal === 'important') priorityColor = '#FF9800';
            if (priorityVal === 'urgent') priorityColor = '#DC3545';

            var imageCount = imagesInput && imagesInput.files ? Math.min(imagesInput.files.length, 3) : 0;
            var hasVideo = videoInput && videoInput.files && videoInput.files.length > 0;

            previewBody.innerHTML =
                '<div style="text-align:center;padding-bottom:16px;border-bottom:2px solid #E8F0FE;margin-bottom:16px;">' +
                '<div style="font-size:42px;margin-bottom:8px;">📝</div>' +
                '<h2 style="color:#1F4E79;margin:0 0 8px 0;font-size:20px;">پیش‌نمایش گزارش</h2>' +
                '<span style="background:' + priorityColor + ';color:white;padding:4px 16px;border-radius:20px;font-size:13px;font-weight:600;">' + priorityText + '</span>' +
                '</div>' +
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">' +
                '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">عنوان خرابی</div><div style="font-size:14px;font-weight:600;color:#333;">' + title + '</div></div>' +
                '<div style="background:#F8F9FA;padding:12px;border-radius:10px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">دسته‌بندی</div><div style="font-size:14px;font-weight:600;color:#333;">' + category + '</div></div>' +
                '</div>' +
                '<div style="background:#F0F4FF;padding:12px;border-radius:10px;margin-bottom:12px;"><div style="font-size:11px;color:#999;margin-bottom:4px;">📍 مکان</div><div style="font-size:14px;color:#333;">' + locationText + '</div></div>' +
                '<div style="background:#FFFDE7;padding:14px;border-radius:10px;border:1px solid #FFF9C4;margin-bottom:12px;"><div style="font-size:11px;color:#999;margin-bottom:6px;">📝 توضیحات</div><div style="font-size:14px;color:#333;line-height:1.8;">' + desc + '</div></div>' +
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">' +
                '<div style="background:#F8F9FA;padding:12px;border-radius:10px;text-align:center;"><div style="font-size:24px;margin-bottom:4px;">📷</div><div style="font-size:13px;color:#333;">' + (imageCount > 0 ? imageCount + ' تصویر' : 'بدون تصویر') + '</div></div>' +
                '<div style="background:#F8F9FA;padding:12px;border-radius:10px;text-align:center;"><div style="font-size:24px;margin-bottom:4px;">🎥</div><div style="font-size:13px;color:#333;">' + (hasVideo ? 'ویدیو پیوست' : 'بدون ویدیو') + '</div></div>' +
                '</div>';

            previewModal.style.display = 'flex';
        });
    }

    // Close modal
    if (modalClose) modalClose.addEventListener('click', function() { previewModal.style.display = 'none'; });
    if (modalCancel) modalCancel.addEventListener('click', function() { previewModal.style.display = 'none'; });
    if (modalSubmit) modalSubmit.addEventListener('click', function() { previewModal.style.display = 'none'; reportForm.submit(); });

    // Close modal on overlay click
    if (previewModal) {
        previewModal.addEventListener('click', function(e) {
            if (e.target === previewModal) previewModal.style.display = 'none';
        });
    }
    // === 7. Auto-suggest priority based on description ===
    var prioritySelect = document.getElementById('priority-select');
    var hintEl = document.getElementById('priority-hint');

    var urgentKeywords = ['آتش', 'حریق', 'سیل', 'برق‌گرفتگی', 'انفجار', 'گاز', 'نشت گاز', 'خطرناک', 'فوری', 'اورژانس', 'سقف ریزش', 'ریزش', 'شکستگی لوله اصلی'];
    var importantKeywords = ['نشتی', 'خرابی کامل', 'از کار افتاده', 'کار نمیکنه', 'کار نمی‌کنه', 'قطع برق', 'قطع آب', 'سرما', 'گرما', 'یخ زده', 'بوی بد', 'شکسته', 'خراب شده', 'کولر خراب', 'شوفاژ خراب', 'پروژکتور خراب'];

    if (descInput) {
        descInput.addEventListener('input', function() {
            var text = this.value.toLowerCase();
            var suggested = 'normal';
            var reason = '';

            for (var i = 0; i < urgentKeywords.length; i++) {
                if (text.indexOf(urgentKeywords[i]) !== -1) {
                    suggested = 'urgent';
                    reason = 'کلمه «' + urgentKeywords[i] + '» شناسایی شد';
                    break;
                }
            }

            if (suggested === 'normal') {
                for (var j = 0; j < importantKeywords.length; j++) {
                    if (text.indexOf(importantKeywords[j]) !== -1) {
                        suggested = 'important';
                        reason = 'کلمه «' + importantKeywords[j] + '» شناسایی شد';
                        break;
                    }
                }
            }

            if (prioritySelect && hintEl) {
                if (suggested === 'urgent') {
                    prioritySelect.value = 'urgent';
                    hintEl.innerHTML = '🔴 پیشنهاد سیستم: <strong>اضطراری</strong> — ' + reason;
                    hintEl.style.color = '#DC3545';
                } else if (suggested === 'important') {
                    prioritySelect.value = 'important';
                    hintEl.innerHTML = '🟡 پیشنهاد سیستم: <strong>مهم</strong> — ' + reason;
                    hintEl.style.color = '#FF9800';
                } else {
                    hintEl.innerHTML = 'سیستم سطح فوریت را پیشنهاد می‌دهد';
                    hintEl.style.color = 'var(--secondary)';
                }
            }
        });
    }
    window.showReportPreview = function(reportId) {
        var modal = document.getElementById('dup-modal');
        var body = document.getElementById('dup-modal-body');
        body.innerHTML = '<p style="text-align:center;padding:40px;color:#999;">⏳ در حال بارگذاری...</p>';
        modal.style.display = 'flex';

        fetch('/reports/ajax/report-preview/?report_id=' + reportId)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.error) {
                    body.innerHTML = '<p style="color:red;text-align:center;padding:20px;">گزارش یافت نشد</p>';
                    return;
                }

                var statusColor = '#17A2B8';
                if (data.status.indexOf('تعمیر') > -1) statusColor = '#2E75B6';
                if (data.status.indexOf('حل') > -1 || data.status.indexOf('بسته') > -1) statusColor = '#28A745';
                if (data.status.indexOf('انتظار') > -1) statusColor = '#FF9800';
                if (data.status.indexOf('معلق') > -1) statusColor = '#E65100';

                body.innerHTML =
                    '<div style="text-align:center;padding-bottom:16px;border-bottom:2px solid #E8F0FE;margin-bottom:16px;">' +
                    '<div style="font-size:42px;margin-bottom:8px;">📋</div>' +
                    '<h2 style="color:#1F4E79;margin:0 0 8px 0;font-size:20px;">گزارش #' + data.id + '</h2>' +
                    '<span style="background:' + statusColor + ';color:white;padding:4px 16px;border-radius:20px;font-size:13px;font-weight:600;">' + data.status + '</span>' +
                    '</div>' +
                    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">' +
                    '<div style="background:#F8F9FA;padding:12px;border-radius:10px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">عنوان</div>' +
                    '<div style="font-size:14px;font-weight:600;color:#333;">' + data.title + '</div>' +
                    '</div>' +
                    '<div style="background:#F8F9FA;padding:12px;border-radius:10px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">دسته‌بندی</div>' +
                    '<div style="font-size:14px;font-weight:600;color:#333;">' + data.category + '</div>' +
                    '</div>' +
                    '<div style="background:#F8F9FA;padding:12px;border-radius:10px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">اولویت</div>' +
                    '<div style="font-size:14px;font-weight:600;color:#333;">' + data.priority + '</div>' +
                    '</div>' +
                    '<div style="background:#F8F9FA;padding:12px;border-radius:10px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">تاریخ ثبت</div>' +
                    '<div style="font-size:14px;font-weight:600;color:#333;">' + data.created_at + '</div>' +
                    '</div>' +
                    '</div>' +
                    '<div style="background:#F0F4FF;padding:12px;border-radius:10px;margin-bottom:12px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">📍 مکان</div>' +
                    '<div style="font-size:14px;color:#333;">' + data.location + '</div>' +
                    '</div>' +
                    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px;">' +
                    '<div style="background:#F8F9FA;padding:12px;border-radius:10px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">👤 گزارش‌دهنده</div>' +
                    '<div style="font-size:14px;color:#333;">' + data.reporter + '</div>' +
                    '</div>' +
                    '<div style="background:#F8F9FA;padding:12px;border-radius:10px;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:4px;">🔧 تکنسین</div>' +
                    '<div style="font-size:14px;color:#333;">' + data.technician + '</div>' +
                    '</div>' +
                    '</div>' +
                    '<div style="background:#FFFDE7;padding:14px;border-radius:10px;border:1px solid #FFF9C4;">' +
                    '<div style="font-size:11px;color:#999;margin-bottom:6px;">📝 توضیحات</div>' +
                    '<div style="font-size:14px;color:#333;line-height:1.8;">' + data.description + '</div>' +
                    '</div>';
            });

        modal.onclick = function(e) {
            if (e.target === modal) modal.style.display = 'none';
        };
    };
});
