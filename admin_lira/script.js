// Инициализация Telegram Web App

// Открытие формы
document.getElementById('openFormBtn').addEventListener('click', function() {
    closeAllForms(); // Закрываем все формы
    document.getElementById('overlay').style.display = 'flex'; // Открываем первую форму
});

// Закрытие формы
document.getElementById('closeFormBtn').addEventListener('click', function() {
    document.getElementById('overlay').style.display = 'none'; // Закрываем первую форму
});

// Открытие простой формы
document.getElementById('openSimpleFormBtn').addEventListener('click', function() {
    closeAllForms(); // Закрываем все формы
    document.getElementById('simpleOverlay').style.display = 'flex'; // Открываем простую форму
});

// Закрытие простой формы
document.getElementById('closeSimpleFormBtn').addEventListener('click', function() {
    document.getElementById('simpleOverlay').style.display = 'none'; // Закрываем простую форму
});

// Выбор всех тем
document.getElementById('selectAllBtn').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('input[name="theme"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
});

// Снятие выбора всех тем
document.getElementById('deselectAllBtn').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('input[name="theme"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
});

// Закрытие всех форм
function closeAllForms() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('simpleOverlay').style.display = 'none';
}

// Обработчик отправки первой формы
document.addEventListener('DOMContentLoaded', function () {
    let selectedThemes = []; // Массив для хранения выбранных тем
    let tg = window.Telegram.WebApp;

    // Функция для открытия модального окна с выбором тем
    const openFormBtn = document.getElementById('openFormBtn');
    const overlay = document.getElementById('overlay');
    const closeFormBtn = document.getElementById('closeFormBtn');

    openFormBtn.addEventListener('click', () => {
        overlay.style.display = 'block';
    });

    closeFormBtn.addEventListener('click', () => {
        overlay.style.display = 'none';
    });

    // Функция для открытия модального окна для отправки сообщения без выбора темы
    const openSimpleFormBtn = document.getElementById('openSimpleFormBtn');
    const simpleOverlay = document.getElementById('simpleOverlay');
    const closeSimpleFormBtn = document.getElementById('closeSimpleFormBtn');

    openSimpleFormBtn.addEventListener('click', () => {
        simpleOverlay.style.display = 'block';
    });

    closeSimpleFormBtn.addEventListener('click', () => {
        simpleOverlay.style.display = 'none';
    });


    // Обработка кнопки "Выбрать все"
    const selectAllBtn = document.getElementById('selectAllBtn');
    selectAllBtn.addEventListener('click', () => {
        const checkboxes = document.querySelectorAll('input[name="theme"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    });

    // Обработка кнопки "Снять выбор"
    const deselectAllBtn = document.getElementById('deselectAllBtn');
    deselectAllBtn.addEventListener('click', () => {
        const checkboxes = document.querySelectorAll('input[name="theme"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
    });

    // Обработка отправки формы с выбором тем
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.addEventListener('click', () => {
        selectedThemes = []; // Очищаем массив перед заполнением
        const checkboxes = document.querySelectorAll('input[name="theme"]:checked');
        checkboxes.forEach(checkbox => {
            selectedThemes.push(checkbox.value);
        });

        const message = document.getElementById('message').value;
        let data = {
            themes: selectedThemes,
            message: message
        };

        tg.sendData(JSON.stringify(data));
        console.log("Данные отправлены:", data);
    });

    // Обработка отправки формы без выбора темы
    const sendSimpleBtn = document.getElementById('sendSimpleBtn');
    sendSimpleBtn.addEventListener('click', () => {
        const simpleMessage = document.getElementById('simpleMessage').value;

        let simpleData = {
            message: simpleMessage
        };

        tg.sendData(JSON.stringify(simpleData));
        console.log("Данные отправлены:", simpleData);
    });
});