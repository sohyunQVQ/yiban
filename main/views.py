from django.shortcuts import render
from main.models import User
import yibanapi


# Create your views here.
def index(request):
    message = "请进行登录"
    if request.method == "POST":
        if request.POST['username']:
            username = request.POST['username']
            if request.POST['password']:
                password = request.POST['password']
                if request.POST['blogtext']:
                    blogtext = request.POST['blogtext']
                    if request.POST['pushtext']:
                        pushtext = request.POST['pushtext']
                        userid, logintoken, logintoken_accrss, name = yibanapi.loginYiban(username, password)
                        if name == False:
                            message="账号或密码错误"
                        else:
                            user = User(username=username, password=password,name=name,blogtext=blogtext,pushtext=pushtext)
                            user.save()
                            message="登录成功/并且已经保存, 将在每天8点运行"
                    else:
                        message = "易喵喵发帖为空"
                else:
                    message = "易班回复内容为空"
            else:
                message = "密码为空"
        else:
            message = "账号为空"
    return render(request, "index.html", {'message':message})

