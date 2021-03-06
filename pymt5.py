import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone


class API:
    symbol = None

    timeframe = {
        'M1': mt5.TIMEFRAME_M1,
        'M2': mt5.TIMEFRAME_M2,
        'M3': mt5.TIMEFRAME_M3,
        'M4': mt5.TIMEFRAME_M4,
        'M5': mt5.TIMEFRAME_M5,
        'M6': mt5.TIMEFRAME_M6,
        'M10': mt5.TIMEFRAME_M10,
        'M12': mt5.TIMEFRAME_M12,
        'M15': mt5.TIMEFRAME_M15,
        'M20': mt5.TIMEFRAME_M20,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H2': mt5.TIMEFRAME_H2,
        'H3': mt5.TIMEFRAME_H3,
        'H4': mt5.TIMEFRAME_H4,
        'H6': mt5.TIMEFRAME_H6,
        'H8': mt5.TIMEFRAME_H8,
        'H12': mt5.TIMEFRAME_H12,
        'D1': mt5.TIMEFRAME_D1,
        'W1': mt5.TIMEFRAME_W1,
        'MN1': mt5.TIMEFRAME_MN1,
    }

    def __init__(self, symbol, login, password, server):
        if not mt5.initialize(login=login, password=password, server=server):
            print('Initialize failed, error code={}'.format(mt5.last_error()))
            raise Exception
        self.symbol = symbol

    def __calc_offset(self):
        now = datetime.now()
        london = timezone('Europe/London')
        is_summer_time = bool(now.astimezone(london).dst())

        # The time difference is GMT+3 in summer time and GMT+2 in winter time.
        offset = 3 if is_summer_time else 2

        return offset

    def get_account(self):
        """Get info on the current trading account.

        Returns:
            dict: Account information
        """
        account_info = mt5.account_info()._asdict()
        return account_info

    def get_terminal_info(self):
        return

    def get_symbols(self):
        """Get all financial instruments from the MetaTrader5 terminal.

        Returns:
            list: List of symbol names
        """
        symbols = mt5.symbols_get()
        result = [s.name for s in symbols]
        return result

    def get_symbol_info(self, symbol=None):
        """Get data on the specified financial instrument.

        Args:
            symbol (str, optional): Financial instrument name. Defaults to None.

        Returns:
            dict: Symbol information
        """
        instrument = symbol if symbol else self.symbol
        return mt5.symbol_info(instrument)._asdict()

    def get_last_tick(self, symbol=None):
        """Get the last tick for the specified financial instrument.

        Args:
            symbol (str, optional): Financial instrument name. Defaults to None.

        Returns:
            dict: [description]
        """
        instrument = symbol if symbol else self.symbol
        return mt5.symbol_info_tick(instrument)._asdict()

    def get_candles(self, timeframe, count=100):
        """Get bars from the MetaTrader5 terminal starting from the current one.

        Args:
            timeframe (str): M1/M2/M3/M4/M5/M6/M10/M12/M15/M20/M30/H1/H2/H3/H4/H6/H8/H12/D1/W1/MN1
            count (int, optional): Specify the number of bars to retrieve. Defaults to 100.
        """
        offset = self.__calc_offset()

        result = []
        candles = mt5.copy_rates_from_pos(
            self.symbol, self.timeframe[timeframe], 0, count)

        for candle in candles:
            timestamp = (datetime.fromtimestamp(
                candle[0]) - timedelta(hours=offset)).isoformat()
            row = {
                'timestamp': timestamp,
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5],
                'spread': candle[6]
            }
            result.append(row)

        return result

    def get_candles_range(self, timeframe, start_date, end_date, symbol=None):

        instrument = symbol if symbol else self.symbol
        result = mt5.copy_rates_range(
            instrument, timeframe, start_date, end_date)

        return result

    def get_orders(self):
        """Get active order information

        Returns:
            list: Active orders
        """
        orders = mt5.orders_get(symbol=self.symbol)
        result = [order._asdict() for order in orders]
        return result

    def get_positions(self):
        """Get open position information

        Returns:
            list: Open positions
        """
        positions = mt5.positions_get(symbol=self.symbol)
        result = [position._asdict() for position in positions]
        return result

    def market_order(self, lot, side, magic=None, stop_loss=None, take_profit=None):
        """Place an order in the market.

        Args:
            lot (float): Specify the order size.
            side (str): Specify whether to 'buy' or 'sell'.
            magic (int): EA ID. Defaults to None.
            stop_loss (float, optional): Stop loss order price. Defaults to None.
            take_profit (float, optional): Take profit order price. Defaults to None.

        Returns:
            dict: Order information
        """

        order_type = mt5.ORDER_TYPE_BUY if side == 'buy' else mt5.ORDER_TYPE_SELL

        params = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': lot,
            'type': order_type,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC
        }
        if magic:
            params['magic'] = magic
        if stop_loss:
            params['sl'] = stop_loss
        if take_profit:
            params['tp'] = take_profit

        response = mt5.order_send(params)._asdict()
        return response

    def limit_order(self, lot, side, price, magic=None, stop_loss=None, take_profit=None):
        """Place a limit order

        Args:
            lot (float): Specify the order size.
            side (str): Specify whether to 'buy' or 'sell'.
            price (float): Limit order price.
            magic (int): EA ID. Defaults to None.
            stop_loss (float, optional): Stop loss order price. Defaults to None.
            take_profit (float, optional): Take profit order price. Defaults to None.

        Returns:
            dict: Order information
        """
        order_type = mt5.ORDER_TYPE_BUY_LIMIT if side == 'buy' else mt5.ORDER_TYPE_SELL_LIMIT

        params = {
            'action': mt5.TRADE_ACTION_PENDING,
            'symbol': self.symbol,
            'volume': lot,
            'type': order_type,
            'price': price,
            'type_time': mt5.ORDER_TIME_GTC,
        }

        if magic:
            params['magic'] = magic
        if stop_loss:
            params['sl'] = stop_loss
        if take_profit:
            params['tp'] = take_profit

        response = mt5.order_send(params)._asdict()
        return response

    def cancel_order(self, ticket):
        """Cancel an active order by specifying the ticket number.

        Args:
            ticket (int): Ticket number to cancel the order.

        Returns:
            dict: Order response
        """
        params = {
            'action': mt5.TRADE_ACTION_REMOVE,
            'order': ticket
        }
        response = mt5.order_send(params)._asdict()
        return response

    def cancel_all_orders(self):
        """Cancel all active orders.

        Returns:
            dict: Order response
        """
        orders = self.get_orders()
        result = []
        for order in orders:
            ticket = order['ticket']
            params = {
                'action': mt5.TRADE_ACTION_REMOVE,
                'order': ticket
            }
            response = mt5.order_send(params)._asdict()
            result.append(response)
        return result

    def close_position(self, ticket):
        """Close the position of the specified ticket.

        Args:
            ticket (int): Ticket number included in position information

        Returns:
            dict: Order information
        """

        position = mt5.positions_get(ticket=ticket)[0]._asdict()
        side = mt5.ORDER_TYPE_SELL if position['type'] == 0 else mt5.ORDER_TYPE_BUY

        params = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': position['volume'],
            'position': position['ticket'],
            'type': side,
            'type_time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC
        }
        response = mt5.order_send(params)._asdict()
        return response

    def close_all_positions(self):
        """Close all positions.

        Returns:
            list: Close order information
        """

        result = []
        positions = self.get_positions()
        for position in positions:
            ticket = position['ticket']
            order_type = mt5.ORDER_TYPE_SELL if position['type'] == 0 else mt5.ORDER_TYPE_BUY
            lot = position['volume']
            params = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': self.symbol,
                'volume': lot,
                'position': ticket,
                'type': order_type,
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            response = mt5.order_send(params)._asdict()
            result.append(response)

        return result

    def shutdown(self):
        """Close the previously established connection to the MetaTrader5 terminal.
        """
        mt5.shutdown()
