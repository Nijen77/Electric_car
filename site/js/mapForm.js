document.getElementById('mapForm').onsubmit = async (e) => {
    e.preventDefault();

    const formElement = document.querySelector('#mapForm');
    const formData = new FormData(formElement);
    const formDataObject = Object.fromEntries(formData.entries());
    formDataObject['parameters'] = formData.getAll('parameters');
    const jsonData = JSON.stringify(formDataObject);

    showLoading(); // Показываем индикатор загрузки

    try {
        const response = await fetch('/submit-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: jsonData,
        });

        const { data } = await response.json();
        if (data) console.log(data);

        if (response.ok) {
            updateUI(data); // Обновляем UI с полученными данными
        } else {
            alert(`Ошибка: ${data.error || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        alert(`Произошла ошибка: ${error.message}`);
    } finally {
        hideLoading(); // Скрываем индикатор загрузки после завершения запроса
    }
};

function showLoading() {
    document.getElementById('loading').style.display = 'flex'; // Отображаем экран загрузки
    document.getElementById('submitButton').disabled = true; // Блокируем кнопку отправки
    document.body.classList.add('loading-active'); // Блокируем взаимодействие со всей страницей
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none'; // Скрываем экран загрузки
    document.getElementById('submitButton').disabled = false; // Разблокируем кнопку отправки
    document.body.classList.remove('loading-active'); // Разрешаем взаимодействие со страницей
}

function updateUI({ start_latitude, start_longitude, end_latitude, end_longitude }) {
    const resultBlock = document.querySelector('.map-result_content');
    if (!resultBlock) return;

    let latitude_center = (start_latitude + end_latitude) / 2;
    let longitude_center = (start_longitude + end_longitude) / 2;
    let zoom = 10;

    // Отображаем карту с маршрутом
    resultBlock.innerHTML = `
        <h3>Маршрут</h3>
        <iframe src="https://yandex.ru/map-widget/v1/?from=mapframe&ll=${longitude_center}%2C${latitude_center}&mode=routes&rtext=${start_latitude}%2C${start_longitude}~${end_latitude}%2C${end_longitude}&rtt=auto&ruri=~&z=${zoom}" 
                width="560" height="400" frameborder="1" allowfullscreen="true" style="position:relative;"></iframe>
    `;
}