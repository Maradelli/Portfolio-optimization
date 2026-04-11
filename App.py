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
budget = st.sidebar.number_input('Ваш бюджет (руб.)', min_value=1000, value=1_000_000, step=1000)
tickers_input = st.sidebar.text_input('Тикеры (через запятую)', 'SBER, LKOH, GAZP, PLZL')

tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

for _ in range(5):
    st.sidebar.write("")
    
start_date = st.sidebar.date_input('Дата начала анализа', value=pd.to_datetime('2023-01-01'))

if st.sidebar.button('Рассчитать оптимальный портфель'):
    if not tickers:
        st.error('Ошибка: Вы не ввели ни одного тикера!')
    else:
        with st.spinner('Анализируем рынок...'):
            data = get_moex_data(tickers, start_date)
            
            if data is None or data.empty:
                st.error('Ошибка: Не удалось получить данные по указанным тикерам. Проверьте правильность написания и дату.')
            else:
                downloaded_tickers = data.columns.tolist()
                invalid_tickers = [t for t in tickers if t not in downloaded_tickers]
                
                if invalid_tickers:
                    st.warning(f"Тикеры не найдены или нет данных: {', '.join(invalid_tickers)}")
                
                final_tickers = downloaded_tickers
                
                try:
                    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
                    bounds = tuple((0, 1) for _ in range(len(final_tickers)))
                    init_guess = [1 / len(final_tickers)] * len(final_tickers)

                    weights = calculate_weights(data, cons, bounds, init_guess)
                    
                    result_data = pd.DataFrame({'Тикер': final_tickers, 'Вес %': weights})
                    
                    result_data = result_data[result_data['Вес %'] > 0.001]

                    if result_data.empty:
                        st.error("Не удалось определить веса. Попробуйте изменить список тикеров.")
                    else:
                        st.subheader("Оптимальное распределение активов")
                        
                        col1, col2 = st.columns([1, 1])

                        with col1:
                            #Круговая диаграмма
                            fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
                            ax_pie.pie(result_data['Вес %'], labels=result_data['Тикер'], 
                                       autopct='%1.1f%%', colors=plt.cm.Paired.colors)
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
                            
                        st.info(f"Минимальный риск достигнут с учётом волатильности активов.")
                
                except Exception as e:
                    st.error(f"Произошла ошибка при оптимизации: {e}")
