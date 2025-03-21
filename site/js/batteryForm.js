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
async function handleFormSubmit(event) {
    event.preventDefault();

    const formElement = document.getElementById("battery_analysis");
    const formData = new FormData(formElement);
    const formDataObject = Object.fromEntries(formData.entries());

    // Добавляем ID авто, если найден
    formDataObject.car_id = carData.find(car => car.name === formDataObject.car_model)?.id || "";

    // Удаляем `car_model`, если он не нужен
    delete formDataObject.car_model;

    const jsonData = JSON.stringify(formDataObject);
    console.log(jsonData);

    try {
        const response = await fetch("/submit-data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: jsonData,
        });

        const { data } = await response.json();
        if (response.ok) {
            alert("Данные успешно отправлены!");
        } else {
            alert(`Ошибка: ${data.error || "Неизвестная ошибка"}`);
        }
    } catch (error) {
        alert(`Произошла ошибка: ${error.message}`);
    }
}

// Назначаем обработчики событий
document.getElementById("car_model").addEventListener("input", function () {
    updateCarModelList(this.value.toLowerCase());
});
document.getElementById("car_model").addEventListener("change", handleCarModelChange);
document.getElementById("battery_analysis").addEventListener("submit", handleFormSubmit);

// Загружаем данные автомобилей при загрузке страницы
loadCarModels();

