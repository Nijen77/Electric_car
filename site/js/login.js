document.getElementById('formLog').onsubmit = async (e) => {
    e.preventDefault(); // Предотвращаем стандартное поведение формы

    // Собираем данные формы вручную как объект (не FormData)
    const formElement = document.querySelector('#formLog');

    const formDataObject = Object.fromEntries(new FormData(formElement).entries());

    const jsonData = JSON.stringify(formDataObject); // Преобразуем объект в JSON

    console.log('Данные формы в JSON:', jsonData); // Проверяем данные перед отправкой

    try {
        let response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonData
        });

        if (response.ok) {
            const result = await response.json();
            alert(`Успех: ${result.message}`);
            window.location.href = '/index.html';
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.error || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        alert(`Произошла ошибка: ${error.message}`);
    }
};
alert('s')