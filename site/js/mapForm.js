document.getElementById('mapForm').onsubmit = async (e) => {
    e.preventDefault();

    const formElement = document.querySelector('#mapForm');
    const formData = new FormData(formElement);

    // Преобразуем FormData в объект
    const formDataObject = Object.fromEntries(formData.entries());
    formDataObject['parameters'] = formData.getAll('parameters'); // Обработка полей с одинаковым именем

    const jsonData = JSON.stringify(formDataObject);

    try {
        // Отправка запроса
        const response = await fetch('/submit-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: jsonData,
        });

        const { data } = await response.json();
        if (data) {
            console.log(data.start_point, data.end_point);
}

        if (response.ok) {
            updateUI(data); // Передаем данные в функцию обновления UI
        } else {
            alert(`Ошибка: ${data.error || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        alert(`Произошла ошибка: ${error.message}`);
    }
};

// Функция для обновления UI
function updateUI(datas) {
    const resultBlock = document.querySelector('.map-result_content');

    if (!resultBlock) {
        console.error('Элемент для отображения результата не найден');
        return;
    }

    // Используем шаблонные строки для корректной вставки HTML
    resultBlock.innerHTML = `
        <h3>Результаты:</h3>
        <p>Начальная точка: ${datas.start_point || 'Не указано'}</p>
        <p>Конечная точка: ${datas.end_point || 'Не указано'}</p>
    `;
}