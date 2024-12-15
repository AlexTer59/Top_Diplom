// Получаем CSRF токен
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

new Vue({
    el: '#task-comments',
    delimiters: ['[[', ']]'],
    data() {
        return {
            baseUrl: 'http://127.0.0.1:8000/',
            comments: [],   // Массив для хранения комментариев
            newCommentText: '',
            defaultAvatar: null,
            taskId: document.getElementById('app').getAttribute('data-task-id')  // Получаем taskId из атрибута элемента
        };
    },

    // Метод вызывается при монтировании компонента
    mounted() {
        this.fetchComments();  // Получаем комментарии при загрузке компонента
        this.defaultAvatar = document.getElementById('app').getAttribute('data-default-avatar')
    },

    methods: {
        async fetchComments() {
            try {
                const response = await fetch(`/api/tasks/${this.taskId}/comments/`);
                const data = await response.json();
                this.comments = data;  // Загружаем новые комментарии в массив
                console.log(this.comments)
            } catch (error) {
                console.error('Ошибка при загрузке комментариев:', error);
            }
        },

        // Метод для лайка комментария
        // Локальное обновление лайка
        async toggleLike(commentId) {
            const comment = this.comments.find(comment => comment.id === commentId);

            // Меняем состояние лайка
            const newLikeStatus = !comment.is_liked;  // Если был лайк, то убираем, если не был — ставим

            comment.is_liked = newLikeStatus;  // Обновляем локально

            // Обновляем количество лайков
            if (newLikeStatus) {
                comment.likes_count++;
            } else {
                comment.likes_count--;
            }

            try {
                // Отправляем обновление на сервер
                const response = await fetch(`/api/tasks/${this.taskId}/comments/${commentId}/like/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({ liked: newLikeStatus })  // Отправляем только новое состояние лайка
                });

                if (!response.ok) {
                    throw new Error("Ошибка при изменении лайка");
                }

                // Получаем обновленные данные для комментария, если это нужно
                const updatedComment = await response.json();
                // Обновляем комментарий с сервера, если нужно
                // this.updateCommentInList(updatedComment); // Если нужно

            } catch (error) {
                console.error(error.message);
                alert("Не удалось обновить лайк. Попробуйте еще раз.");
                // В случае ошибки, восстанавливаем старое состояние лайка
                comment.is_liked = !newLikeStatus;
                if (newLikeStatus) {
                    comment.likes_count--;
                } else {
                    comment.likes_count++;
                }
            }
        },

        // Метод для отправки нового комментария
        async submitComment() {
            // Проверка, что комментарий не пустой
            if (!this.newCommentText.trim()) {
                return;  // Если комментарий пустой, не отправляем запрос
            }

            try {
                const response = await fetch(`/api/tasks/${this.taskId}/comments/create`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),  // CSRF токен для безопасности
                    },
                    body: JSON.stringify({
                        task: this.taskId,
                        comment: this.newCommentText,  // Отправляем текст комментария
                    }),
                });

                if (!response.ok) {
                    throw new Error("Ошибка при добавлении комментария");
                }

                // Получаем новый комментарий с сервера
                const newComment = await response.json();

                this.comments.push(newComment)


                // Очистка поля ввода после успешной отправки
                this.newCommentText = '';


            } catch (error) {
                alert("Не удалось добавить комментарий. Попробуйте еще раз.");
                console.error(error.message);
            }
        },
    },


});