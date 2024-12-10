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
            boardMembers: [], // Участники доски
            lists: [],  // Массив для списков
            tasks: {},  // Массив задач для каждого списка

            defaultAvatar: '',

            newListName: "", // Для имени нового списка
            editListId: null,
            isOwner: false,

            newTaskTitle: "",
            newTaskDescription: "",
            newTaskAssignedTo: null,
            newTaskStatus: null,
            newTaskDeadline: null,
            newTaskIsUrgent: false,


        };
    },
    mounted() {
        this.boardId = this.$el.getAttribute('data-board-id'); // Получаем boardId из data-атрибута только после монтирования
        this.defaultAvatar = this.$el.getAttribute('data-default-avatar')
        this.fetchBoardData(); // Загружаем данные сразу при монтировании компонента

    },
    methods: {
        // Метод для сортировки задач в списке по дедлайну и срочности
        sortTasksByDueDateAndUrgency(listId) {
            if (Array.isArray(this.tasks[listId])) {
                this.tasks[listId].sort((a, b) => {
                    // Сначала проверяем на просроченность (is_overdue), потом срочность (is_urgent)
                    if (a.is_overdue !== b.is_overdue) {
                        return a.is_overdue ? -1 : 1; // Просроченные задачи идут первыми
                    }

                    if (a.is_urgent !== b.is_urgent) {
                        return a.is_urgent ? -1 : 1; // Срочные задачи идут после просроченных
                    }

                    // Если задачи имеют одинаковую срочность/прошедший срок, сортируем по дедлайну
                    const dateA = new Date(a.due_date);
                    const dateB = new Date(b.due_date);
                    return dateA - dateB; // Сортируем по возрастанию дедлайна
                });
            }
        },

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
                this.isOwner = this.board.owner == this.$el.getAttribute('data-user-id'); // Проверяем, является ли текущий пользователь владельцем

                // Запрашиваем участников доски
                const boardMembersResponse = await fetch(`${this.baseUrl}users/profiles/boards/${this.boardId}/`);
                const membersData = await boardMembersResponse.json();
                this.boardMembers = membersData;


                // Запрашиваем все списки для этой доски
                const listsResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/`);
                const listsData = await listsResponse.json();
                this.lists = listsData; // Сохраняем списки

                // Для каждого списка запрашиваем задачи
                for (let list of this.lists) {
                    const tasksResponse = await fetch(`${this.baseUrl}api/lists/${list.id}/tasks/`);
                    const tasksData = await tasksResponse.json();
                    this.$set(this.tasks, list.id, tasksData); // Сохраняем задачи для каждого списка

                    this.sortTasksByDueDateAndUrgency(list.id); // Сортируем задачи по дедлайну и срочности
                }

            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        },


        // ========================== СПИСКИ ==================================
        // Метод для пересчета позиций списков
        recalculatePositions() {
            this.lists.forEach((list, index) => {
                // Убираем архив из пересчета
                if (list.name.toLowerCase() !== 'архив') {
                    list.position = index + 1;
                }
            });
        },


        // Удаляет задачу из текущего списка
        removeTaskFromList(taskId, listId) {
            // Проверяем, существует ли список с такими задачами
            if (!Array.isArray(this.tasks[listId])) {
                console.error(`Список с ID ${listId} не существует.`);
                return;
            }

            // Находим индекс задачи в списке
            const taskIndex = this.tasks[listId].findIndex(task => task.id === taskId);

            if (taskIndex !== -1) {
                // Если задача найдена, удаляем её из массива
                this.tasks[listId].splice(taskIndex, 1);
            } else {
                console.error(`Задача с ID ${taskId} не найдена в списке ${listId}.`);
            }
        },

        // Добавляет задачу в новый список
        addTaskToList(task, listId) {
            // Проверяем, является ли this.tasks[listId] массивом
            if (!Array.isArray(this.tasks[listId])) {
                this.$set(this.tasks, listId, []);  // Если нет, инициализируем как пустой массив
            }

            this.tasks[listId].push(task); // Добавляем задачу в массив
        },

        // Получаем ID следующего списка по позиции
        getNextListId(currentListId) {
            const sortedLists = this.sortListsByPosition();
            const currentIndex = sortedLists.findIndex(list => list.id === currentListId);
            return sortedLists[currentIndex + 1] ? sortedLists[currentIndex + 1].id : currentListId;
        },

        // Получаем ID предыдущего списка по позиции
        getPreviousListId(currentListId) {
            const sortedLists = this.sortListsByPosition();
            const currentIndex = sortedLists.findIndex(list => list.id === currentListId);
            return sortedLists[currentIndex - 1] ? sortedLists[currentIndex - 1].id : currentListId;
        },

        // Сортировка списков по позиции
        sortListsByPosition() {
            return this.lists.slice().sort((a, b) => a.position - b.position);
        },

        // Удаление списка с пересчетом позиций
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
                        this.$set(this, 'lists', [...this.lists]); // потенциально убрать
                        this.recalculatePositions();  // Пересчитываем позиции

                    }
                    this.closeEditListPopup();
                } catch (error) {
                    alert(error.message);
                }
            }
        },

        // Метод для добавления нового списка
        async addNewList() {
            if (!this.newListName.trim()) {
                alert("Введите имя списка");
                return;
            }

            // Проверка, не пытается ли пользователь создать список с именем "Архив"
            if (this.newListName.toLowerCase() === 'архив') {
                alert("Нельзя создать список с именем 'Архив'");
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

                const archiveIndex = this.lists.findIndex(list => list.name.toLowerCase() === 'архив');
                if (archiveIndex !== -1) {
                    this.lists.splice(archiveIndex, 0, newList);  // Вставляем перед архивом
                } else {
                    this.lists.push(newList); // Если архив не найден, добавляем в конец
                }

                this.recalculatePositions();  // Пересчитываем позиции
                this.closeCreateListPopup()
                this.newListName = '';

            } catch(error) {
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

        // ========================== СПИСКИ ==================================
        // ========================== ЗАДАЧИ ==================================
        // Метод для перемещения задачи
        async moveTask(taskId, currentListId, direction) {
            const task = this.findTaskById(taskId);
            if (!task) return;

            let newListId = currentListId;
            if (direction === 'forward') {
                newListId = this.getNextListId(currentListId);
            } else if (direction === 'back') {
                newListId = this.getPreviousListId(currentListId);
            }

            if (newListId !== currentListId) {
                // Удаляем задачу из старого списка
                this.removeTaskFromList(taskId, currentListId);
                // Добавляем задачу в новый список
                this.addTaskToList(task, newListId);

                // Сортируем задачи в новом списке по дедлайну и срочности
                this.sortTasksByDueDateAndUrgency(newListId);

                // Отправляем запрос на сервер для обновления только нужных данных задачи
                try {
                    const response = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${currentListId}/tasks/${taskId}/edit/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken(),
                        },
                        body: JSON.stringify({
                            status: newListId,       // Новый список
                            due_date: task.due_date  // Дедлайн задачи (оставляем без изменений)
                        })
                    });

                    if (!response.ok) {
                        throw new Error("Ошибка при перемещении задачи");
                    }
                } catch (error) {
                    alert(error.message);
                }
            }
        },

        // Находит задачу по ID
        findTaskById(taskId) {
            // Находим все задачи для текущего списка (если они существуют)
            for (let listId in this.tasks) {
                if (Array.isArray(this.tasks[listId])) {
                    const task = this.tasks[listId].find(task => task.id === taskId);
                    if (task) {
                        return task;
                    }
                }
            }
            // Если задача не найдена
            console.error(`Задача с ID ${taskId} не найдена.`);
            return null;
        },

        async getUsers() {
            try {
                const response = await fetch(`${this.baseUrl}/users/profiles`);
                const data = await response.json();
                this.availableUsers = data;
            } catch (error) {
                console.error('Ошибка при загрузке списка пользователей:', error);
            }
        },

        // Метод для добавления новой задачи в список
        async addNewTask(listId) {
             if (!this.newTaskTitle.trim()) {
                alert("Введите название задачи");
                return;
            }
            try {
                const taskData = {
                    title: this.newTaskTitle,
                    description: this.newTaskDescription,
                    due_date: this.newTaskDeadline,
                    assigned_to: this.newTaskAssignedTo,
                    status: this.newTaskStatus,
                    is_urgent: this.newTaskIsUrgent,
                };

                console.log(this.newTaskStatus)

                const response = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${this.newTaskStatus}/tasks/create`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify(taskData),
                });

                if (!response.ok) {
                    throw new Error("Ошибка при добавлении задачи");
                }

                const newTask = await response.json();
                console.log(newTask)
                // Проверяем, существует ли массив задач для текущего списка (this.newTaskList)
                if (!Array.isArray(this.tasks[this.newTaskStatus])) {
                    this.$set(this.tasks, this.newTaskStatus, []);  // Инициализируем массив, если его нет
                }

                // Добавляем новую задачу в массив задач для этого списка
                this.tasks[this.newTaskStatus].push(newTask);

                // После добавления новой задачи, сортируем задачи по дедлайну и срочности
                this.sortTasksByDueDateAndUrgency(this.newTaskStatus);


                this.closeAddTaskPopup();
                this.resetTaskForm(); // Очищаем форму
            } catch (error) {
                alert(error.message);
            }
        },
        // ========================== ЗАДАЧИ ==================================
        // ================================ ПОПАПЫ ==============================

        openAddTaskPopup(list_id) {
            const modal = new bootstrap.Modal(document.getElementById('addTaskModal'));
            this.newTaskStatus = list_id
            modal.show(); // Явно вызываем Bootstrap метод для открытия окна
        },

        closeAddTaskPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTaskModal'));
            modal.hide(); // Явно вызываем Bootstrap метод для открытия окна
        },


        closeCreateListPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('addTaskModal'));
            modal.hide(); // Явно вызываем Bootstrap метод для скрытия окна
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

        resetTaskForm() {
            this.newTaskTitle = "";
            this.newTaskDescription = "";
            this.newTaskDeadline = null;
            this.newTaskAssignedTo = null;
            this.newTaskStatus = '';
        },
    },
});