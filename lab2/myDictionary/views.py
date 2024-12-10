# words/views.py

from django.shortcuts import render, redirect
from .utils import add_to_file, read_from_file


def home(request):
    return render(request, 'home.html')


def words_list(request):
    words1, words2 = read_from_file()
    words = list(zip(words1, words2))
    return render(request, 'words_list.html', {"words": words})


def add_word(request):
    if request.method == 'POST':
        word1 = request.POST.get('word1')
        word2 = request.POST.get('word2')
        add_to_file(word1, word2)
        return redirect('home')

    return render(request, 'add_word.html')