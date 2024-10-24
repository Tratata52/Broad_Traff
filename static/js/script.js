//function sendRow(callId) {
//    const customerName = document.querySelector(`#call-${callId} [data-field="name"]`).value;
//    const city = document.querySelector(`#call-${callId} [data-field="city"]`).value;
//    const comment = document.querySelector(`#call-${callId} [data-field="comment"]`).value;
//
//    $.ajax({
//        type: 'POST',
//        url: `/send/${callId}`,
//        data: JSON.stringify({
//            id: callId,
//            name_note: customerName,
//            city_note: city,
//            note: comment
//        }),
//        contentType: 'application/json'
//    }).done(function(response) {
//        if (response.status === "success") {
//            alert("Данные успешно отправлены!");
//        } else {
//            alert("Ошибка: " + response.message);
//        }
//    }).fail(function(xhr) {
//        alert("Ошибка при отправке данных: " + xhr.responseText);
//    });
//}
//
//const duplicates = {{ duplicates | tojson }};
//
//function checkDuplicates() {
//    const rows = document.querySelectorAll('tbody tr');
//    rows.forEach(row => {
//        const phone = row.querySelector('td:nth-child(2)').innerText;
//        if (duplicates.includes(phone)) {
//            row.classList.add('duplicate-phone');
//        }
//    });
//}
//
//document.addEventListener('DOMContentLoaded', checkDuplicates);
//
//function saveRow(callId) {
//    const customerName = document.querySelector(`#call-${callId} [data-field="name"]`).value;
//    const city = document.querySelector(`#call-${callId} [data-field="city"]`).value;
//    const comment = document.querySelector(`#call-${callId} [data-field="comment"]`).value;
//
//    $.ajax({
//        type: 'POST',
//        url: '/save_lead',
//        data: JSON.stringify({
//            id: callId,
//            name_note: customerName,
//            city_note: city,
//            note: comment
//        }),
//        contentType: 'application/json'
//    }).done(function(response) {
//        if (response.status === "success") {
//            alert("Данные успешно сохранены!");
//        } else {
//            alert("Ошибка: " + response.message);
//        }
//    }).fail(function(xhr) {
//        alert("Ошибка при отправке данных: " + xhr.responseText);
//    });
//}
//
//function deleteRow(callId) {
//    $.ajax({
//        type: 'POST',
//        url: `/delete/${callId}`,
//        success: function(response) {
//            if (response.status === "success") {
//                $(`#call-${callId}`).remove();
//                alert("Строка успешно удалена!");
//            } else {
//                alert("Ошибка при удалении строки: " + response.message);
//            }
//        },
//        error: function(xhr) {
//            alert("Ошибка при удалении строки: " + xhr.responseText);
//        }
//    });
//}
//
//function approveRow(callId) {
//    $.ajax({
//        type: 'POST',
//        url: `/approve/${callId}`,
//        success: function(response) {
//            if (response.status === "success") {
//                $(`#call-${callId}`).remove();
//                alert("Звонок успешно согласован и удален!");
//            } else {
//                alert("Ошибка при согласовании: " + response.message);
//            }
//        },
//        error: function(xhr) {
//            alert("Ошибка при согласовании: " + xhr.responseText);
//        }
//    });
//}
//
//function togglePlay(callId) {
//const player = document.getElementById(`player-${callId}`);
//const audio = document.getElementById(`audio-${callId}`);
//const playBtn = player.querySelector('.play-btn');
//const pauseBtn = player.querySelector('.pause-btn');
//
//if (audio.paused) {
//    audio.play();
//    playBtn.style.display = 'none';
//    pauseBtn.style.display = 'block';
//} else {
//    audio.pause();
//    playBtn.style.display = 'block';
//    pauseBtn.style.display = 'none';
//}
//
//// Обновляем прогресс-бар
//audio.ontimeupdate = function () {
//    updateProgress(callId);
//};
//}
//
//function updateProgress(callId) {
//    const player = document.getElementById(`player-${callId}`);
//    const audio = document.getElementById(`audio-${callId}`);
//    const progressBar = player.querySelector('.progress-bar');
//    const percentage = (audio.currentTime / audio.duration) * 100;
//    progressBar.style.width = `${percentage}%`;
//}
//
//function setProgress(event, callId) {
//    const player = document.getElementById(`player-${callId}`);
//    const audio = document.getElementById(`audio-${callId}`);
//    const progressContainer = player.querySelector('.progress-container');
//    const clickX = event.offsetX;
//    const width = progressContainer.clientWidth;
//    const duration = audio.duration;
//
//    audio.currentTime = (clickX / width) * duration;
//}
