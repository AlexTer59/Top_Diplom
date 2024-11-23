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
        hoverDelete: null, // Для плавного изменения иконки корзины
    },
    mounted() {
        // Загрузка данных о досках при монтировании компонента
        this.getBoards();
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

        // Метод для удаления доски
        async deleteBoard(boardId) {
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

                // Удаляем доску из ownedBoards после успешного запроса
                this.ownedBoards = this.ownedBoards.filter(board => board.id !== boardId);

                console.log(`Доска с ID ${boardId} успешно удалена`);
            } catch (error) {
                console.error('Ошибка при удалении доски:', error);
                alert('Не удалось удалить доску. Попробуйте снова.');
            }
    },

//         Метод для открытия формы создания доски
        openCreateBoard() {
            window.location.href = `${this.baseUrl}create-board/`; // Перенаправление на страницу для создания доски
        }
    }
});