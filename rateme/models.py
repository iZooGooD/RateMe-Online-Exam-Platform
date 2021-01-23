from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Tests(models.Model):
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    test_name=models.CharField(max_length=100)
    test_category=models.CharField(max_length=100)
    total_question=models.IntegerField()
    total_time=models.IntegerField()
    test_password=models.CharField(max_length=100)



class Question(models.Model):
    test_id=models.ForeignKey(Tests,on_delete=models.CASCADE)
    question_name=models.TextField()
    choice_1=models.TextField()
    choice_2=models.TextField()
    choice_3=models.TextField()
    choice_4=models.TextField()
    correct_choice=models.CharField(max_length=20)


class UserMapper(models.Model):
    email_id=models.CharField(max_length=100)
    test_id=models.ForeignKey(Tests,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=100,default="")
    last_name=models.CharField(max_length=100,default="")
    test_started=models.DateTimeField(auto_now_add=True)
    test_ended=models.DateTimeField(auto_now=True)
    total_score=models.IntegerField(default=0)

    def __int__(self):
        return self.pk

class Submission(models.Model):
    test_id=models.ForeignKey(Tests,on_delete=models.CASCADE)
    u_id=models.ForeignKey(UserMapper,on_delete=models.CASCADE)
    question_id=models.ForeignKey(Question,on_delete=models.CASCADE)
    selected_value=models.IntegerField()


    
    




    