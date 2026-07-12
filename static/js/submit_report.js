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
                        dupList.innerHTML += '<li>گزارش #' + d.id + ' — ' + d.title + ' (' + d.created_at + ')</li>';
                    });
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
            var title = document.querySelector('[name="title"]').value || '-';
            var desc = descInput ? descInput.value : '-';
            var faculty = facultySelect ? facultySelect.options[facultySelect.selectedIndex].text : '-';
            var building = buildingSelect ? buildingSelect.options[buildingSelect.selectedIndex].text : '-';
            var category = categorySelect ? categorySelect.options[categorySelect.selectedIndex].text : '-';
            var priority = document.getElementById('priority-select');
            var priorityText = priority ? priority.options[priority.selectedIndex].text : '-';

            previewBody.innerHTML =
                '<div class="preview-item"><div class="preview-label">عنوان:</div><div class="preview-value">' + title + '</div></div>' +
                '<div class="preview-item"><div class="preview-label">مکان:</div><div class="preview-value">' + faculty + ' — ' + building + '</div></div>' +
                '<div class="preview-item"><div class="preview-label">دسته‌بندی:</div><div class="preview-value">' + category + '</div></div>' +
                '<div class="preview-item"><div class="preview-label">سطح فوریت:</div><div class="preview-value">' + priorityText + '</div></div>' +
                '<div class="preview-item"><div class="preview-label">توضیحات:</div><div class="preview-value">' + desc + '</div></div>';

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
});
