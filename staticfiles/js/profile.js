// Получаем CSRF токен
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data() {
        return {
            baseUrl: 'http://127.0.0.1:8000/',
            profile: {}, // Данные профиля
            editForm: {
                first_name: '',
                last_name: '',
                bio: '',
                birth_date: '',
                avatar: null, // Поле для загрузки файла
            },
        };
    },

    mounted() {
        this.profileId = this.$el.getAttribute('data-profile-id');
        this.fetchProfileData();
    },

    methods: {
        async fetchProfileData() {
            if (!this.profileId) {
                console.error('Отсутствует ID профиля!');
                return;
            }

            // Подгружаем данные профиля
            try {
                const response = await fetch(`${this.baseUrl}users/profiles/${this.profileId}/api/`);
                this.profile = await response.json();
            } catch (error) {
                alert(error.message)
                console.error('Ошибка загрузки профиля:', error);
            }
        },

        handleAvatarUpload(event) {
            // Обработка загрузки аватара
            const file = event.target.files[0];
            if (file) {
                this.editForm.avatar = file;
            } else {
                this.editForm.avatar = null;
            }
        },


        async submitProfileUpdate() {
            // Отправляем изменения на сервер
            try {
                const formData = new FormData();
                Object.keys(this.editForm).forEach((key) => {
                    if (this.editForm[key] !== this.profile[key]) { // Сравниваем с исходными данными
                        if (key === 'avatar' && this.editForm[key] === null) {
                            // Пропускаем, если avatar равен null
                            return;
                        }
                        formData.append(key, this.editForm[key]);
                    }
                });
                const response = await fetch(`${this.baseUrl}users/profiles/${this.profileId}/api/edit/`, {
                    method: 'PUT',
                    headers: {
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: formData,
                });

                if (response.ok) {
                    const updatedProfile = await response.json()
                    this.profile = updatedProfile; // Обновляем профиль

                    // Добавляем уникальный параметр к URL аватарки
                    if (this.profile.avatar) {
                        this.profile.avatar += `?t=${new Date().getTime()}`;
                    }

                    this.closeEditProfilePopup();


                } else {
                    throw new Error("Ошибка при обновлении профиля!");
                    console.error('Ошибка обновления профиля:', await response.json());
                }
            } catch (error) {
                alert(error.message)
            }
        },

        openEditProfilePopup() {
            const modal = new bootstrap.Modal(document.getElementById('editProfileModal'));
            this.editForm = { ...this.profile }; // Копируем данные профиля в форму
            modal.show();
        },

        closeEditProfilePopup() {
            const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
            modal.hide();
        },

        formatDate(isoDate) {
        if (!isoDate) return '-'; // Если дата отсутствует
        const date = new Date(isoDate);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        });
    },

    },
});

