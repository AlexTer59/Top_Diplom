// Получаем элементы панели и кнопок
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebarClose = document.getElementById('sidebarClose');

// Открытие панели
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.add('active');
});

// Закрытие панели
sidebarClose.addEventListener('click', () => {
    sidebar.classList.remove('active');
});

// Закрытие панели при клике вне её области (опционально)
document.addEventListener('click', (event) => {
    if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
        sidebar.classList.remove('active');
    }
});