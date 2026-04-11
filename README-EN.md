# 📈 MOEX Portfolio Optimizer (Markowitz Model)

[PO.webm](https://github.com/user-attachments/assets/15015b8f-b1ce-4d9c-9207-a819bd75e70a)


Russian version -> [here](https://github.com/Maradelli/Portfolio-optimization/blob/main/README.md)

An interactive web application for optimizing an investment portfolio based on shares of the Moscow Stock Exchange. The project implements **Harry Markowitz's Modern Portfolio Theory** to find a portfolio with minimal risk. 
## ✨ Main features
* **Data automation**: Downloading quotes directly from MOEX using the API ISS.
* **Smart Risk-Free Rate**: Dynamic collecting of the actual key rate from the official website of Central Bank of the Russian Federation using web scrapping. 
* **Algorithmic optimization**: Using the `SLSQP` method to minimize portfolio volatility under specified constraints.
* **Interactive interface**: Built on Streamlit, it allows you to change the composition of tickers, budget and see the result instantly.
* **Clean visualization**: Automatic filtering of assets with near-zero weight for ease of analysis.

## 🛠 Technology stack
* **Python 3.13**
* **Streamlit**: Web interface.
* **Pandas & NumPy**: Data processing and matrix calculations.
* **SciPy (Optimize)**: Mathematical optimization.
* **Matplotlib**: Visualization of the distribution of shares.
* **Requests & APIMOEX**: Interaction with financial APIs.

## 📐 How it works
1. The program collects historical closing prices for the selected tickers.
2. Calculating the logarithmic return, average return and asset covariance matrix.
3. The program goes to the website cbr.ru and extracts the current key rate as a risk-free return ($R_f$).
4. The problem of minimizing the risk function (volatility) is solved:
   $$\sigma_p = \sqrt{w^T \Sigma w}$$
   with condition $\sum w_i = 1$.

## 🚀 Project launch
1. Clone the repository:
   git clone [https://github.com/Maradelli/Portfolio-optimization.git](https://github.com/Maradelli/Portfolio-optimization.git)
2. Install the dependencies:
   pip install -r requirements.txt
3. Run the application:
   streamlit run App.py

## Structure of the project
- `App.py`: interface of the application and visualization
- `Functions.py`: mathematical core (calculations and data parsing)
- `Research.ipynb`: primary analysis

*Developed as part of the study of data analysis and financial mathematics. The project will be finalized.*
