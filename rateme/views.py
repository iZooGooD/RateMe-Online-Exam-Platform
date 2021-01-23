from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from rateme.models import Tests,Question,UserMapper,Submission
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
import datetime
import json
import csv
# Create your views here.

def index(request):
    return render(request,'rateme/index.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            messages.success(request,'You are now logged in')
            return redirect('dashboard')
        else:
            messages.error(request,"Invalid credentials")
            return redirect('login')
    return render(request,'rateme/login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method=='POST':
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        username=request.POST['username']
        password=request.POST['password']
        cpassword=request.POST['cpassword']

        if password==cpassword:
            #check username
            if User.objects.filter(username=username).exists():
                messages.error(request,"That username is already taken")
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request,"Email with that account already exists")
                    return redirect('register')
                else:
                    user=User.objects.create_user(username=username,password=password,email=email,first_name=fname,last_name=lname)
                    user.save()
                    messages.success(request,'You are now registered, go ahead and login.')
                    return redirect(register)
        else:
            messages.error(request,"Password do not match with confirm password")
            return redirect('register')
    else:
        return render(request, 'rateme/signup.html')

def dashboard(request):
    if request.user.is_authenticated: 
        tests=Tests.objects.raw("select t.test_name,t.total_time,t.total_question,t.test_password,t.id,count(m.id) as total_submissions from rateme_tests as t left join rateme_usermapper as m on t.id=m.test_id_id where t.user_id_id=%s",[request.user.id])
        context={}
        error={'error_code':0}
        context['tests']=tests
        try:
            print("-----------in try block")
            print(tests[0].test_name)
            if tests[0].test_name==None:
                error['error_code']=1
        except:
            print("Changed the status of error to 1")
            error['error_code']=1
            
        context['error']=error
        return render(request,'rateme/dashboard.html',context)
    return redirect('login')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request,"You are now logged out")
        return redirect('login')


# reading the csv file using form data
def processdata(request):
    if request.method == 'POST' and request.FILES['mycsvfile']:
        #reading post data 
        test_name=request.POST['test_name']
        
        test_category=request.POST['test_category']
        test_time=request.POST['test_time']
        test_password=request.POST['test_password']
        

        #saving questions and choices from csv
        myfile = request.FILES['mycsvfile']
        decoded_file = myfile.read().decode('utf-8-sig').splitlines()
        reader=csv.reader(decoded_file)
        data=list(reader)
        #for row in data:
            

        #saving the test data
        userid=User.objects.get(username=request.user.username)
   
        entry=Tests(user_id=userid,test_name=test_name,total_question=len(data),total_time=test_time,test_category=test_category,test_password=test_password)
        entry.save()

        ##getting the last inserted test id 
        curr_test_id=Tests.objects.filter(user_id_id=userid).last()
      

        ##inserting questions and choice for that test id
        for row in data:
            question=row[0]
            choice1=row[1]
            choice2=row[2]
            choice3=row[3]
            choice4=row[4]
            correct_choice=row[5]
            question_entry=Question(test_id=curr_test_id,question_name=question,choice_1=choice1,choice_2=choice2,choice_3=choice3,choice_4=choice4,correct_choice=correct_choice)
            question_entry.save()        
  

    return redirect('dashboard')



def jointest(request):

    return render(request,'rateme/jointest.html')

def starttest(request):
    if request.method == 'POST':
        firstname=request.POST['fname']
        lastname=request.POST['lname']
        email=request.POST['email']
        test_id=request.POST['test_id']
        check_already_given=UserMapper.objects.raw("select m.id,m.email_id from rateme_usermapper as m where m.test_id_id=%s and m.email_id=%s",[test_id,email])
        test_password=request.POST['test_password']
        request.session['email']=email
        request.session['firstname']=firstname
        request.session['lastname']=lastname
        ct=datetime.datetime.now()
        request.session['current_timestamp']=str(ct)
        if len(check_already_given)>0:
            return redirect('thankyou')
        try:
            entry=Tests.objects.get(id=test_id,test_password=test_password)
        except:
            return redirect('jointest')
       
        print(entry)
        if entry:  
            all_question=Question.objects.all().filter(test_id=test_id)
            context={'entry':entry,'question_builder':all_question}
            return render(request,"rateme/starttest.html",context)
    return redirect("jointest")

