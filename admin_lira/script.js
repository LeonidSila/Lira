document.getElementById('openFormBtn').addEventListener('click', function() {
    closeAllForms(); // Закрываем все формы
    document.getElementById('overlay').style.display = 'flex'; // Открываем первую форму
});

document.getElementById('closeFormBtn').addEventListener('click', function() {
    document.getElementById('overlay').style.display = 'none'; // Закрываем первую форму
});

document.getElementById('openSimpleFormBtn').addEventListener('click', function() {
    closeAllForms(); // Закрываем все формы
    document.getElementById('simpleOverlay').style.display = 'flex'; // Открываем простую форму
});

document.getElementById('closeSimpleFormBtn').addEventListener('click', function() {
    document.getElementById('simpleOverlay').style.display = 'none'; // Закрываем простую форму
});

document.getElementById('selectAllBtn').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('input[name="theme"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
});

document.getElementById('deselectAllBtn').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('input[name="theme"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
});

// Закрываем все формы
function closeAllForms() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('simpleOverlay').style.display = 'none';
}

// Обработчик отправки первой формы
document.getElementById('sendBtn').addEventListener('click', function(event) {
    event.preventDefault();

    const selectedThemes = Array.from(document.querySelectorAll('input[name="theme"]:checked'))
        .map(checkbox => checkbox.value);
    const messageText = document.getElementById('message').value;
    const fileInput = document.getElementById('fileInput').files[0];

    if (selectedThemes.length || messageText || fileInput) {
        const url = 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage';
        const chatId = '<YOUR_CHAT_ID>';

        let textMessage = `Выбранные темы: ${selectedThemes.join(', ')}\nСообщение: ${messageText}`;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: chatId,
                text: textMessage
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Сообщение отправлено в Telegram!');
                document.getElementById('overlay').style.display = 'none';
            } else {
                alert('Произошла ошибка при отправке сообщения.');
            }
        })
        .catch(err => {
            console.log(err);
            alert('Произошла ошибка при отправке сообщения.');
        });

        if (fileInput) {
            const fileUrl = `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendDocument`;
            const fileData = new FormData();
            fileData.append('chat_id', chatId);
            fileData.append('document', fileInput);

            fetch(fileUrl, {
                method: 'POST',
                body: fileData
            })
            .then(response => {
                if (response.ok) {
                    alert('Файл отправлен в Telegram!');
                } else {
                    alert('Произошла ошибка при отправке файла.');
                }
            })
            .catch(err => {
                console.log(err);
                alert('Произошла ошибка при отправке файла.');
            });
        }

    } else {
        alert('Пожалуйста, выберите хотя бы одну тему или введите сообщение.');
    }
});

// Обработчик отправки второй формы
document.getElementById('sendSimpleBtn').addEventListener('click', function(event) {
    event.preventDefault();

    const simpleMessageText = document.getElementById('simpleMessage').value;
    const simpleFileInput = document.getElementById('simpleFileInput').files[0];

    if (simpleMessageText || simpleFileInput) {
        const url = 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage';
        const chatId = '<YOUR_CHAT_ID>';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: chatId,
                text: simpleMessageText
            })
        })
        .then(response => {
            if (response.ok) {
                alert('Сообщение отправлено в Telegram!');
                document.getElementById('simpleOverlay').style.display = 'none';
            } else {
                alert('Произошла ошибка при отправке сообщения.');
            }
        })
        .catch(err => {
            console.log(err);
            alert('Произошла ошибка при отправке сообщения.');
        });

        if (simpleFileInput) {
            const fileUrl = `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendDocument`;
            const fileData = new FormData();
            fileData.append('chat_id', chatId);
            fileData.append('document', simpleFileInput);

            fetch(fileUrl, {
                method: 'POST',
                body: fileData
            })
            .then(response => {
                if (response.ok) {
                    alert('Файл отправлен в Telegram!');
                } else {
                    alert('Произошла ошибка при отправке файла.');
                }
            })
            .catch(err => {
                console.log(err);
                alert('Произошла ошибка при отправке файла.');
            });
        }

    } else {
        alert('Пожалуйста, введите сообщение.');
    }
});