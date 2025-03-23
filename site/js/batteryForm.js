let carData = []; // Глобальный массив для хранения данных автомобилей

// Функция загрузки данных автомобилей
async function loadCarModels() {
    try {
        const response = await fetch("./js/carsModels.json");
        carData = await response.json();
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }
}

// Функция обновления списка моделей
function updateCarModelList(query) {
    const datalist = document.getElementById("car_model_list");
    datalist.innerHTML = ""; // Очищаем список

    if (query.length < 1) return;

    let count = 0;
    carData.forEach(option => {
        if (option.name.toLowerCase().includes(query) && count < 5) {
            let opt = document.createElement("option");
            opt.value = option.name;
            datalist.appendChild(opt);
            count++;
        }
    });
}

// Функция обработки выбора модели
function handleCarModelChange() {
    const selectedModel = document.getElementById("car_model").value;
    const hiddenInput = document.getElementById("car_id");

    const foundCar = carData.find(car => car.name === selectedModel);
    hiddenInput.value = foundCar ? foundCar.id : "";
}

// Функция обработки отправки формы
// async function handleFormSubmit(event) {
//     event.preventDefault();

//     const formElement = document.getElementById("battery_analysis");
//     const formData = new FormData(formElement);
//     const formDataObject = Object.fromEntries(formData.entries());

//     // Добавляем ID авто, если найден
//     formDataObject.car_id = carData.find(car => car.name === formDataObject.car_model)?.id || "";

//     // Удаляем `car_model`, если он не нужен
//     delete formDataObject.car_model;

//     // Приведение типов данных
//     if (formDataObject.probeg_km) {
//         formDataObject.probeg_km = parseInt(formDataObject.probeg_km, 10); // Преобразование в целое число
//     }
//     if (formDataObject.battery_age_months) {
//         formDataObject.battery_age_months = parseInt(formDataObject.battery_age_months, 10); // Преобразование в целое число
//     }

//     const jsonData = JSON.stringify(formDataObject);
//     console.log("Данные для отправки:", jsonData);

//     try {
//         // Отправка данных на /predict
//         const predictResponse = await fetch("http://127.0.0.1:5001/predict", {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: jsonData,
//         });

//         const predictResult = await predictResponse.json();

//         if (predictResponse.ok) {
//             console.log("Ответ от /predict:", predictResult);
//             getImage(predictResult);


//             // Отправка данных на /submit-data
//             const submitResponse = await fetch("http://127.0.0.1:5000/submit-data", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: jsonData,
//             });

//             const submitResult = await submitResponse.json();

//             if (submitResponse.ok) {
//                 console.log("Данные успешно записаны в MongoDB:", submitResult);
//                 alert("Запросы успешно выполнены!");
//             } else {
//                 console.error("Ошибка при записи в MongoDB:", submitResult.error);
//                 alert(`Ошибка записи в MongoDB: ${submitResult.error}`);
//             }
//         } else {
//             console.error("Ошибка от /predict:", predictResult.error);
//             alert(`Ошибка обработки данных: ${predictResult.error}`);
//         }
//     } catch (error) {
//         console.error("Ошибка сети или сервера:", error);
//         alert(`Произошла ошибка: ${error.message}`);
//     }
// }
async function handleFormSubmit(event) {
    event.preventDefault();

    const formElement = document.getElementById("battery_analysis");
    const loadingElement = document.getElementById("battery_loading"); // Получаем элемент загрузки
    const formData = new FormData(formElement);
    const formDataObject = Object.fromEntries(formData.entries());

    // Добавляем ID авто, если найден
    formDataObject.car_id = carData.find(car => car.name === formDataObject.car_model)?.id || "";

    // Удаляем `car_model`, если он не нужен
    delete formDataObject.car_model;

    // Приведение типов данных
    if (formDataObject.probeg_km) {
        formDataObject.probeg_km = parseInt(formDataObject.probeg_km, 10);
    }
    if (formDataObject.battery_age_months) {
        formDataObject.battery_age_months = parseInt(formDataObject.battery_age_months, 10);
    }

    const jsonData = JSON.stringify(formDataObject);
    console.log("Данные для отправки:", jsonData);

    try {
        // Показываем загрузку
        loadingElement.style.display = "flex";

        // Отправка данных на /predict
        const predictResponse = await fetch("http://127.0.0.1:5001/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: jsonData,
        });

        const predictResult = await predictResponse.json();

        if (predictResponse.ok) {
            console.log("Ответ от /predict:", predictResult);
            getImage(predictResult);

            // Отправка данных на /submit-data
            const submitResponse = await fetch("http://127.0.0.1:5000/submit-data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: jsonData,
            });

            const submitResult = await submitResponse.json();

            if (submitResponse.ok) {
                console.log("Данные успешно записаны в MongoDB:", submitResult);
                alert("Запросы успешно выполнены!");
            } else {
                console.error("Ошибка при записи в MongoDB:", submitResult.error);
                alert(`Ошибка записи в MongoDB: ${submitResult.error}`);
            }
        } else {
            console.error("Ошибка от /predict:", predictResult.error);
            alert(`Ошибка обработки данных: ${predictResult.error}`);
        }
    } catch (error) {
        console.error("Ошибка сети или сервера:", error);
        alert(`Произошла ошибка: ${error.message}`);
    } finally {
        // Скрываем загрузку в любом случае (успех или ошибка)
        loadingElement.style.display = "none";
    }
}

document.getElementById("battery_analysis").addEventListener("submit", handleFormSubmit);


// Назначаем обработчики событий
document.getElementById("car_model").addEventListener("input", function () {
    updateCarModelList(this.value.toLowerCase());
});
document.getElementById("car_model").addEventListener("change", handleCarModelChange);
// document.getElementById("battery_analysis").addEventListener("submit", handleFormSubmit);

// Загружаем данные автомобилей при загрузке страницы
loadCarModels();

function updateUIX({ degradation, recommendations }) {
    const resultBlock = document.querySelector('.battery-result_content');
    if (!resultBlock) return;

    resultBlock.innerHTML = `<h3>Оценка состояния аккумулятора</h3>
        <img src="/source/img/photo.jpg" alt="">
        дегрод${degradation} и реком ${recommendations}`
        ;

}


function getImage({ value, text }) {
    let imagePath;

    if (value < 10) {
        imagePath = "source/img/less_10.svg";
    } else if (value < 20) {
        imagePath = "source/img/10-20.svg";
    } else if (value < 40) {
        imagePath = "source/img/20-40.svg";
    } else if (value <= 60) {
        imagePath = "source/img/40-60.svg";
    } else if (value <= 80) {
        imagePath = "source/img/60-80.svg";
    } else {
        imagePath = "source/img/more_80.svg";
    }

    // Вывод изображения и текста (можно вставить в HTML)
    const imgElement = document.createElement("img");
    imgElement.src = imagePath;
    imgElement.alt = text;
    imgElement.classList.add('battery-picture')

    const textElement = document.createElement("h3");
    textElement.textContent = text;

    const container = document.getElementById("map-result_content");
    container.innerHTML = ""; // Очистка перед вставкой нового
    container.appendChild(imgElement);
    container.appendChild(textElement);
}

// Пример использования
