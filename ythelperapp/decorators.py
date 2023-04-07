from django.http import HttpResponse
from django.shortcuts import redirect

def login_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            logged = True
            username = request.user.username
            return view_func(request, {'logged': logged, 'username': username}, *args, **kwargs)
        else:
            logged = False
            return view_func(request, {'logged': logged, 'username' : 'none'}, *args, **kwargs)
    
    return wrapper_func

def not_authenticated(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main_page')
        else:
            return view_func(request, *args, **kwargs)
        
    return wrapper_func