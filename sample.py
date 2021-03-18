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

    # 成行で注文
    api.market_order(lot=0.01, side='sell')

    # ポジションを取得
    positions = api.get_positions()
    print(positions)

    # チケット番号を指定してポジションをクローズ(成行)
    api.close_position(positions[0]['ticket'])

    # 全ポジションをクローズ
    api.close_all_positions()

    api.shutdown()
