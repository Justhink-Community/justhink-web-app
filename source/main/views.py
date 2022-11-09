from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test



NOTIFICATION_TAGS = {
    'success': 'checkmark-circle-outline',
    'error': 'close-circle-outline',
    'warning': 'alert-circle-outline',
    'info': 'information-circle-outline'
}

def IndexView(request):
    return render(request, "index.html")


@user_passes_test(lambda u: u.is_anonymous)
def LoginView(request):
    if request.POST:
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password) 

        if user is not None:     
            login(request, user)
            messages.success(request, f'Başarıyla giriş yaptın: {username}', extra_tags=NOTIFICATION_TAGS['success'])
        else: 
            messages.error(request, 'Bilgilerinde hata var, kontrol et!', extra_tags=NOTIFICATION_TAGS['error']) 

        return redirect('index-page')


@user_passes_test(lambda u: u.is_anonymous)
def RegisterView(request):
    if request.POST:
        try:
            kvkk_check =  request.POST['kvkk']
        except KeyError: 
            messages.error(request, 'Kayıt olmak için KVKK\'yı kabul etmelisin.', extra_tags=NOTIFICATION_TAGS['error'])
        else:
            username, password, email = request.POST['username'], request.POST['password'], request.POST['email']

            try:
                request.POST['emailperm']
            except KeyError:
                email_perm = False 
            else:
                email_perm = True 
            
            user = User.objects.create_user(username = username, password = password, email = email)

            if user is not None:
                login(request, user) 
                messages.success(request, 'Başarıyla hesabınızı oluşturdunuz.', extra_tags=NOTIFICATION_TAGS['success'])
            else: 
                messages.error(request, 'Hesabınız bizden kaynaklı bir sorundan ötürü oluşturulamadı. [#001]', extra_tags=NOTIFICATION_TAGS['error'])
        
        return redirect('index-page')


@user_passes_test(lambda u: not u.is_anonymous)
def LogoutView(request):
    messages.info(request, 'Hesabınızdan çıkış yaptınız.', extra_tags=NOTIFICATION_TAGS['info'])
    logout(request)
    
    return redirect('index-page')