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
            newListName: "", // Для имени нового списка
            editListId: null,
            isOwner: false,
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
                this.isOwner = this.board.owner.id == this.$el.getAttribute('data-user-id'); // Проверяем, является ли текущий пользователь владельцем

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
            console.log('Добавить задачу в список ${listId}');
        },

        // Метод для добавления нового списка
        async addNewList() {
            if (!this.newListName.trim()) {
                alert("Введите имя списка");
                return;
            }

            try{
                const response = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/create/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify({ name: this.newListName }),
                });

                if (!response.ok) {
                    throw new Error("Ошибка при добавлении списка");
                }

                const newList = await response.json();
                this.lists.push(newList);
                this.closeCreateListPopup()
                this.newListName = '';

            } catch(error) {
                print('err')
                alert(error.message);
            }
        },

        async editList() {
            if (!this.newListName.trim()) {
                alert('Введите имя списка');
                return;
            }
            try {
                const response = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${this.editListId}/edit/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({ name: this.newListName }),
                });
                if (!response.ok) {
                    throw new Error('Ошибка при обновлении списка');
                }
                const updatedList = await response.json();
                const index = this.lists.findIndex(list => list.id === updatedList.id);
                if (index !== -1) {
                    // Обновляем список в массиве с использованием this.$set
                    this.$set(this.lists, index, updatedList);
                }
                this.closeEditListPopup();


            } catch (error) {
                alert(error.message);
            }
        },

        async deleteList() {
            if (confirm('Вы уверены, что хотите удалить этот список?')) {
                try {
                    // Отправляем запрос на сервер для удаления списка
                    const response = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${this.editListId}/delete/`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken(),
                        },
                    });

                    if (!response.ok) {
                        throw new Error('Ошибка при удалении списка');
                    }

                    // Удаляем список из локального массива
                    const index = this.lists.findIndex(list => list.id === this.editListId); // Найдем индекс элемента
                    if (index !== -1) {
                        this.lists.splice(index, 1); // Удаляем элемент по индексу
                    }
                    this.closeEditListPopup();
                } catch (error) {
                    alert(error.message);
                }
            }
        },

        openCreateListPopup() {
            const modal = new bootstrap.Modal(document.getElementById('addListModal'));
            modal.show(); // Явно вызываем Bootstrap метод для открытия окна
        },
        closeCreateListPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addListModal'));
            modal.hide(); // Явно вызываем Bootstrap метод для скрытия окна
        },

        openEditListPopup(list) {
            const modal = new bootstrap.Modal(document.getElementById('editListModal'));
            this.newListName = list.name;
            this.editListId = list.id;
            modal.show(); // Явно вызываем Bootstrap метод для открытия окна
        },

        closeEditListPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('editListModal'));
            this.newListName = '';
            this.editListId = null;
            modal.hide(); // Явно вызываем Bootstrap метод для скрытия окна
        },
    },
});