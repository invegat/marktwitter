from .models import *

def toy_data(DB):
    DB.drop_all()
    DB.create_all()
    u1 = User(name='invegat')
    t1 = Tweet(text='Lambda School rocks!')
    t2 = Tweet(text='Web4, DS1')
    t3 = Tweet(text='https://lambdaschool.com/courses/data-science/')
    u1.tweets.append(t1)
    u1.tweets.append(t2)
    u1.tweets.append(t3)
    DB.session.add(u1)
    DB.session.add(t1)
    DB.session.add(t2)
    DB.session.add(t3)
    u1 = User(name='LambdaSchool')
    t1 = Tweet(text="What Lambda School is all about in 60 seconds. What are you waiting for?")
    t2 = Tweet(text=
    "This morning I submitted my first app to the App Store - \
    a free podcast app called Pods that I built during a @LambdaSchool project week.")
    t3 = Tweet(text=
    "A school that invests in you. Live, online classes, pay NOTHING until you land a high-paying job.")
    u1.tweets.append(t1)
    u1.tweets.append(t2)
    u1.tweets.append(t3)
    DB.session.add(u1)
    DB.session.add(t1)
    DB.session.add(t2)
    DB.session.add(t3)
    DB.session.commit()

