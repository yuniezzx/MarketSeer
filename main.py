from data_sources import *
import akshare as ak


if __name__ == '__main__':
    stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol="SH601127")
    print(stock_individual_basic_info_xq_df)



