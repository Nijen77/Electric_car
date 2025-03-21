let carData = []; // Глобальный массив для хранения данных автомобилей

document.getElementById("car_model").addEventListener("input", function () {
    let query = this.value.toLowerCase();
    let datalist = document.getElementById("car_model_list");

    if (query.length < 1) {
        datalist.innerHTML = ""; // Очищаем список, если нет ввода
        return;
    }

    fetch("./js/carsModels.json") // Загружаем список моделей авто
        .then(response => response.json())
        .then(data => {
            carData = data; // Сохраняем в глобальную переменную
            datalist.innerHTML = "";
            let count = 0;

            data.forEach(option => {
                if (option.name.toLowerCase().includes(query) && count < 5) {
                    let opt = document.createElement("option");
                    opt.value = option.name;
                    datalist.appendChild(opt);
                    count++;
                }
            }); let carData = []; // Глобальный массив для хранения данных автомобилей

            document.getElementById("car_model").addEventListener("input", function () {
                let query = this.value.toLowerCase();
                let datalist = document.getElementById("car_model_list");

                if (query.length < 1) {
                    datalist.innerHTML = ""; // Очищаем список, если нет ввода
                    return;
                }

                fetch("./js/carsModels.json") // Загружаем список моделей авто
                    .then(response => response.json())
                    .then(data => {
                        carData = data; // Сохраняем в глобальную переменную
                        datalist.innerHTML = "";
                        let count = 0;

                        data.forEach(option => {
                            if (option.Модель.toLowerCase().includes(query) && count < 5) {
                                let opt = document.createElement("option");
                                opt.value = option.Модель;
                                datalist.appendChild(opt);
                                count++;
                            }
                        });
                    })
                    .catch(error => console.error("Ошибка загрузки данных:", error));
            });

            document.getElementById("car_model").addEventListener("change", function () {
                let selectedModel = this.value;
                let hiddenInput = document.getElementById("car_id");

                let foundCar = carData.find(car => car.Модель === selectedModel);
                hiddenInput.value = foundCar ? foundCar._id : ""; // Заполняем ID
            });

            document.getElementById("battery_analysis").onsubmit = async (e) => {
                e.preventDefault();

                const formElement = document.querySelector("#battery_analysis");
                const formData = new FormData(formElement);
                const formDataObject = {
                    car_id: formData.get("car_id"),
                    mileage: formData.get("mileage"),
                    usage_time: formData.get("usage_time")
                };

                const jsonData = JSON.stringify(formDataObject);
                console.log(jsonData);

                try {
                    const response = await fetch("/submit-data", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: jsonData,
                    });

                    const { data } = await response.json();
                    if (data) console.log(data);

                    if (response.ok) {
                        alert("Данные успешно отправлены!");
                    } else {
                        alert(`Ошибка: ${data.error || "Неизвестная ошибка"}`);
                    }
                } catch (error) {
                    alert(`Произошла ошибка: ${error.message}`);
                }
            };

        })
        .catch(error => console.error("Ошибка загрузки данных:", error));
});

document.getElementById("car_model").addEventListener("change", function () {
    let selectedModel = this.value;
    let hiddenInput = document.getElementById("car_id");

    let foundCar = carData.find(car => car.name === selectedModel);
    hiddenInput.value = foundCar ? foundCar.id : ""; // Заполняем ID
});




document.getElementById("battery_analysis").onsubmit = async (e) => {
    e.preventDefault();

    const formElement = document.querySelector("#battery_analysis");
    const formData = new FormData(formElement);
    const formDataObject = Object.fromEntries(formData.entries());

    // Добавляем ID авто (если найден)
    let carId = carData.find(car => car.name === formDataObject.car_model)?.id || "";
    formDataObject["car_id"] = carId;

    const jsonData = JSON.stringify(formDataObject);
    console.log(jsonData)

    try {
        const response = await fetch("/submit-data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: jsonData,
        });

        const { data } = await response.json();
        if (data) console.log(data);

        if (response.ok) {
            alert("Данные успешно отправлены!");
        } else {
            alert(`Ошибка: ${data.error || "Неизвестная ошибка"}`);
        }
    } catch (error) {
        alert(`Произошла ошибка: ${error.message}`);
    }
};
