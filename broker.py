import sys, os, json, delphi, datetime
from dotenv import load_dotenv


from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.client import TradingClient

cwd = os.path.dirname(__file__)

load_dotenv()

trading_client = TradingClient(os.getenv('PAPER-API-KEY'), os.getenv('PAPER-SECRET-KEY'))
def broker(tickerName, VOSTbuySignal, VOSTsellSignal, deRisk, timeframe):

    if VOSTbuySignal or VOSTsellSignal or deRisk:
        
        if VOSTbuySignal:

            market_order_data = MarketOrderRequest(
                symbol=f'{tickerName}',
                qty=1000,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
                client_order_id=f'{tickerName}_{timeframe}'
            )

            # Market order
            market_order = trading_client.submit_order(
                order_data=market_order_data
            ) 
            print(f'{datetime.date()}\nVOST Buy Signal: Buying {tickerName}')



        if VOSTsellSignal:
            try:
                if(trading_client.get_open_position(f'{tickerName}')):
                    market_order_data = MarketOrderRequest(
                        symbol=f'{tickerName}',
                        qty=OrderSide.opposite(trading_client.get_order_by_client_id(f'{tickerName}_{timeframe}')),
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.DAY,
                        client_order_id=f'{tickerName}_{timeframe}'
                    )

                    # Market order
                    market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
                
            except:
                print(f'{datetime.date()}\nFailed while trying to act on VOSTsellSignal broker.py:51 {tickerName}')
                pass


            # Market order
            market_order = trading_client.submit_order(
                order_data=market_order_data
            ) 
            print(f'{datetime.date()}\nVOST Sell Signal: Selling {tickerName}')



        if deRisk:
            try:
                if(trading_client.get_open_position(f'{tickerName}')):
                    market_order_data = MarketOrderRequest(
                        symbol="f'{tickerName}'",
                        qty=333,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.DAY,
                        client_order_id=f'{tickerName}_{timeframe}'
                    )

                    # Market order
                    market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
                    
                    print(f'{datetime.date()}\nDe-Risking {tickerName}')
            except:
                print(f'{datetime.date()}\nFailed while trying to act on deRisk signal broker.py:81 {tickerName}')
                pass

        sys.stdout.flush()
    else:
        print(f'No action taken on {tickerName}. Current Time: {datetime.datetime.now()}')
