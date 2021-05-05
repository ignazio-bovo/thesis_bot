import numpy as np
from hitbtc_data import DataGathererHITBTC
from perceptron import Perceptron, SOPerceptron
import time
import sys

if __name__ == '__main__':

    wealth = 0

    try:
        dg = DataGathererHITBTC(sys.argv[1])
    except:
        print(f'symbol {sys.argv[1]} not found')

    prev_ask = dg.prev_ask
    prev_bid = dg.prev_bid

    perc_x = SOPerceptron(3)
    perc_y = SOPerceptron(3)

    rounds = 0
    errors = np.zeros(50)

    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[2])
        except:
            print("error with interval quantity")
    else:
        interval = 5

    i = 0

    # with open('out.txt','w') as file_:
        # file_.write('x_pred,x_true,y_pred,y_true,net_x,net_y,wealth')
        # file_.write('\n')

    position = {}
    while True:
        rounds = max(rounds + 2, 50)
        i = (i + 1) % 50

        if position:
            side_ = 'sell' if position['side'] == 'buy' else 'buy'
            closing_pos = dg.close_position(position, price=None)
            print(time_, side_, position['quantity'],'close')
            position = {}

        line = dg.get_line()
        # msg = ','.join(map(str,line))

        z = np.array([line[1],line[2],line[3]])
        ask = line[4]
        bid = line[5]
        time_ = line[0]

        x_pred = perc_x.predict(z)
        y_pred = perc_y.predict(z) if  x_pred != 1 else 1

        x = bid - prev_ask
        y = ask - prev_bid

        errors[i] = int(y_pred != np.sign(x)) + int(x_pred != np.sign(x))

        # net1, net2 = 0,0
        print('*'*65)
        print(f'{time_} xpred: {x_pred}, x: {x: .3f}, ypred: {y_pred}, y: {y: .3f}')
        if x_pred > 0:
            try:
                position = dg.open_position(side='buy', quantity=1e-3)
                print(time_, position['side'], position['quantity'],'open')
            except NameError as e:
                print(time_, e)
                # net1 = (x - .18e-2 * np.abs(x))

        if y_pred < 0:
            try:
                position = dg.open_position(side='sell', quantity=1e-3)
                print(time_, position['side'], position['quantity'],'open')
            except NameError as e:
                print(time_, e)
                # net2 = -(y + .18e-2 * np.abs(y))

        # wealth += net1 + net2
        # with open('out.txt','a') as file_:
            # file_.write(f'{x_pred},{x:.3f},{y_pred},{y:.3f},{net1:.3f},{net2:.3f},{wealth:.6f}')
            # file_.write('\n')
        
        perc_x.update(z,x)
        perc_y.update(z,y)

        prev_ask = ask
        prev_bid = bid

        time.sleep(interval)

