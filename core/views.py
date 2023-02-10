from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random

# Create your views here.

@login_required(login_url='signin')
def index(request):
    # crie uma lista vazia para armazenar os objetos de usuário que o usuário atual está seguindo
    user_following_list = []

    # percorre a lista de objetos Seguir para o usuário atual
    for users in user_following:
        # anexe o objeto de usuário associado a cada objeto Seguir à lista user_following_list
        user_following_list.append(users.user)

    # cria uma lista vazia para armazenar os objetos Post para o feed do usuário atual
    feed = []

    # percorrer a user_following_list
    for usernames in user_following_list:
        # obtenha todos os objetos Post associados a cada nome de usuário na lista user_following_list
        feed_lists = Post.objects.filter(user=usernames)
        # anexar cada lista de objetos Post à lista de feeds
        feed.append(feed_lists)

    # nivela a lista de listas em uma única lista de objetos Post para o feed do usuário atual
    feed_list = list(chain(*feed))

    # criar uma lista de todos os objetos User no banco de dados
    all_users = User.objects.all()
    # crie uma lista vazia para armazenar os objetos User que o usuário atual está seguindo
    user_following_all = []

    # percorre a lista de objetos Seguir para o usuário atual
    for user in user_following:
        # obtenha o objeto User associado a cada objeto Follow
        user_list = User.objects.get(username=user.user)
        # anexar cada objeto User à lista user_following_all
        user_following_all.append(user_list)

    # criar uma lista de objetos User que o usuário atual não está seguindo
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]

    # obter o objeto User do usuário atual
    current_user = User.objects.filter(username=request.user.username)

    # remova o objeto User do usuário atual da new_suggestions_list
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]

    # embaralhe a final_suggestions_list
    random.shuffle(final_suggestions_list)

    # crie uma lista vazia para armazenar os IDs de perfil associados aos usuários sugeridos
    username_profile = []
    # crie uma lista vazia para armazenar os objetos de Perfil associados aos usuários sugeridos
    username_profile_list = []

    # percorrer o final_suggestions_list
    for users in final_suggestions_list:
        # anexe o id de cada objeto User à lista username_profile
        username_profile.append(users.id)

    # percorrer a lista username_profile
    for ids in username_profile:
        # obtenha o objeto Perfil associado a cada id
        profile_lists = Profile.objects.filter(id_user=ids)
        # anexe cada objeto de perfil à lista_de_perfil_do_usuário
        username_profile_list.append(profile_lists)

    # nivelar a lista de listas em uma única lista de objetos de Perfil para os usuários sugeridos
    suggestions_username_profile_list = list(chain(*username_profile_list))

    # renderiza o modelo de índice, passando user_profile, feed_list e os 4 primeiros perfis sugeridos como contexto
    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
    # obtenha o nome de usuário do usuário que está fazendo a solicitação
    user = request.user.username

    # obtenha a imagem carregada da solicitação
    image = request.FILES.get('image_upload')

    # pegue a legenda da imagem
    caption = request.POST['caption']

    # crie um novo objeto Post com o usuário, imagem e legenda fornecidos
    new_post = Post.objects.create(user=user, image=image, caption=caption)

    # salvar a nova postagem no banco de dados
    new_post.save()

    # redirecionar o usuário de volta para a página inicial
    return redirect('/')
else:
    # se o método de solicitação não for POST, redirecione o usuário de volta para a página inicial
    return redirect('/')

#funçaõ de procurar usuario
@login_required(login_url='signin')
def search(request):
    # Obtém o objeto de usuário atual a partir do nome de usuário no objeto request
    user_object = User.objects.get(username=request.user.username)

    # Obtém o perfil do usuário atual a partir do objeto de usuário
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        # Armazena o nome de usuário inserido no formulário em uma variável
        username = request.POST['username']

        # Filtra os objetos de usuário com nomes de usuário semelhantes ao inserido
        username_object = User.objects.filter(username__icontains=username)

        # Cria listas vazias para armazenar os perfis de usuário correspondentes
        username_profile = []
        username_profile_list = []

        # Loop através dos objetos de usuário filtrados
        for users in username_object:
            # Adiciona o ID do usuário a uma lista
            username_profile.append(users.id)

        # Loop através dos IDs de usuário
        for ids in username_profile:
            # Filtra os perfis de usuário com IDs de usuários correspondentes
            profile_lists = Profile.objects.filter(id_user=ids)
            # Adiciona os perfis de usuário à lista de perfis de usuário
            username_profile_list.append(profile_lists)
        
        # Converte a lista de listas de perfis de usuário em uma única lista de perfis de usuário
        username_profile_list = list(chain(*username_profile_list))

    # Renderiza a página de pesquisa com as informações do perfil do usuário atual e a lista de perfis de usuário correspondidos
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})

