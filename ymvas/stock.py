from collections import deque
import random, numpy as np

class StockTrading:
    _api = None

    def __init__(self, api ):
        self.api = api

    def instruments(self):
        if self._instruments != None:
            return self._instruments

        ins  = {}
        data = self.api("/stocks/instruments")
        for i in data:
            ins[data[i]['name']] = data[i]

        self._instruments = ins
        return ins

    def batch( self ,target = 1, year = 2020 , sequences = 150 ):
        count = 0
        ymvas = self.api
        days  = deque( maxlen = sequences )

        while True:
            query = f"?year={year}&sequences=200&page={count}&target={target}"
            rows  = ymvas.api( "/stocks/datasets/related_stocks" + query )

            count += 1
            print( f'URL: {query:100} BATCH: {count:5} : {len(rows):5}' )

            if len(rows) == 0:
                return

            for row in rows:
                weights = list(row.values())[1:]
                weights = [float(x) for x in weights ]
                days.append( weights )

                if len( days ) != sequences:
                    continue

                batch = ( np.array(days) , row['action'] )
                yield batch

    def sets( self,target=1, batches = 100 , split = 2020 ):
        count = 0
        generator = self.batch( target , split )
        X,Y = [],[]

        while True:
            # print( 'sets :' , count )
            x,y = next(generator)
            X.append(x)
            Y.append(y)

            if (count % batches == 0) and count != 0:
                yield (
                    np.array(X).astype(np.float32),
                    np.array(Y).astype(np.float32)
                )

                X,Y = [],[]

            count += 1

    # def stocksData( self , page ):
    #     info = requests.get( "https://api.ymvas.com/stocks::stream", params = {
    #         'page' : page
    #     }, headers = self.ysk )
    #
    #     return info.json()['data']
    #
    # def stream( self ):
    #     last_time  = 0
    #
    #     page = 0
    #     while data := self.stocksData( page ):
    #         if len(data) == 0:
    #             break
    #
    #         for i in data:
    #             xtime = float(data[i]['time'])
    #             stock = data[i]['instrument']
    #             price = data[i]['price']
    #
    #             wait      = xtime - last_time
    #             last_time = xtime
    #
    #             if wait < 1 and wait > 0:
    #                 sleep(wait)
    #
    #             yield xtime,stock,price
    #
    #         page += 1
