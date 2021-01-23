from django.urls import path,include
from . import views

urlpatterns=[
    path("",views.index,name="index"),
    path("account/login",views.login,name="login"),
    path("account/register",views.register,name="register"),
    path("account/dashboard",views.dashboard,name="dashboard"),
    path("account/processdata",views.processdata,name="processdata"),
     path("jointest",views.jointest,name="jointest"),
     path("starttest",views.starttest,name="starttest"),
      path("submittest",views.submittest,name="submittest"),
      path("thankyou",views.thankyou,name="thankyou"),
    path("account/logout",views.logout,name="logout"),
    path("account/deltest/<int:test_id>",views.delete_test,name="delete_test"),
    path("account/mytest/<int:test_id>",views.testdetails,name="testdetails")
]