#função like_post 
@login_required(login_url='signin')
def like_post(request):
    # Obtém o nome de usuário do usuário atual a partir do objeto request
    username = request.user.username

    # Obtém o ID do post a partir da solicitação GET
    post_id = request.GET.get('post_id')

    # Obtém o objeto de post correspondente ao ID de post
    post = Post.objects.get(id=post_id)

    # Filtra o primeiro registro de "LikePost" com o ID de post e o nome de usuário correspondentes
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        # Cria um novo registro de "LikePost" com o ID de post e o nome de usuário
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        # Salva o novo registro
        new_like.save()
        # Incrementa o número de curtidas no objeto de post
        post.no_of_likes = post.no_of_likes + 1
        # Salva as alterações no objeto de post
        post.save()
        # Redireciona para a página principal
        return redirect('/')
    else:
        # Exclui o registro de "LikePost" correspondente
        like_filter.delete()
        # Decrementa o número de curtidas no objeto de post
        post.no_of_likes = post.no_of_likes - 1
        # Salva as alterações no objeto de post
        post.save()
        # Redireciona para a página principal
        return redirect('/')

#função profile para retornar os dados de perfil 
@login_required(login_url='signin')
def profile(request, pk):
    # Obtém o objeto de usuário correspondente ao nome de usuário especificado
    user_object = User.objects.get(username=pk)

    # Obtém o perfil do usuário correspondente ao objeto de usuário
    user_profile = Profile.objects.get(user=user_object)

    # Filtra os posts de usuário correspondentes ao nome de usuário especificado
    user_posts = Post.objects.filter(user=pk)

    # Conta o número de posts de usuário
    user_post_length = len(user_posts)

    # Obtém o nome de usuário do usuário que está visualizando o perfil
    follower = request.user.username

    # Armazena o nome de usuário do usuário cujo perfil está sendo visualizado
    user = pk

    # Verifica se o usuário que está visualizando o perfil segue o usuário cujo perfil está sendo visualizado
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        # Se o usuário segue o usuário cujo perfil está sendo visualizado, o texto do botão é "Unfollow"
        button_text = 'Unfollow'
    else:
        # Se o usuário não segue o usuário cujo perfil está sendo visualizado, o texto do botão é "Follow"
        button_text = 'Follow'

    # Conta o número de seguidores do usuário cujo perfil está sendo visualizado
    user_followers = len(FollowersCount.objects.filter(user=pk))

    # Conta o número de usuários que o usuário cujo perfil está sendo visualizado está seguindo
    user_following = len(FollowersCount.objects.filter(follower=pk))

    # Cria o contexto de renderização
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    # Renderiza a página de perfil com o contexto
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        #caso já esteja seguindo o codigo ira deletar a relação de seguidor e seguido 
        #caso contrario ira adicionar os dois usuarios como seguidor e seguido
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

#codigo de configurações para o usuario personalizar o seu perfil
@login_required(login_url='signin')
def settings(request):
    # Recupera o perfil do usuário atual
    user_profile = Profile.objects.get(user=request.user)

    # Verifica se a requisição é do tipo POST
    if request.method == 'POST':
        # Verifica se a imagem foi enviada
        if request.FILES.get('image') == None:
            # Caso não tenha sido enviada, a imagem antiga é mantida
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            # Atualiza o perfil do usuário com as novas informações
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        # Caso tenha sido enviada uma nova imagem
        if request.FILES.get('image') != None:
            # Recupera a nova imagem
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            # Atualiza o perfil do usuário com as novas informações
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        # Redireciona para a página de configurações
        return redirect('settings')
    # Renderiza a página de configurações com as informações do perfil do usuário
    return render(request, 'setting.html', {'user_profile': user_profile})

#codigo de signup para cadastrar novos usuarios
def signup(request):
    # Verifica se a requisição é do tipo POST
    if request.method == 'POST':
        # Recupera as informações do formulário
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Verifica se as duas senhas são iguais
        if password == password2:
            # Verifica se já existe um usuário com o mesmo email
            if User.objects.filter(email=email).exists():
                # Exibe uma mensagem informando que o email já está sendo usado
                messages.info(request, 'Email Taken')
                return redirect('signup')

            # Verifica se já existe um usuário com o mesmo nome de usuário
            elif User.objects.filter(username=username).exists():
                # Exibe uma mensagem informando que o nome de usuário já está sendo usado
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                # Cria um novo usuário
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Efetua o login do usuário e redireciona para a página de configurações
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # Cria um novo perfil para o usuário
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            # Exibe uma mensagem informando que as senhas não são iguais
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    # Renderiza a página de cadastro
    else:
        return render(request, 'signup.html')
    

#codigo de signin de autenticação do usuario 
def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

