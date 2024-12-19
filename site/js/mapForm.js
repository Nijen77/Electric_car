document.getElementById('mapForm').onsubmit = async (e) => {
    e.preventDefault(); // Предотвращаем стандартное поведение формы

    const formElement = document.querySelector('#mapForm');
    const formData = new FormData(formElement);

    // Используем getAll() для получения всех значений 'parameters[]'
    const formDataObject = Object.fromEntries(formData.entries());
    formDataObject['parameters'] = formData.getAll('parameters');

    const jsonData = JSON.stringify(formDataObject); // Преобразуем объект в JSON

    console.log('Данные формы в JSON:', jsonData); // Проверяем данные перед отправкой

    try {
        let response = await fetch('/submit-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: jsonData
        });

        if (response.ok) {
            const result = await response.json();
            alert(`Успех: ${result.message}`);
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.error || 'Неизвестная ошибка'}`);
        }

        if (response.ok) {
            const updatedData = await response.json();
            console.log('Обновленные данные из базы:', updatedData);
            updateUI(updatedData); // Функция для обновления интерфейса новыми данными
        } else {
            const error = await response.json();
            alert(`Ошибка: ${error.error || 'Неизвестная ошибка'}`);
        }
    } catch (error) {
        alert(`Произошла ошибка: ${error.message}`);
    }
};