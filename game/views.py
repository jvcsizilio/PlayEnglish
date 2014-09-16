# encoding: utf8
from django.shortcuts import render
from models import Player, Sentence, Language
from django.contrib.auth.forms import UserCreationForm
import random


def home(request, dados={}):
    player = Player.objects.get(user=request.user)
    dados['list_words'] = player.sentences_unlocked.all()
    dados['player'] = player
    return render(request, 'home.html', dados)


def register(request):
    form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def confirm_register(request):
    dados = {}

    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        user.is_staff = True
        user.save()
        new_player(user)
        dados['message'] =\
            u'Welcome {nome}'.format(nome=user.username)
        return render(request, 'register.html', dados)
    else:
        dados = {}
        dados['form'] = form
        return render(request, 'register.html', {'form': form})


def get_new_sentence(request):
    dados = {}
    player = Player.objects.get(user=request.user)

    if player.can_new_sentence > 0:
        player.add_sentence
        dados['message'] = 'Palavra adicionada'
    else:
        dados['message'] = 'Jogue um pouco mais'
    return home(request, dados)


def play(request, dados={}):
    request.session['last_words'] = []
    player = Player.objects.get(user=request.user)
    dados['player'] = player
    dados['option'] = random.choice(
        player.sentences_unlocked.all())
    return render(request, 'play.html', dados)


def correct(request, id):
    dados = {}

    player = Player.objects.get(user=request.user)
    sentence = Sentence.objects.get(id=id)

    list_words = request.session.get('list_words')
    if list_words is not None:
        list_words.append(sentence.get_sentence)
    else:
        list_words = []
        list_words.append(sentence.get_sentence)
        request.session['list_words'] = list_words

    dados['list_words'] = list_words[-5:]

    answer = request.POST.get('answer').strip()
    if answer.lower() in \
            sentence.translate_text.lower().replace(',', ' ').split():
        player.add_point
        dados['status'] = True
    else:
        player.remove_point
        dados['status'] = False

    return play(request, dados)


def gera_nova_lista(request):
    f = open('list_words.txt', 'r')
    string = ''
    lang = Language.objects.get(id=1)
    for i in f.readlines():
        string = i.split()
        sent = Sentence(
            language=lang, original_text=string[1],
            translate_text=string[3], level=1)
        sent.save()


def new_player(user):
    player = Player(
        user=user, level=1, points=10)
    player.save()
    player.add_sentence
    player.add_sentence
    player.add_sentence
