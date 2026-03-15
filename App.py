import streamlit as st
from Functions import calculate_weights, get_moex_data
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(page_title='MOEX Portfolio Optimizer', layout='centered')
st.title('Оптимизатор портфеля by Maradelli')
st.markdown('Приложение рассчитывает идеальные доли акций, минимизируя риск по теории Марковица.')

st.sidebar.header('Настройки портфеля')
budget = st.sidebar.number_input('Ваш бюджет (руб.)', min_value = 1000, value = 1_000_000, step=1000)
tickers_input = st.sidebar.text_input('Тикеры (через запятую)', 'SBER, LKOH, GAZP, PLZL')
tickers = [t.strip().upper() for t in tickers_input.split(',')]
start_date = st.sidebar.date_input('Дата начала анализа', value=pd.to_datetime('2026-01-01'))

if st.sidebar.button('Рассчитать оптимальный портфель'):
    with st.spinner('Анализируем рынок...'):
        data = get_moex_data(tickers, start_date)
        
        if not data.empty:
            cons = ({'type' : 'eq', 'fun' : lambda x: np.sum(x) - 1}) #Накладываем ограничения
            bounds = tuple((0,1) for _ in range(len(tickers))) #Задаём границы для веса
            init_guess = [1/len(tickers)] * len(tickers) #Задаём начальную точку для минимизации

            weights = calculate_weights(data, cons, bounds, init_guess)
            result_data = pd.DataFrame({'Тикер' : tickers, 'Вес %' : weights})
            result_data = result_data[result_data['Вес %'] > 0.1]
            st.subheader("Оптимальное распределение активов")

            col1, col2 = st.columns([1,1])

            with col1:
                #Круговая диаграмма
                fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
                ax_pie.pie(result_data['Вес %'], labels=result_data['Тикер'], autopct='%1.1f%%', colors=plt.cm.Paired.colors)
                ax_pie.set_title("Доли в портфеле")
                st.pyplot(fig_pie)

            with col2:
                #Таблица с расчётами
                res_df = pd.DataFrame({
                    "Тикер": result_data['Тикер'],
                    "Доля (%)": (result_data['Вес %'] * 100).round(2),
                    "Сумма (₽)": (result_data['Вес %'] * budget).round(2)
                })
                st.table(res_df)
                
            st.info(f"Минимальный риск достигнут при текущей ключевой ставке 15.5%")
        else:
            st.error("Ошибка загрузки данных. Проверьте правильность тикеров.")