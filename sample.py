from pymt5 import API


if __name__ == '__main__':
    api = API('USDJPY.')

    # アカウント情報の取得
    account_info = api.get_account()
    print(account_info)

    # ローソク足の取得
    candles = api.get_candles(timeframe='M1', count=100)
    print(len(candles))
    print(candles[-1])

    # シンボル一覧を取得(指定できないものも取れちゃうかも)
    symbols = api.get_symbols()
    print(symbols)

    # Tickの取得
    last_tick = api.get_last_tick()
    bid = last_tick['bid']
    ask = last_tick['ask']
    print(last_tick)
    print('bid: {}, ask: {}'.format(bid, ask))

    # シンボルに関する詳細情報の取得
    symbol_info = api.get_symbol_info()
    print(symbol_info['point'])
    print(bid - 60 * symbol_info['point'])

    # SL/TPの設定(±6pipsの場合)
    point = symbol_info['point']
    buy_sl = bid - 60 * point
    buy_tp = bid + 60 * point

    sell_sl = ask + 60 * point
    sell_tp = ask - 60 * point

    # 成行で注文
    api.market_order(lot=0.01, side='sell',
                     stop_loss=sell_sl, take_profit=sell_tp)

    # ポジションを取得
    positions = api.get_positions()
    print(positions)

    # チケット番号を指定してポジションをクローズ(成行)
    api.close_position(positions[0]['ticket'])

    # 全ポジションをクローズ
    api.close_all_positions()

    api.shutdown()
