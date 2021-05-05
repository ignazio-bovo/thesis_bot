import numpy as np
import pandas as pd
import datetime as dt
from get_data import DataGathererBase
import requests
from settings import HITBTC_DEMO_KEY, HITBTC_DEMO_SECRET

class DataGathererHITBTC(DataGathererBase):
    def __init__(self, symbol):
        self.session = requests.session()
        self.session.auth = (HITBTC_DEMO_KEY, HITBTC_DEMO_SECRET)
        self.symb = symbol
        # self.client = Client(BINANCE_KEY, BINANCE_SECRET)
        self.current_time = dt.datetime.utcnow()
        self.previous_time = self.current_time - dt.timedelta(seconds = 30)
        self.ask = 0
        self.asksize = 0
        self.bid = 0
        self.bidsize = 0
        self.orders = []

        # top of the order book
        url_book = f'https://api.demo.hitbtc.com/api/2/public/orderbook/{self.symb}?limit=1'
        book = self.session.get(url_book).json()
        ask_data = book['ask']
        bid_data = book['bid']
        self.prev_bid, self.prev_bidsize =  map(np.float64,list(bid_data[0].values()))
        self.prev_ask, self.prev_asksize =  map(np.float64,list(ask_data[0].values()))

    def get_line(self):
        # top of the order book
        book = self.session.get(f'https://api.demo.hitbtc.com/api/2/public/orderbook/{self.symb}?limit=1').json()
        ask_data = book['ask']
        bid_data = book['bid']

        self.bid, self.bidsize = map(np.float64,list(bid_data[0].values()))
        self.ask, self.asksize = map(np.float64,list(ask_data[0].values()))

        ofi = int(self.bid >= self.prev_bid) * self.bidsize - int(self.bid <= self.prev_bid) * self.prev_bidsize -\
                int(self.ask <= self.prev_ask) * self.asksize +  int(self.ask >= self.prev_ask) * self.prev_asksize

        self.prev_bid, selfprev_bidsize = self.bid, self.bidsize
        self.prev_ask, self.prev_asksize = self.ask, self.asksize

        sell_qty = 0
        buy_qty = 0
        self.current_time = dt.datetime.utcnow()

        trades_url = f'https://api.demo.hitbtc.com/api/2/public/trades/{self.symb}?from={self.previous_time.isoformat()}&till={self.current_time.isoformat()}'
        trades = self.session.get(trades_url).json()

        for t in trades:
            if t['side'] == 'buy':
                buy_qty += np.float64(t['quantity'])
            else:
                sell_qty += np.float64(t['quantity'])

        time_out = self.current_time.isoformat()
        line = [time_out, ofi, sell_qty,buy_qty, self.ask, self.bid]
        return line 

    def open_position(self, side, quantity):
        '''
        Place market order to immediately open the position
        '''
        orderData = {'symbol': self.symb, 'side': side, 'quantity': quantity, 'type': 'market'}
        resp = self.session.post('https://api.demo.hitbtc.com/api/2/margin/order', data = orderData).json()

        if list(resp.keys())[0] == 'error':
            raise NameError(resp['error']['message'])
            return None
        return resp 

    def close_position(self, open_order, price=None):
        '''
        place market/limit order to close the position
        '''
        if price :
            resp = self.session.delete(f'https://api.demo.hitbtc.com/api/2/margin/position/{self.symb}',
                    json={'price':price, "strictValidate": True}).json()
        else:
            resp = self.session.delete(f'https://api.demo.hitbtc.com/api/2/margin/position/{self.symb}',
                    json={"strictValidate": True}).json()

        if list(resp.keys())[0] == 'error':
            raise NameError(resp['error']['message'])
            return None
        return resp

    def balance(self):
        resp = self.session.get('https://api.demo.hitbtc.com/api/2/account/balance').json()
        # print(resp)
        bal = 0
        for r in resp:
            if r['currency'] == 'BTC':
                bal += np.float64(r['available']) * self.bid
            if r['currency'] == 'USD':
                bal += np.float64(r['available'])
        return bal