@csrf_exempt
def submittest(request):
     ## an array with one object and one array, 1st object has all user details ('email','firstname','lastname','test_id')
     ## 2nd array is list of dict with params as question_id and selected choice for that question_id and 2nd param is selected_value
     user_submission=json.loads(request.body)
     user_email=user_submission[0]['email']
     fname=user_submission[0]['firstname']
     lname=user_submission[0]['lastname']
     test_id=int(user_submission[0]['test_id'])
     
     time_started=str(request.session['current_timestamp'])
     ct = datetime.datetime.now() 
     time_ended=str(ct)
     t_id=Tests.objects.get(id=test_id)
     mapping_entry=UserMapper(email_id=user_email,test_id=t_id,first_name=fname,last_name=lname,test_started=time_started,test_ended=time_ended)
     mapping_entry.save()
     curr_user_id=UserMapper.objects.filter(email_id=user_email).last()
     for question in user_submission[1]:
         q_id=Question.objects.get(id=question['question_id'])
         temp_entry=Submission(test_id=t_id,u_id=curr_user_id,question_id=q_id,selected_value=question['selected_value'])
         temp_entry.save()
    ##envaluation of test
     all_question=Question.objects.all().filter(test_id=t_id)
     score=0
     for question,real_question in zip(user_submission[1],all_question):
         if(str(question['selected_value'])==str(real_question.correct_choice)):
             score+=1
     update_score=UserMapper.objects.filter(id=curr_user_id).update(total_score=score)
     return JsonResponse({"status":"true"})
    
def testdetails(request,test_id):
    ## does the details of rquesting id belongs to this id with user id ?
    entry=Tests.objects.raw("select id,test_name from rateme_tests where id=%s and user_id_id=%s",[test_id,request.user.id])
    if len(entry)==0:
        ##if no he dont belong here and redirect him back to his dashboard
        return redirect('dashboard')
    test_details=tests=Tests.objects.raw("select t.test_name,t.total_time,t.total_question,t.test_password,t.id,count(m.id) as total_submissions from rateme_tests as t left join rateme_usermapper as m on t.id=m.test_id_id where t.user_id_id=%s and t.id=%s",[request.user.id,test_id])
    test_submissions=Tests.objects.raw("select u.id,u.email_id,u.first_name,u.last_name,u.test_ended,u.total_score from rateme_usermapper as u where u.test_id_id=%s",[test_id])

    context={'test_details':test_details[0],'submissions':test_submissions}
    return render(request,'rateme/edittest.html',context)

def delete_test(request,test_id):
     ## does the details of rquesting id belongs to this id with user id ?
    entry=Tests.objects.raw("select id,test_name from rateme_tests where id=%s and user_id_id=%s",[test_id,request.user.id])
    if len(entry)==0:
        ##if no he dont belong here and redirect him back to his dashboard
        return redirect('dashboard')
    try:
        delete_test=Tests.objects.filter(id=test_id).delete()
        tests=Tests.objects.raw("select t.test_name,t.total_time,t.total_question,t.test_password,t.id,count(m.id) as total_submissions from rateme_tests as t left join rateme_usermapper as m on t.id=m.test_id_id where t.user_id_id=%s",[request.user.id])
    except:
        return redirect('dashboard') 
    context={}
    error={'error_code':0}
    context['tests']=tests
    try:
        if tests[0].test_name==None:
            error['error_code']=1
    except:
        error['error_code']=1
    context['error']=error
    return render(request,'rateme/dashboard.html',context)



def thankyou(request):
    del request.session['email']
    return render(request,'rateme/thankyou.html')