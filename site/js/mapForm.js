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
        //полученние обработанных данных - деструктуризация 
        const { data } = await response.json();
        if (data) { console.log(data); } //вывод данных в случае успеха




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
function updateUI({ start_latitude, start_longitude, end_latitude, end_longitude }) {
    const resultBlock = document.querySelector('.map-result_content');

    if (!resultBlock) {
        console.error('Элемент для отображения результата не найден');
        return;
    }
    let latitude_center = (start_latitude + end_latitude) / 2;
    let longitude_center = (start_longitude + end_longitude) / 2;
    let zoom = 10;


    // Используем шаблонные строки для корректной вставки HTML
    resultBlock.innerHTML = `
        <h3>Маршрут</h3>
        <iframe src="https://yandex.ru/map-widget/v1/?from=mapframe&ll=${longitude_center}%2C${latitude_center}&mode=routes&rtext=${start_latitude}%2C${start_longitude}~${end_latitude}%2C${end_longitude}&rtt=auto&ruri=~&z=${zoom}" width="560" height="400" frameborder="1" allowfullscreen="true" style="position:relative;"></iframe>
    `;
}

