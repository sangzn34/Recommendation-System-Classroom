import math
import numpy as np
from pprint import pprint
import json

class recommender:
    def __init__(self, data_rating=None):
        # rating table
        self.data_rating = data_rating
        # predict table
        self.data_rating_pred = dict()
        # keyword <- rows
        self.rows = list()
        # keyword <- colums
        self.columns = list()
        # similarity table
        self.sim_table = []
        self.k = 1
        self.best_k = 0
        self.colK = []
        self.data_rating_k = []
        if self.data_rating == None:
            print("Rating table is None. Use setratingtable(value) to setup it.")
        else:
            self.set_rating_table_rows_columns()
    def set_k(self, k = 1):
        self.k = k
    
    def set_best_k(self, k = 1):
        self.best_k = k

    def pred(self, active_user, position_pred, sim_table):
        up = 0
        down = 0
        for user in self.data_rating:
            try:
                up += sim_table[active_user][user]["sim"] * self.data_rating[user][position_pred]
                down += abs(sim_table[active_user][user]["sim"])
            except (KeyError, TypeError):
                up += 0
        if down == 0:
            down = 1
        p = float(up / abs(down))
        return p

    def pred_movie(self, active_user):
        movie_list = dict()
        file = 'data/data'+str(self.best_k+1)+'.json'
        if active_user not in self.rows:
            return movie_list
        threshold = 4
        num = 5
        with open(file) as json_data:
           d = json.load(json_data)
           count = 0
           for movie in self.columns:
               if movie not in self.data_rating[active_user]:
                    p = self.pred(active_user, movie, d)
                    if p >= threshold:
                        movie_list.update({movie : p})
                        count += 1
                    if count >= num:
                        break
        return movie_list

    def cal_find_best_k(self):
        persent = []
        for k in range(self.k):
            file = 'data/data'+str(k+1)+'.json'
            with open(file) as json_data:
                d = json.load(json_data)
                count = 0
                sum = 0
                for object in d:
                    for movie in self.colK[k]:
                        r = 0
                        if movie not in self.data_rating[object]:
                            continue
                            #r = self.pred(object, movie, d)
                        #else:
                        r =  self.data_rating[object][movie] 
                        p = 0
                        down = 0
                        for target in d[object]:
                            try:
                                if d[object][target] == None or self.data_rating[target][movie] == None:
                                    continue 
                                p += d[object][target]["sim"] * self.data_rating[target][movie]
                                down +=  abs(d[object][target]["sim"])
                            except (KeyError, TypeError):
                                p += 0
                        if down != 0:
                            p = p / abs(down)
                            sum += np.power(p - r, 2)
                            count += 1
                            a = sum / count
                if count == 0:
                    count = 1
                RMSE = np.sqrt(sum / count)
                persent.append(RMSE)
        min = np.min(persent)
        for i in range(len(persent)):
            if min == persent[i]:
                self.best_k = i
        print(persent) 

    def calculate_sim_table(self):
        # exemple app data to sim table ( 'Alice' -> 'Boom' )
        self.sim_table = []
        for k in range(self.k):
            self.sim_table.append(dict())
            for active_user in self.rows:
                for target_user in self.rows:
                    if active_user != target_user:  # same user
                        buffer = self.sim(k, active_user, target_user)
                        if active_user not in self.sim_table[k]:  # not has data
                            self.sim_table[k].update({active_user: {}})
                        if target_user not in self.sim_table[k][active_user]:
                            self.sim_table[k][active_user].update({target_user: buffer})
            with open('data/data' + str(k+1) + '.json', 'w') as outfile:
                json.dump(self.sim_table[k], outfile)
    
    


    def set_rating_table(self, rating_table):
        self.data_rating = rating_table
        self.set_rating_table_rows_columns()

    def set_rating_table_rows_columns(self):
        for object in self.data_rating:
            self.rows.append(object)
            for key in self.data_rating[object]:
                if key not in self.columns:
                    self.columns.append(key)
        len_col = len(self.columns)
        partition = int(len_col / self.k)
        count = 0
        colK = []
        data_rating_k = []
        for i in range(self.k):
            self.data_rating_k.append(dict())
            self.colK.append(dict()); 
            for j in range(partition):
                self.colK[len(self.colK) - 1].update({self.columns[count] : True})
                count += 1
        if count != len_col:
             for i in range(count, len_col):
                self.colK[len(self.colK) - 1].update({self.columns[count] : True})
                count += 1
        for object in self.data_rating:
            for key in self.data_rating[object]:
                i = 0
                for col in self.colK:
                    if key in col:
                        if object not in self.data_rating_k[i]:
                            self.data_rating_k[i].update({object: {}})
                        self.data_rating_k[i][object].update({key:  self.data_rating[object][key]})
                    i += 1

                
    
    def sim(self, k, value_a, value_b):
        # list_a -> []
        # list_b -> []
        list_a = list()
        list_b = list()


        # ***example value_a = Alice , value_b = Boom
        try:
            match = set(self.data_rating_k[k][value_a]).intersection(self.data_rating_k[k][value_b])
        except KeyError:
            return None
        # value_a -> data -> [ a : 2 , b : 4 , c : 1 , e : 4 ]
        # value_b -> data -> [ a : 1 , c : 3 , d : 3 , f : 2 ]

        # after intersection variable match = [ a , c ]

        # if match = []
        if len(match) == 0:
            return None

        # list_a -> []
        # list_b -> []
        for p in match:
            list_a.append(float(self.data_rating_k[k][value_a][p]))
            list_b.append(float(self.data_rating_k[k][value_b][p]))
        # insert data to list a and b
        # list_a -> [ 2 , 1 ]
        # list_b -> [ 1 , 3 ]

        # R(a,p)-average(R(a)) -> u
        # [ 2 , 1 ] - (sum( 2 ,4 ,1 ,4 )/4) -> [ -0.75 , -1.75 ]
        u = (np.array(list_a) - np.average(list_a))

        # R(b,p)-average(R(b)) -> p
        # [ 1 , 3 ] - (sum( 1 ,3 ,3 ,2 )/4) -> [ -1.25 , -0.75 ]
        p = (np.array(list_b) - np.average(list_b))

        # sum((R(a,p)-average(R(a))) * (R(b,p)-average(R(b))))
        # [ -0.75 -1.75 ] * [ -1.25 , -0.75 ]
        # [ -0.75 * -1.25 , -1.75 * -0.75 ]
        # sum[ 0.9375 , 1.3125 ] -> 2.25
        up = sum(u*p)

        # sum( ( R(a, p)-average(R(a)) )^2 )
        # sum ( [ -0.75 -1.75 ]^2 ) -> sum [ 0.5625 , 3.0625 ]
        # 0.5625 + 3.0625 -> 3.625
        do = sum(np.power(u, 2))

        # sum( ( R(b, p)-average(R(a)) )^2 )
        # sum ( [ -1.25 -0.75 ]^2 ) -> sum [ 1.5625 , 0.5625 ]
        # 1.5625 + 0.5625 -> 2.125
        wn = sum(np.power(p, 2))

        # sqrt ( sum( ( R(a, p)-average(R(a)) )^2 ) ) * sqrt ( sum( ( R(a, p)-average(R(a)) )^2 ) )
        # sqrt ( 3.625 ) * sqrt ( 2.125 )
        # 1.904 * 1.458
        down = np.sqrt(do)*np.sqrt(wn)
        output = { 'sim': float(up/down) }

        # if rating [ 4, 4, 4, 4 ]
        # average[ 4, 4, 4, 4 ] -> 4
        # R(t,p)-average(R(t)) - > [ 0, 0, 0, 0 ]
        # 0/0 or n/0 -> nan
        if math.isnan(output['sim']):
            output = None

        # return value <- similarity
        return output
