import math
import numpy as np
from pprint import pprint

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
        self.sim_table = dict()
        if self.data_rating == None:
            print("Rating table is None. Use setratingtable(value) to setup it.")
        else:
            self.set_rating_table_rows_columns()
        
    def calculate_sim_table(self):
        # exemple app data to sim table ( 'Alice' -> 'Boom' )
        for active_user in self.rows:
            for target_user in self.rows:
                if active_user != target_user:  # same user
                    buffer = self.sim(active_user, target_user)
                    if active_user not in self.sim_table:  # not has data
                        self.sim_table.update({active_user: {}})
                    if target_user not in self.sim_table[active_user]:
                        self.sim_table[active_user].update({target_user: buffer})
        pprint(self.sim_table)

    def set_rating_table(self, rating_table):
        self.data_rating = rating_table
        self.set_rating_table_rows_columns()

    def set_rating_table_rows_columns(self):
        for object in self.data_rating:
            self.rows.append(object)
            for key in self.data_rating[object]:
                if key not in self.columns:
                    self.columns.append(key)
    
    def sim(self,value_a, value_b):
        # list_a -> []
        # list_b -> []
        list_a = list()
        list_b = list()


        # ***example value_a = Alice , value_b = Boom
        match = set(self.data_rating[value_a]).intersection(self.data_rating[value_b])
        # value_a -> data -> [ a : 2 , b : 4 , c : 1 , e : 4 ]
        # value_b -> data -> [ a : 1 , c : 3 , d : 3 , f : 2 ]

        # after intersection variable match = [ a , c ]

        # if match = []
        if len(match) == 0:
            return None

        # list_a -> []
        # list_b -> []
        for p in match:
            list_a.append(float(self.data_rating[value_a][p]))
            list_b.append(float(self.data_rating[value_b][p]))
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
