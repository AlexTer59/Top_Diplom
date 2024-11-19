from django.contrib import admin
from django import forms
from .models import *

admin.site.register(Board)
admin.site.register(List)
admin.site.register(Task)

# Кастомная форма для админки

# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # Фильтруем списки и участников по выбранной доске
#         if 'board' in self.data:  # Если доска выбрана в форме (данные переданы через POST)
#             try:
#                 board_id = int(self.data.get('board'))
#                 board = Board.objects.get(id=board_id)
#                 self.fields['list'].queryset = board.lists.all()
#                 self.fields['assigned_to'].queryset = board.members.all()
#             except (ValueError, Board.DoesNotExist):
#                 self.fields['list'].queryset = List.objects.none()
#                 self.fields['assigned_to'].queryset = Profile.objects.none()
#         elif (self.instance and hasattr(self.instance,'board')
#               and self.instance.board):  # Если редактируется существующая задача
#             board = self.instance.board
#             self.fields['list'].queryset = board.lists.all()
#             self.fields['assigned_to'].queryset = board.members.all()
#         else:  # Если ни один из случаев не подошел
#             self.fields['list'].queryset = List.objects.none()
#             self.fields['assigned_to'].queryset = Profile.objects.none()
#
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     form = TaskForm
#
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#
#         if not obj:  # Если создается новая задача
#             # Получаем доски, к которым пользователь имеет доступ
#             user_boards = request.user.profile.shared_boards.all()
#             owner_boards = Board.objects.filter(owner=request.user.profile)
#             # Объединяем доски, к которым пользователь имеет доступ, и доски, где он является создателем
#             all_boards = user_boards | owner_boards
#             # Для каждой доски получаем все связанные с ней списки
#             lists = List.objects.filter(board__in=all_boards)
#             form.base_fields['list'].queryset = lists  # Отображаем все доступные списки
#
#         return form