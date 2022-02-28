import investpy

df = investpy.get_stock_historical_data(stock='PMG',
                                        country='Colombia',
                                        from_date='01/01/2020',
                                        to_date='01/01/2022')
print(df.head())