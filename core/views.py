from django.shortcuts import render

def main(request):
    return render(request, 'main.html')

def board(request):
    return render(request, 'board.html')

def login(request):
    return render(request, 'login.html')