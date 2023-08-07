from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
import numpy as np
import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tkinter import ttk

college_list = []
global filename, dataset, names
global positive, negative, neutral, college
sid = SentimentIntensityAnalyzer()

main = Tk()
main.title("Sentiment Analysis of Educational Institutions for getting Admissions")
main.geometry("1300x1200")

def uploadDataset():
    global filename, dataset
    filename = filedialog.askopenfilename(initialdir="Dataset")
    tf1.insert(END,filename)
    text.delete('1.0', END)
    text.insert(END,filename+" dataset loaded\n\n")
    dataset = pd.read_csv(filename, lineterminator='\n')
    text.insert(END,str(dataset.head()))

def processReviews():
    text.delete('1.0', END)
    global dataset, college_list, names
    college_list.clear()
    college_list = np.unique(dataset['college']).tolist()
    temp = []
    for i in range(len(college_list)):
        selected_college = dataset.loc[dataset['college'] == college_list[i]]
        selected_college = selected_college['review'].tolist()
        if len(selected_college) > 10:
            temp.append(college_list[i])            
    college_list = temp    
    names['values'] = college_list
    names.current(0)

def sentimentAnalysis():
    text.delete('1.0', END)
    global dataset, college_list, names, college
    global positive, negative, neutral
    positive = 0
    negative = 0
    neutral = 0
    college = names.get()
    selected_college = dataset.loc[dataset['college'] == college]
    selected_college = selected_college['review'].tolist()
    for i in range(len(selected_college)):
        review = selected_college[i]
        print(review)
        sentiment_dict = sid.polarity_scores(review)
        compound = sentiment_dict['compound']
        print(compound)
        if compound >= 0.90:
            positive = positive + 1
        elif compound >= 0.50 and compound < 0.90:
            negative = negative + 1
        else:
            neutral = neutral + 1
    if positive > 0:
        positive = positive / len(selected_college)
    if negative > 0:
        negative = negative / len(selected_college)
    if neutral > 0:
        neutral = neutral / len(selected_college)
    text.insert(END,"Selected College Name : "+names.get()+"\n")
    text.insert(END,"Positive Reviews % : "+str(positive)+"\n")
    text.insert(END,"Negative Reviews % : "+str(negative)+"\n")
    text.insert(END,"Neutral Reviews  % : "+str(neutral)+"\n")

def graph():
    global positive, negative, neutral
    count = [positive, negative, neutral]
    unique = ['Yes Admission%', 'No Admission%', 'Not Known%']
    plt.pie(count,labels=unique,autopct='%1.1f%%')
    plt.title(college+' Admission Graph')
    plt.axis('equal')
    plt.show()

font = ('times', 15, 'bold')
title = Label(main, text='Sentiment Analysis of Educational Institutions for getting Admissions')
title.config(bg='mint cream', fg='olive drab')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 14, 'bold')
ff = ('times', 12, 'bold')

l1 = Label(main, text='Upload Dataset:')
l1.config(font=font1)
l1.place(x=50,y=100)

tf1 = Entry(main,width=40)
tf1.config(font=font1)
tf1.place(x=210,y=100)

uploadButton = Button(main, text="Upload College Reviews Dataset", command=uploadDataset)
uploadButton.place(x=650,y=100)
uploadButton.config(font=ff)

processButton = Button(main, text="Process Reviews Different Colleges", command=processReviews)
processButton.place(x=50,y=150)
processButton.config(font=ff)

l2 = Label(main, text='College Names:')
l2.config(font=font1)
l2.place(x=50,y=210)

names = ttk.Combobox(main,values=college_list,postcommand=lambda: names.configure(values=college_list))
names.place(x=230,y=210)
names.config(font=font1)

sentimentButton = Button(main, text="Perform Sentiment Analysis", command=sentimentAnalysis)
sentimentButton.place(x=50,y=260)
sentimentButton.config(font=ff)

graphButton = Button(main, text="College Overall Admission Graph", command=graph)
graphButton.place(x=330,y=260)
graphButton.config(font=ff)

font1 = ('times', 13, 'bold')
text=Text(main,height=15,width=100)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=300)
text.config(font=font1)

main.config(bg='gainsboro')
main.mainloop()
