from pprint import pprint
from recommender import recommender
import csv


if __name__ == "__main__":
    given = dict()
    tb_movie = dict()
    file_rating = 'data/ratings'
    file_movie = 'data/movies'

    with open(file_rating+'.csv','r') as csvfile:
        reader = csv.DictReader(csvfile)
        for data in reader:
            if data['userId'] not in given:
                given.update({data['userId']: {}})
            given[data['userId']].update({data['movieId']: float(data['rating'])})

    with open(file_movie+'.csv', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for data in reader:
            try:
                tb_movie.update({data['movieId']: data['title']})
            except UnicodeEncodeError:
                continue

    # create object recommender
    object = recommender()

    # input data(given) to object [ given 
    # 
    # -> file .json ]
    object.set_k(5)
    object.set_rating_table(given)

    #object.calculate_sim_table()
    #object.cal_find_best_k()

    object.set_best_k(0)
    active_user = 0
    cache_user = dict()
    while active_user != "Exit":
        try:
            active_user = input("Enter Active User : ")
            movie_recommend = object.pred_movie(active_user) if active_user not in cache_user else cache_user[active_user]
            cache_user.update({active_user: movie_recommend})
            for movie in movie_recommend:
                print(movie + '\t' +tb_movie[movie] + '\t' + str(movie_recommend[movie]))
        except (KeyError):
            continue

    