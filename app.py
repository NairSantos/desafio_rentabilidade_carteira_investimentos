import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    
    with open("carteira.txt", "r") as file:
        text = file.readlines()

    wallet = {}

    for line in text:
        ticker, value = line.split("-")
        ticker = f"{ticker.strip()}.SA"
        value = float(value.strip())
        wallet[ticker] = value

    ticker_names = list(wallet.keys())

    ticker_names.append("^BVSP")
   
    initial_date = "2024-11-01"
    final_date = "2025-12-31"
    tickers = yf.Tickers(ticker_names)

    
    tbl = tickers.download(start=initial_date, end=final_date)['Close']

    
    rents = {}
    for ticker in tbl.columns:
        rents[ticker] = tbl[ticker].iloc[-1] / tbl[ticker].iloc[0] - 1

    initial_value = sum(wallet.values())
    final_value = sum(wallet[ticker] * (1 + rents[ticker]) for ticker in wallet)
    wallet_rent = final_value / initial_value - 1
    
    plt.figure(figsize=(12, 6))
    tbl.plot(title="Evolução dos Ativos da Carteira")
    plt.xlabel("Data")
    plt.ylabel("Preço Ajustado (R$)")
    plt.legend(title="Ativos", loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid()
    plt.tight_layout()

 
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('index.html', 
                           wallet_rent=wallet_rent*100,
                           index_rent=rents.get("^BVSP", 0)*100, 
                           img_base64=img_base64)  


if __name__ == '__main__':
    app.run(debug=True)