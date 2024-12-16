// Получаем CSRF токен
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

new Vue({
    el: '#app', // Привязываем Vue к элементу с id="app"
    delimiters: ['[[', ']]'], // Устанавливаем разделители
    data() {
        return {
            baseUrl: 'http://127.0.0.1:8000/',
            task: {},
            board: {}, // Данные о доске
            lists: [],  // Массив для списков
            boardMembers: [], // Участники доски

            defaultAvatar: null,
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
        this.boardId = this.$el.getAttribute('data-board-id');
        this.listId = this.$el.getAttribute('data-list-id');
        this.taskId = this.$el.getAttribute('data-task-id');
        this.userId = this.$el.getAttribute('data-user-id');
        this.defaultAvatar = this.$el.getAttribute('data-default-avatar');
        this.fetchData();
    },

    methods: {
        async fetchData() {

            if (!this.boardId || !this.listId || !this.taskId) {
                console.error('Отсутствует ID доски, списка или задачи!');
                return;
            }

            try {
                // Запрашиваем данные о доске
                const boardResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/`);
                const boardData = await boardResponse.json();
                this.board = boardData; // Сохраняем данные о доске
                this.isOwner = this.board.owner == this.$el.getAttribute('data-user-id'); // Проверяем, является ли текущий пользователь владельцем

                // Запрашиваем данные о задаче
                const taskResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${this.listId}/tasks/${this.taskId}`);
                const taskData = await taskResponse.json();
                this.task = taskData;

                // Запрашиваем участников доски
                const boardMembersResponse = await fetch(`${this.baseUrl}users/profiles/boards/${this.boardId}/`);
                const membersData = await boardMembersResponse.json();
                this.boardMembers = membersData;

                // Запрашиваем все списки для этой доски
                const listsResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/`);
                const listsData = await listsResponse.json();
                this.lists = listsData; // Сохраняем списки

            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        },

        // Проверка, может ли текущий пользователь редактировать задачу
        canEditTask() {
            if (!this.task || !this.userId) {
                return false;  // Если данные не загружены, не разрешаем редактирование
            }

            return this.isOwner || this.task.created_by_id == this.userId;
        },

        // Проверка, может ли текущий пользователь изменить только статус задачи
        canMoveTask() {
            if (!this.task || !this.userId) {
                return false;  // Если данные не загружены, не разрешаем перемещение
            }
            return this.task.assigned_to == this.userId;
        },

        async editTask(popupId) {
            if (!this.newTaskTitle.trim()) {
                alert("Введите название задачи");
                return;
            }

            if (!this.newTaskAssignedTo) {
                alert("Пожалуйста, выберите исполнителя.");
                return;
            }

            try {
                // Подготовка данных для обновления задачи
                const updatedTaskData = {
                    title: this.newTaskTitle,
                    description: this.newTaskDescription,
                    due_date: this.newTaskDeadline,
                    assigned_to: this.newTaskAssignedTo,
                    is_urgent: this.newTaskIsUrgent,
                    status: this.newTaskStatus  // Новый статус
                };

                // Проверка на просроченность задачи
                const currentDate = new Date();
                const isOverdue = new Date(this.newTaskDeadline) < currentDate;
                updatedTaskData.is_overdue = isOverdue; // Если дата в прошлом, устанавливаем is_overdue в true, иначе false

                const response = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${this.task.status}/tasks/${this.task.id}/edit/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify(updatedTaskData),
                });

                if (!response.ok) {
                    throw new Error("Ошибка при обновлении задачи");
                }

                const updatedTask = await response.json();

                // Обновляем текущую задачу в приложении
                Object.assign(this.task, updatedTask);

                // Закрытие модального окна
                this.closeEditTaskPopup(popupId);
            } catch (error) {
                alert(error.message);
            }
        },

        async deleteTask() {
            if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
                try {
                    // Отправляем запрос на сервер для удаления задачи
                    const response = await fetch(
                        `${this.baseUrl}api/boards/${this.boardId}/lists/${this.listId}/tasks/${this.taskId}/delete/`,
                        {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken(),
                            },
                        }
                    );

                    if (!response.ok) {
                        const errorDetails = await response.json();
                        console.error("Ошибка при удалении задачи:", errorDetails);
                        throw new Error('Ошибка при удалении задачи');
                    }

                    // Редирект на страницу со списком задач
                    this.backToBoard();

                } catch (error) {
                    console.error(error.message);
                    alert("Не удалось удалить задачу. Попробуйте еще раз.");
                }
            }
        },

        backToBoard() {
            window.location.href = `${this.baseUrl}boards/${this.boardId}/`;
        },

        resetTaskForm() {
            this.newTaskTitle = "";
            this.newTaskDescription = "";
            this.newTaskAssignedTo = null;
            this.newTaskStatus = null;
            this.newTaskDeadline = null;
            this.newTaskIsUrgent = false;
        },

        openEditTaskPopup(popupId) {
            this.newTaskTitle = this.task.title;
            this.newTaskDescription = this.task.description;
            const [day, month, year] = this.task.due_date.split('-');
            this.newTaskDeadline = `${year}-${month}-${day}`;
            this.newTaskStatus = this.task.status;  // Статус задачи, устанавливаем ID списка
            this.newTaskAssignedTo = this.task.assigned_to;
            this.newTaskIsUrgent = this.task.is_urgent;
            const modal = new bootstrap.Modal(document.getElementById(popupId));
            modal.show();
        },


        closeEditTaskPopup(popupId) {
            const modal = bootstrap.Modal.getInstance(document.getElementById(popupId));
            modal.hide();
            this.resetTaskForm();
        },



    },
});
