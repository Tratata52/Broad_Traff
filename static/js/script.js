//let allData = {};  // Все данные
//let filteredData = {};  // Отфильтрованные данные
//
//// Функция для загрузки данных
//async function loadData() {
//    try {
//        const response = await fetch('/static/compact_contact_sources.json'); // Путь к файлу JSON
//        const data = await response.json();
//        allData = data;
//        filteredData = data;
//        populateProjectFilter(data);
//        generateTable(filteredData);
//        updateSummary(filteredData);
//    } catch (error) {
//        console.error('Ошибка загрузки данных:', error);
//    }
//}
//
//// Генерация таблицы с фильтрацией
//function generateTable(data) {
//    const tbody = document.getElementById('tableBody');
//    tbody.innerHTML = ''; // Очищаем таблицу
//
//    const aggregatedData = {}; // Данные по источникам
//
//    // Агрегируем данные по источникам, исключая повторения
//    for (const date in data) {
//        for (const project in data[date]) {
//            const sources = data[date][project];
//            for (const source in sources) {
//                if (!aggregatedData[source]) {
//                    aggregatedData[source] = { горячие_лиды: 0, звонки: 0 };
//                }
//                aggregatedData[source].горячие_лиды += sources[source].горячие_лиды || 0;
//                aggregatedData[source].звонки += sources[source].звонки || 0;
//            }
//        }
//    }
//
//    // Создаем строки таблицы с суммой по каждому источнику
//    for (const source in aggregatedData) {
//        const row = document.createElement('tr');
//        row.innerHTML = `
//            <td>${source}</td>
//            <td class="${aggregatedData[source].горячие_лиды > 0 ? 'highlight-hot-leads' : ''}">
//                ${aggregatedData[source].горячие_лиды}
//            </td>
//            <td>${aggregatedData[source].звонки}</td>
//        `;
//        tbody.appendChild(row);
//    }
//}
//
//// Обновление информации о статистике
//function updateSummary(data) {
//    let hotLeadsCount = 0;
//    let totalCalls = 0;
//
//    for (const date in data) {
//        for (const project in data[date]) {
//            const sources = data[date][project];
//            for (const source in sources) {
//                hotLeadsCount += sources[source].горячие_лиды || 0;
//                totalCalls += sources[source].звонки || 0;
//            }
//        }
//    }
//
//    document.getElementById('hotLeadsCount').textContent = hotLeadsCount;
//    document.getElementById('totalCalls').textContent = totalCalls;
//}
//
//// Заполнение фильтра проектов
//function populateProjectFilter(data) {
//    const projectFilter = document.getElementById('projectFilter');
//    const projects = new Set();
//
//    for (const date in data) {
//        for (const project in data[date]) {
//            projects.add(project);
//        }
//    }
//
//    projects.forEach(project => {
//        const option = document.createElement('option');
//        option.value = project;
//        option.textContent = project;
//        projectFilter.appendChild(option);
//    });
//}
//
//// Применение фильтров
//function applyFilters() {
//    const projectFilter = document.getElementById('projectFilter').value;
//    const startDate = document.getElementById('startDateFilter').value;
//    const endDate = document.getElementById('endDateFilter').value;
//
//    filteredData = {}; // Очистка данных перед фильтрацией
//
//    // Фильтрация данных по датам и проектам
//    for (const date in allData) {
//        if ((startDate === "" || date >= startDate) && (endDate === "" || date <= endDate)) {
//            for (const project in allData[date]) {
//                if (projectFilter === "" || project === projectFilter) {
//                    if (!filteredData[date]) {
//                        filteredData[date] = {};
//                    }
//                    filteredData[date][project] = allData[date][project];
//                }
//            }
//        }
//    }
//
//    generateTable(filteredData); // Перегенерация таблицы
//    updateSummary(filteredData); // Обновление статистики
//}
//
//// Сортировка таблицы по столбцам
//let sortDirection = [true, true, true]; // Для сортировки
//function sortTable(colIndex) {
//    const rows = document.querySelectorAll('#dataTable tbody tr');
//    const rowsArray = Array.from(rows);
//    const direction = sortDirection[colIndex] ? 1 : -1;
//
//    rowsArray.sort((rowA, rowB) => {
//        const cellA = rowA.cells[colIndex].textContent.trim();
//        const cellB = rowB.cells[colIndex].textContent.trim();
//        return (cellA - cellB) * direction;
//    });
//
//    rowsArray.forEach(row => document.querySelector('#dataTable tbody').appendChild(row));
//
//    sortDirection[colIndex] = !sortDirection[colIndex]; // Переключаем направление сортировки
//}
//
//
//// Функция для вычисления цвета фона
//function getLeadBackgroundColor(hotLeads) {
//    // Максимальное количество лидов для расчета (можно настроить по необходимости)
//    const maxLeads = 1000;
//
//    // Нормализуем количество лидов в диапазон от 0 до 1
//    const normalized = Math.min(hotLeads / maxLeads, 1); // Ограничиваем максимальное значение 1
//
//    // Рассчитываем цвет на основе нормализованного значения
//    const red = Math.floor(255 - (normalized * 255)); // Чем больше лидов, тем краснее
//    const green = Math.floor(normalized * 255); // Чем больше лидов, тем зеленее
//
//    return `rgb(${red}, ${green}, 0)`; // Цвет от желтого (255, 255, 0) до зеленого (0, 255, 0)
//}
//
//// Загружаем данные при старте страницы
//loadData();