import pandas as pd
import apimoex
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime
import requests
from scipy.optimize import minimize



def get_moex_data(tickers, start_date):
    '''
    Получение данных с Московской Биржи
    '''
    with requests.Session() as session:
        all_data = []
        for ticker in tickers:
            data = apimoex.get_board_history(session, ticker, start=start_date, board='TQBR')

            if not data: #в случае, если данные не считались
                print(f'Нет данных для {ticker}')
                continue
            df = pd.DataFrame(data)
            df = df[['TRADEDATE', 'CLOSE']]
            df.columns = ['Date', ticker]
            df.set_index('Date', inplace=True)
            all_data.append(df)

    final_df = pd.concat(all_data, axis = 1, join='inner')
    return final_df

def get_actual_rf():
    '''
    Получение ключевой ставки ЦБ
    '''
    url = 'https://www.cbr.ru/hd_base/KeyRate/'
    tables = pd.read_html(url)
    df = tables[0]
    raw_value = df.iloc[0,1]
    if isinstance(raw_value, str):
        current_rate = float(raw_value.replace(',', '.')) / 100
    else:
        current_rate = float(raw_value) / 100
        
    return current_rate
    
def calculate_weights(df, cons, bounds, init_guess):
    '''
    Считаем доходность, среднюю доходность, ковариационную матрицу и веса (во вложенной функции)
    '''
    returns = np.log(df / df.shift(1)).dropna()
    mean_returns = returns.mean() * 252
    cov_mat = returns.cov() * 252
    R_f = get_actual_rf()

    def get_ret_vol_sharpe(weights):
        '''
        Считаем ожидаемую доходность, волатильность, коэффициент Шарпа и возвращаем их
        '''
        weights = np.array(weights)
        e = np.sum(weights * mean_returns)
        vol = np.sqrt(np.dot(weights.T, np.dot(cov_mat, weights)))
        sharpe = (e - R_f) / vol
        return np.array([e, vol, sharpe])

    def min_vol(weights): 
        '''
        Поиск минимальной волатильности (риска)
        '''
        return get_ret_vol_sharpe(weights)[1]

    opt_results = minimize(min_vol, init_guess, method='SLSQP', 
                           bounds=bounds, constraints=cons)
    return opt_results.x