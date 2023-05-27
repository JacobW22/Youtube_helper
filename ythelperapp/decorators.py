from django.http import HttpResponse
from django.shortcuts import redirect

def login_check(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            logged = True
            return view_func(request, {'logged': logged, 'username': request.user.username} , *args, **kwargs)
        else:
            logged = False
            return view_func(request, {'logged': logged} , *args, **kwargs)
    
    return wrapper_func


def not_authenticated_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main_page')
        else:
            return view_func(request, *args, **kwargs)
        
    return wrapper_func