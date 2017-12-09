
from recommender import recommender
import csv


if __name__ == "__main__":
    given = dict()
    file = 'data/ratings'


    with open(file+'.csv','r') as csvfile:
        reader = csv.DictReader(csvfile)
        for data in reader:
            if data['userId'] not in given:
                given.update({data['userId']: {}})
            given[data['userId']].update({data['movieId']: float(data['rating'])})

    # create object recommender
    object = recommender()

    # input data(given) to object [ given 
    # 
    # -> file .json ]
    object.set_rating_table(given)

    object.calculate_sim_table()
