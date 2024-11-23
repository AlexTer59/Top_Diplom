// board_detail.js

// Получаем CSRF токен
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Инициализация Vue
new Vue({
    el: '#app', // Привязываем Vue к элементу с id="app"
    delimiters: ['[[', ']]'],
    data() {
        return {
            boardId: null,  // Изначально boardId будет пустым
            baseUrl: 'http://127.0.0.1:8000/', // Базовый URL, который можно легко изменить
            board: {}, // Данные о доске
            lists: [],  // Массив для списков
            tasks: {},  // Массив задач для каждого списка
        };
    },
    mounted() {
        this.boardId = this.$el.getAttribute('data-board-id'); // Получаем boardId из data-атрибута только после монтирования
        this.fetchBoardData(); // Загружаем данные сразу при монтировании компонента
    },
    methods: {
        // Метод для загрузки данных о доске и списках
        async fetchBoardData() {
            if (!this.boardId) {
                console.error('Board ID is missing!');
                return;
            }

            try {
                // Запрашиваем данные о доске
                const boardResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/`);
                const boardData = await boardResponse.json();
                this.board = boardData; // Сохраняем данные о доске

                // Запрашиваем все списки для этой доски
                const listsResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/`);
                const listsData = await listsResponse.json();
                this.lists = listsData; // Сохраняем списки

                // Для каждого списка запрашиваем задачи
                for (let list of this.lists) {
                    const tasksResponse = await fetch(`${this.baseUrl}api/lists/${list.id}/tasks/`);
                    const tasksData = await tasksResponse.json();
                    this.$set(this.tasks, list.id, tasksData); // Сохраняем задачи для каждого списка
                }
            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        },

        // Метод для добавления новой задачи в список
        addTask(listId) {
            console.log(`Добавить задачу в список ${listId}`);
        },

        // Метод для добавления нового списка
        addNewList() {
            console.log("Добавить новый список");
        },
    }
});