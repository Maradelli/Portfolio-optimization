import pandas as pd
import apimoex
import numpy as np
import requests
from scipy.optimize import minimize

def get_moex_data(tickers, start_date):
    '''
    Получение данных с Московской Биржи с проверкой на существование тикера
    '''
    with requests.Session() as session:
        all_data = []
        for ticker in tickers:
            data = apimoex.get_board_history(session, ticker, start=start_date, board='TQBR')
            
            if data: 
                df = pd.DataFrame(data)
                if not df.empty:
                    df = df[['TRADEDATE', 'CLOSE']]
                    df.columns = ['Date', ticker]
                    df.set_index('Date', inplace=True)
                    all_data.append(df)
            else:
                continue

        if not all_data:
            return pd.DataFrame()
            
        final_df = pd.concat(all_data, axis=1, join='outer')
        final_df = final_df.sort_index().ffill()
        
        final_df = final_df.dropna()
        
    return final_df

def get_actual_rf():
    '''
    Получение ключевой ставки ЦБ
    '''
    try:
        url = 'https://www.cbr.ru/hd_base/KeyRate/'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        tables = pd.read_html(response.text)
        df = tables[0]
        raw_value = df.iloc[0, 1]
        
        if isinstance(raw_value, str):
            current_rate = float(raw_value.replace(',', '.')) / 100
        else:
            current_rate = float(raw_value) / 100
        return current_rate
    except Exception:
        return 0.16 

def calculate_weights(df, cons, bounds, init_guess):
    '''
    Расчет оптимальных весов портфеля
    '''
    returns = np.log(df / df.shift(1)).dropna()
    
    mean_returns = returns.mean() * 252
    cov_mat = returns.cov() * 252
    
    try:
        R_f = get_actual_rf()
    except:
        R_f = 0.16

    def get_ret_vol_sharpe(weights):
        weights = np.array(weights)
        e = np.sum(weights * mean_returns)
        vol = np.sqrt(np.dot(weights.T, np.dot(cov_mat, weights)))
        sharpe = (e - R_f) / (vol + 1e-9) 
        return np.array([e, vol, sharpe])

    def min_vol(weights): 
        return get_ret_vol_sharpe(weights)[1]

    opt_results = minimize(
        min_vol, 
        init_guess, 
        method='SLSQP', 
        bounds=bounds, 
        constraints=cons
    )
    
    return opt_results.x
