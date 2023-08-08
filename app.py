from flask import Flask, render_template, request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from itertools import groupby
from operator import itemgetter
import matplotlib
matplotlib.use('agg')
app = Flask(__name__)

college_list = []
global filename, dataset, names
global positive, negative, neutral, college
sid = SentimentIntensityAnalyzer()

@app.route('/')
def home():
    return render_template('index.html', text_widget=None, college_list=college_list)  # Pass college_list to the template
@app.route('/upload', methods=['POST'])
def upload():
    global filename, dataset, college_list
    filename = request.files['file']
    filename.save('uploaded_dataset.csv')
    dataset = pd.read_csv('uploaded_dataset.csv', lineterminator='\n')

    # Update college_list with the unique college names from the dataset
    college_list = dataset['college'].unique().tolist()

    return render_template('index.html', college_list=college_list)  # Pass college_list to the template


def processReviews(college_name):
    global dataset, college_list
    college = college_name.strip()  # Strip any leading/trailing spaces from the college name
    positive = 0
    negative = 0
    neutral = 0
    selected_college = dataset.loc[dataset['college'] == college]
    selected_college_reviews = selected_college['review'].tolist()

    for review in selected_college_reviews:
        sentiment_dict = sid.polarity_scores(review)
        compound = sentiment_dict['compound']
        if compound >= 0.90:
            positive += 1
        elif compound >= 0.50 and compound < 0.90:
            negative += 1
        else:
            neutral += 1

    total_reviews = len(selected_college_reviews)
    if total_reviews > 0:
        positive_percentage = (positive / total_reviews) * 100
        negative_percentage = (negative / total_reviews) * 100
        neutral_percentage = (neutral / total_reviews) * 100
    else:
        positive_percentage = 0
        negative_percentage = 0
        neutral_percentage = 0

    if total_reviews > 0:
        average_rating = (positive_percentage - negative_percentage) / total_reviews * 100
    else:
        average_rating = 0

    college_rank = get_college_rank(college_name)  # Get the rank of the college

    result = f"Selected College Name: {college}\n"
    result += f"Positive Reviews %: {positive_percentage:.2f}\n"
    result += f"Negative Reviews %: {negative_percentage:.2f}\n"
    result += f"Neutral Reviews %: {neutral_percentage:.2f}\n"
    result += f"Average Rating %: {average_rating/100}\n"
    result += f"College Rank: {college_rank}\n"

    return result, positive, negative, neutral, average_rating, college_rank


@app.route('/sentiment', methods=['POST'])
def sentiment():
    global college_list, dataset
    college = request.form.get('college_names', '')
    result, positive, negative, neutral, average_rating, college_rank = processReviews(college)


    graph_image = generate_graph(college, positive, negative, neutral)

    if graph_image:
        return render_template('index.html', college_list=college_list, result=result, graph_image=graph_image, average_rating=average_rating)
    else:
        return render_template('index.html', college_list=college_list, result=result, average_rating=average_rating)


def generate_rankings():
    global dataset, college_list
    rankings = {}

    for college in college_list:
        selected_college = dataset.loc[dataset['college'] == college]
        selected_college_reviews = selected_college['review'].tolist()
        positive, negative, neutral = 0, 0, 0

        for review in selected_college_reviews:
            sentiment_dict = sid.polarity_scores(review)
            compound = sentiment_dict['compound']
            if compound >= 0.90:
                positive += 1
            elif compound >= 0.50 and compound < 0.90:
                negative += 1
            else:
                neutral += 1

        total_reviews = len(selected_college_reviews)
        if total_reviews > 0:
            positive_percentage = (positive / total_reviews) * 100
            negative_percentage = (negative / total_reviews) * 100
            neutral_percentage = (neutral / total_reviews) * 100
        else:
            positive_percentage = 0
            negative_percentage = 0
            neutral_percentage = 0

        if total_reviews > 0:
            average_rating = (positive_percentage - negative_percentage) / total_reviews * 100
        else:
            average_rating = 0

        rankings[college] = (average_rating, total_reviews, positive, negative, neutral)

    # Sort the colleges based on the average rating, total reviews, and positive reviews (in that order)
    sorted_rankings = sorted(rankings.items(), key=lambda item: (item[1][0], item[1][1], item[1][2]), reverse=True)

    # Group colleges with the same ranking factors and assign the same rank
    ranked_colleges = []
    rank = 1
    for idx, (college, ranking_factors) in enumerate(sorted_rankings):
        if idx > 0 and ranking_factors < sorted_rankings[idx - 1][1]:
            rank = idx + 1
        ranked_colleges.append((rank, college, *ranking_factors))

    return ranked_colleges


def get_college_rank(college_name):
    ranked_colleges = generate_rankings()
    for rank, college, *_ in ranked_colleges:
        if college == college_name:
            return rank
    return None

@app.route('/rankings', methods=['GET'])
def rankings():
    ranked_colleges = generate_rankings()
    return render_template('rankings.html', ranked_colleges=ranked_colleges)


def do_enumerate(iterable, start=1):
    return enumerate(iterable, start)

# Register the custom filter
app.jinja_env.filters['enumerate'] = do_enumerate


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



def graph(college, positive, negative, neutral):
    count = [positive, negative, neutral]
    unique = ['Yes Admission%', 'No Admission%', 'Not Known%']
    plt.pie(count, labels=unique, autopct='%1.1f%%')
    plt.title(college + ' Admission Graph')
    plt.axis('equal')

    # Save the plot to a binary stream
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Encode the binary image to base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return image_base64
def generate_graph(college, positive, negative, neutral):
    graph_image = graph(college, positive, negative, neutral)
    return graph_image 

if __name__ == '__main__':
    app.run(debug=True, port=6500)
