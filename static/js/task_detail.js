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
            boardMembers: [], // Участники доски
            newTaskTitle: "",
            newTaskDescription: "",
            newTaskAssignedTo: null,
            newTaskStatus: "",
            newTaskList: null,
            newTaskDeadline: null,
        };
    },
    mounted() {
        this.boardId = this.$el.getAttribute('data-board-id');
        this.listId = this.$el.getAttribute('data-list-id');
        this.taskId = this.$el.getAttribute('data-task-id');
        this.userId = this.$el.getAttribute('data-user-id');
        this.fetchData();
    },
    methods: {
        async fetchData() {

            if (!this.boardId || !this.listId || !this.taskId) {
                console.error('Отсутствует ID доски, списка или задачи!');
                return;
            }

            try {
                // Запрашиваем данные о задаче
                const taskResponse = await fetch(`${this.baseUrl}api/boards/${this.boardId}/lists/${this.listId}/tasks/${this.taskId}`);
                const taskData = await taskResponse.json();
                this.task = taskData;
                console.log(this.task)

                // Запрашиваем участников доски
                const boardMembersResponse = await fetch(`${this.baseUrl}users/profiles/boards/${this.boardId}/`);
                const membersData = await boardMembersResponse.json();
                this.boardMembers = membersData;

                //

            } catch (error) {
                console.error('Ошибка при загрузке данных:', error);
            }
        },

        async editTask(listId) {
            // Проверка на наличие данных
            if (!this.newTaskTitle.trim()) {
                alert("Введите название задачи");
                return;
            }

            try {
                // Формируем данные для отправки
                const taskData = {
                    title: this.newTaskTitle,
                    description: this.newTaskDescription,
                    due_date: this.newTaskDeadline,
                    assigned_to: this.newTaskAssignedTo,
                    status: this.newTaskStatus,
                };

                // Отправляем запрос на обновление задачи
                const response = await fetch(
                    `${this.baseUrl}api/boards/${this.boardId}/lists/${this.listId}/tasks/${this.taskId}/edit/`,
                    {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCsrfToken(),
                        },
                        body: JSON.stringify(taskData),
                    }
                );

                // Проверяем успешность запроса
                if (!response.ok) {
                    const errorDetails = await response.json();
                    console.error("Ошибка при обновлении задачи:", errorDetails);
                    throw new Error("Ошибка при обновлении задачи");
                }

                // Получаем обновленные данные задачи
                const updatedTask = await response.json();
                console.log("Обновленная задача:", updatedTask);

                // Обновляем текущую задачу в приложении
                Object.assign(this.task, updatedTask);

                // Закрываем форму редактирования и сбрасываем поля
                this.closeEditTaskPopup();
                this.resetTaskForm();
            } catch (error) {
                console.error("Ошибка:", error.message);
                alert("Не удалось обновить задачу. Попробуйте еще раз.");
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

                    // Редирект на страницу со списком задач или другую страницу
                    window.location.href = `${this.baseUrl}boards/${this.boardId}/`; // пример редиректа

                } catch (error) {
                    console.error(error.message);
                    alert("Не удалось удалить задачу. Попробуйте еще раз.");
                }
            }
        },

        backToBoard() {
            window.location.href = `${this.baseUrl}boards/${this.boardId}/`; // пример редиректа
        },

        resetTaskForm() {
            this.newTaskTitle = "";
            this.newTaskDescription = "";
            this.newTaskAssignedTo = null;
            this.newTaskStatus = "";
            this.newTaskList = null;
            this.newTaskDeadline = null;
        },

        openEditTaskPopup(list) {
            const modal = new bootstrap.Modal(document.getElementById('editTaskModal'));
            this.newTaskTitle = this.task.title;
            this.newTaskDescription = this.task.description;
            this.newTaskDeadline = this.task.due_date;
            this.newTaskAssignedTo = this.task.assigned_to
            this.newTaskStatus = this.task.status;
            modal.show(); // Явно вызываем Bootstrap метод для открытия окна
        },

        closeEditTaskPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('editTaskModal'));
            modal.hide(); // Явно вызываем Bootstrap метод для открытия окна
        },
    },
});
