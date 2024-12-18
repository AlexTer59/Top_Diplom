function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        baseUrl: 'http://127.0.0.1:8000/', // Базовый URL, который можно легко изменить
        ownedBoards: [],
        sharedBoards: [],
        newBoardName: '',
        newBoardDescription: '',
        selectedUsers: [],
        availableUsers: [],
        editBoardId: null,
        isBaseSubscription: null,
        isBoardLimitReached: false,
        maxMembers: 50,
    },
    mounted() {
        // Загрузка данных о досках при монтировании компонента
        this.checkSubscription();
        this.getBoards();
        this.getUsers();
    },

    watch: {
        // Следим за изменениями в selectedUsers
        selectedUsers(newValue, oldValue) {
            if (newValue.length > this.maxMembers) {
                this.selectedUsers = newValue.slice(0, this.maxMembers);
                alert(`Вы можете выбрать не более ${this.maxMembers} участников.`);
            }
        },
    },

    methods: {
        async getBoards() {
            try {
                const responseOwned = await fetch(`${this.baseUrl}api/boards/owned/`);
                const dataOwned = await responseOwned.json();
                this.ownedBoards = dataOwned;

                const responseShared = await fetch(`${this.baseUrl}api/boards/shared/`);
                const dataShared = await responseShared.json();
                this.sharedBoards = dataShared;
            } catch (error) {
                console.error('Ошибка при загрузке досок:', error);
            }
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

        async checkSubscription() {
            try {
                const response = await fetch(`${this.baseUrl}users/profiles/subscription/get/api/`);
                const subscription = await response.json();

                if (subscription.tier === 'base') {
                    this.isBaseSubscription = true;
                    this.maxMembers = 3;
                } else {
                    this.isBaseSubscription = false;
                }

                this.checkBoardLimit()

            } catch (error) {
                console.error('Ошибка при проверке подписки:', error);
            }
        },

        checkBoardLimit() {
            if (this.isBaseSubscription) {
                this.isBoardLimitReached = this.ownedBoards.length >= 3;
            } else {
                this.isBoardLimitReached = false;
            }
        },

        checkUserLimit() {
            console.log('проверяю')
            if (this.selectedUsers.length > this.maxMembers) {
                // Если количество выбранных пользователей больше лимита, удаляем последний выбранный
                this.selectedUsers = this.selectedUsers.slice(0, this.maxMembers);
                alert(`Вы можете выбрать не более ${this.maxMembers} участников.`);
            }
        },

        async createBoard() {
             if (this.isBoardLimitReached) {
                // Если лимит достигнут, не позволяем создавать доску
                return;
            }

            if (!this.newBoardName.trim()) {
                alert('Введите название доски');
                return;
            }

            try {
                const response = await fetch(`${this.baseUrl}api/boards/create/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({
                        name: this.newBoardName,
                        description: this.newBoardDescription,
                        members: this.selectedUsers,
                    }),
                });

                if (!response.ok) {
                    throw new Error('Ошибка при создании доски');
                }

                const newBoard = await response.json();
                this.ownedBoards.push(newBoard); // Добавляем новую доску в список

                this.checkBoardLimit();

                this.closeCreateBoardPopup(); // Закрываем модальное окно
                this.resetBoardPopup();  // Очищаем модальное окно
            } catch (error) {
                alert(error.message);
            }
        },


        // Метод для удаления доски
        async deleteBoard(boardId) {
            if (this.editBoardId) {
                boardId = this.editBoardId;
            }

            if (confirm('Вы уверены, что хотите удалить эту доску?')) {
                try {
                    const response = await fetch(`${this.baseUrl}api/boards/${boardId}/delete/`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken(), // CSRF-токен для защиты
                        },
                    });

                    if (!response.ok) {
                        throw new Error(`Ошибка удаления: ${response.status}`);
                    }
                    const index = this.ownedBoards.findIndex(board => board.id === boardId);
                    console.log(index)
                    if (index != -1) {
                        // Удаляем доску из ownedBoards после успешного запроса
                        this.ownedBoards = this.ownedBoards.filter(board => board.id !== boardId);
                         if (this.ownedBoards.length === 0) {
                            this.$set(this, 'ownedBoards', []);
                         }
                    }

                    this.checkBoardLimit();

                    if (this.editBoardId) {
                        this.closeEditBoardPopup()
                    } else {
                        this.editBoardId = null;
                    }

                } catch (error) {
                    console.error('Ошибка при удалении доски:', error);
                    alert('Не удалось удалить доску. Попробуйте снова.');
                }
            }
        },

        async editBoard() {
            if (!this.newBoardName.trim()) {
                alert('Введите имя доски');
                return;
            }

            try {
                const response = await fetch(`${this.baseUrl}api/boards/${this.editBoardId}/edit/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({
                        name: this.newBoardName,
                        description: this.newBoardDescription,
                        members: this.selectedUsers,
                    }),
                });
                if (!response.ok) {
                    throw new Error('Ошибка при обновлении доски');
                }
                const updatedBoard = await response.json();
                const index = this.ownedBoards.findIndex(list => list.id === updatedBoard.id);
                if (index !== -1) {
                    // Обновляем список в массиве с использованием this.$set
                    this.$set(this.ownedBoards, index, updatedBoard);
                }

                this.closeEditBoardPopup();
                this.resetBoardPopup();


            } catch (error) {
                alert(error.message);
            }
        },

        openEditBoardPopup(board) {
            const modal = new bootstrap.Modal(document.getElementById('editBoardModal'));
            this.newBoardName = board.name;
            this.newBoardDescription = board.description;
            this.editBoardId = board.id;
            this.selectedUsers = board.members;

            modal.show(); // Явно вызываем Bootstrap метод для открытия окна
        },

        openCreateBoardPopup(board) {
            const modal = new bootstrap.Modal(document.getElementById('createBoardModal'));
            console.log(this.maxMembers)
            modal.show(); // Явно вызываем Bootstrap метод для открытия окна
        },

        closeCreateBoardPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createBoardModal'));

            modal.hide(); // Явно вызываем Bootstrap метод для скрытия окна
            this.resetBoardPopup();
        },

         resetBoardPopup() {
            this.newBoardName = '';
            this.newBoardDescription = '';
            this.editBoardId = null;
            this.selectedUsers = [];
         },

        closeEditBoardPopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('editBoardModal'));
            modal.hide(); // Явно вызываем Bootstrap метод для скрытия окна
            this.resetBoardPopup();
        },

        //         Метод для открытия формы создания доски
        openCreateBoard() {
            window.location.href = `${this.baseUrl}create-board/`; // Перенаправление на страницу для создания доски
        },
    },

});