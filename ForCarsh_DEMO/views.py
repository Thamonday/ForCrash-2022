from calendar import month
import email
from re import X
from time import time
from unicodedata import name
from django.shortcuts import redirect, render
import pyrebase
from django.contrib import auth as authe
import pickle
from django.conf import settings
import xgboost as xgb
import os
from pathlib import Path
import pandas as pd
from django.contrib import messages
from datetime import datetime

firebaseConfig={ 'apiKey': "AIzaSyD3qcCh1MxUoiqk7dld7hLuGVmx--ri3hY",
  'authDomain': "forcrashdemo.firebaseapp.com",
  'databaseURL': "https://forcrashdemo-default-rtdb.firebaseio.com",
  'projectId': "forcrashdemo",
  'storageBucket': "forcrashdemo.appspot.com",
  'messagingSenderId': "216908476609",
  'appId': "1:216908476609:web:872afce2e6255e1e1fe440",
  'measurementId': "G-FJMZLMD0ZY"

}
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()
database=firebase.database()

date_now = datetime.now()
loginactive = 0
name = []
email_G = []
memberKey = []
def index(request): 
    if loginactive == 0: return render(request,'Login.html')
    elif loginactive == 1 : return render(request,'Home.html',{'name':name,'email':email_G,'memberKey':memberKey})

def login(request):
    return render(request,'login.html')

def logout(request):
    authe.logout(request)
    global name
    name = []
    return render(request,'Login.html')

def register(request):
    return render(request,'Register.html')

def aboutus(request):
    return render(request,'aboutus.html')

def howto(request):
    return render(request,'HowTo.html')

def history(request):
    global email_G
    return render(request,'History.html',{'name':name,'email':email_G,'memberKey':memberKey})

def QuestionForm(request):
    return render(request,'QuestionForm.html',{'name':name,'date':date_now,'email':email_G})

def postlogin(request):
    email = request.POST.get('Email')
    password = request.POST.get('Password')
    try:
        user = auth.sign_in_with_email_and_password(email,password)
        global loginactive
        loginactive = 1
        members=database.child('Member').get()
        for person in members.each():
            if person.val()['email']==email:
                member_name = database.child('Member').child(person.key()).child('firstname').get().val()
                global name , email_G ,memberKey
                name = member_name
                email_G = email
                memberKey = person.key()
        return render(request,'Home.html',{'name':member_name,'date':date_now,'email':email_G,'memberKey':memberKey})
    except:
        messages.error(request, "อีเมลหรือรหัสผ่านให้ถูกต้อง")
        return redirect('/login')

def postregister(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = auth.create_user_with_email_and_password(email, password)
    except: 
        messages.warning(request,"อีเมลนี้มีผู้ใช้แล้ว")
        return redirect('/register')
    firstname=request.POST.get('firstname')
    lastname=request.POST.get('lastname')
    institute=request.POST.get('institute')
    data = {'firstname':firstname,'lastname':lastname,'institute':institute,'email':email,'password':password}
    database.child('Member').push(data)#.setValue("setting")
    # database.child('Member').child(memberId).setValue(email)
    return render(request,'Login.html')

def postQuestionForm(request):
    booster = xgb.Booster()
    booster.load_model(r'models\bin_model1_xgboost.bin')
    with open(r'models\sav_model1_xgboost.sav','rb') as f:
        clf1 = pickle.load(f)
    booster.load_model(r'models\bin_model2_xgboost.bin')
    with open(r'models\sav_model2_xgboost.sav','rb') as f:
        clf2 = pickle.load(f)
    
    day_of_week = date_now.strftime("%A")
    acc_month = int(date_now.strftime("%m"))
    acc_time = int(date_now.strftime("%H"))

    dict1 ={'Monday':0 ,'Tuesday':1 ,'Wednesday':2 ,'Thursday':3 ,'Friday':4 ,'Saturday':5 ,'Sunday':6 }
    n = 0
    for i in dict1:
        if day_of_week == i:
            day_of_week = n
        n+=1
    x = acc_time    
    if (x > 6) and (x <= 12):
        acc_time = 0 #'Morning'
    elif (x > 12) and (x <= 18 ):
        acc_time = 1 #'Afternoon'
    elif (x > 18) and (x <= 24):
        acc_time = 2 #'Evening'
    elif (x >= 0) and (x <= 6) :
        acc_time = 3 #'Night'

    
    age=request.POST.get('age')
    sex = request.POST.get('sex')
    nation = request.POST.get('nation')
    alc = request.POST.get('alc')
    drug = request.POST.get('drug')
    
    belt = request.POST.get('belt')
    helmet = request.POST.get('helmet')
    if belt is None:
        belt = 1 
    if helmet is None:
        helmet = 1

    head=request.POST.get('head')
    neck=request.POST.get('neck')
    thorax=request.POST.get('thorax')
    abdomen=request.POST.get('abdomen')
    upper=request.POST.get('upper')
    pelvis=request.POST.get('pelvis')
    lower=request.POST.get('lower')
    back=request.POST.get('back')

    transport=request.POST.get('transport')
    person_type=request.POST.get('person_type')
    refer_sender=request.POST.get('refer_sender')

    global email_G
   
    data = {'Sex':sex,'Age':age,'nationality':nation,'transport':transport,'acc_person_type':person_type,
        'refer_sender':refer_sender,'alcohol':alc,'drug':drug,'belt':belt,'helmet':helmet,
        'day_of_week':day_of_week,'acc_month':acc_month,'acc_time':acc_time,'abdomen':abdomen,
        'back':back,'head':head,'lower':lower,'neck':neck,'pelvis':pelvis,'thorax':thorax,'upper':upper}

    df = pd.DataFrame(data, index=[0])
    print(df)
    df= df.astype(int)
    
    y_pred = clf1.predict(df)
    print(y_pred== 'Severe')
    if y_pred == 'Severe' :
        y_pred = clf2.predict(df)
    df['result']=y_pred
    df['email']= email_G
    
    time = date_now.strftime("%m/%d/%Y, %H:%M:%S")
    print(type(time),time)
    df['datetime']= time
    df['HN']= 'ยังไม่มีการแก้ไข'
    df['unconscious']= request.POST.get('unconscious')
    rescuer = request.POST.get('rescuer')
    df['rescuer']= rescuer
    df['ERTriage']= '-'
    print(y_pred,rescuer)
    if rescuer == '1':
        y_pred = 'Resuscitation'
    
    pre=df.to_dict('records')
    to_firebase = pre[0]
    database.child('Form').push(to_firebase)

    if y_pred == 'Non-Urgent':
        finalResult = 'เจ็บป่วยไม่ฉุกเฉิน'
    elif  y_pred == 'Semi-Urgent':
        finalResult = 'ฉุกเฉินไม่เร่งด่วน'
    elif  y_pred == 'Urgent':
        finalResult = 'ฉุกเฉินไม่เร่งด่วน'
    elif  y_pred == 'Emergency':
        finalResult = 'ฉุกเฉินวิกฤติ'
    elif  y_pred == 'Resuscitation':
        finalResult = 'ไม่มีการตอบสนอง'

    return render(request,'Result.html',{'result':y_pred,'finalResult':finalResult,'name':name,'email':email_G})