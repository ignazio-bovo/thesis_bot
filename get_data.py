# from abc import ABC
import numpy as np
import datetime as dt
from binance.client import Client
from binance.enums import *
from settings import BINANCE_KEY, BINANCE_SECRET

class DataGathererBase():
    def __init__(self, symbol):
        pass

    def get_line(self):
        pass

    def open_position(self, side, quantity, order_type = None, price=None):
        pass

    def close_position(self, open_order):
        pass


class DataGathererBinance(DataGathererBase):
    def __init__(self, symbol):
        global BINANCE_KEY, BINANCE_SECRET
        self.symb = symbol
        self.client = Client(BINANCE_KEY, BINANCE_SECRET)
        self.current_time = dt.datetime.now()
        self.previous_time = self.current_time - dt.timedelta(seconds =30)
        self.ask = 0
        self.asksize = 0
        self.bid = 0
        self.bidsize = 0
        self.orders = []

        # top of the order book
        self.depth = self.client.get_order_book(symbol=self.symb, limit=5)
        self.prev_bid, self.prev_bidsize = map(np.float64,self.depth['bids'][0])
        self.prev_ask, self.prev_asksize = map(np.float64,self.depth['asks'][0])

    def get_line(self):

        # maker liquidity imbalance 
        self.depth = self.client.get_order_book(symbol=self.symb, limit=5)
        self.bid, self.bidsize = map(np.float64,self.depth['bids'][0])
        self.ask, self.asksize = map(np.float64,self.depth['asks'][0])

        ofi = int(self.bid >= self.prev_bid) * self.bidsize - int(self.bid <= self.prev_bid) * self.prev_bidsize -\
                int(self.ask <= self.prev_ask) * self.asksize +  int(self.ask >= self.prev_ask) * self.prev_asksize

        self.prev_bid, selfprev_bidsize = self.bid, self.bidsize
        self.prev_ask, self.prev_asksize = self.ask, self.asksize
        
        # taker liquidity imbalance
        sell_qty = 0
        buy_qty = 0
        self.current_time = dt.datetime.now()
        trades = self.client.get_aggregate_trades(symbol=self.symb, 
                startTime = int(self.previous_time.timestamp()*1000),
                endTime= int(self.current_time.timestamp()*1000))
        self.previous_time = self.current_time

        for t in trades:
            if t['m']:
                buy_qty += np.float64(t['q'])
            else:
                sell_qty += np.float64(t['q'])
        line = [self.current_time.isoformat(), ofi, sell_qty,buy_qty, self.ask, self.bid]
        return line 

    def open_position(self, side, quantity, order_type = None, price=None):
        side_ = SIDE_BUY if side == 'BUY' else SIDE_SELL
        type_ = ORDER_TYPE_MARKET if order_type is None else ORDER_TYPE_LIMIT
        if order_type and not price:
            raise NameError('price must be together with a limit order ')

        order = self.client.create_test_order(
            symbol=self.symb,
            side=side_,
            type=type_,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=price)
        return order

    def close_position(self, open_order):
        info = client.get_order(open_order)
        qty = info['executedQty']
        side = info['side']
        order = self.client.create_test_order(
            symbol=self.symb,
            side= SIDE_SELL if side == SIDE_BUY else SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=qty,
            price=price)
        return order 


