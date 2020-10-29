class stock:
    def __init__(self, i, ticker, sector, stock_return, standard_deviation, sharpe_ratio, beta):
        self.i = i
        self.ticker = ticker
        self.sector = sector
        self.stock_return = stock_return
        self.standard_deviation = standard_deviation
        self.sharpe_ratio = sharpe_ratio
        self.beta = beta
