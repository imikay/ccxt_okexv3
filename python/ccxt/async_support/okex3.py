# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import hashlib
import math
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import NotSupported
from ccxt.base.errors import DDoSProtection
from ccxt.base.errors import ExchangeNotAvailable
from ccxt.base.errors import InvalidNonce


class okex3 (Exchange):

    def describe(self):
        return self.deep_extend(super(okex3, self).describe(), {
            'id': 'okex3',
            'name': 'okex3',
            'countries': ['CN'],
            'rateLimit': 2000,
            'userAgent': self.userAgents['chrome39'],
            'version': 'v3',
            'accounts': None,
            'accountsById': None,
            'hostname': 'okex.com',
            'has': {
                'CORS': False,
                'fetchDepositAddress': False,
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchClosedOrders': True,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchOrderBook': True,
                'fetchOrderBooks': False,
                'fetchTradingLimits': False,
                'withdraw': False,
                'fetchCurrencies': False,
            },
            'timeframes': {
                '1m': 60,
                '3m': 180,
                '5m': 300,
                '15m': 900,
                '30m': 1800,
                '1h': 3600,
                '1d': 86400,
                '1w': 604800,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766791-89ffb502-5ee5-11e7-8a5b-c5950b68ac65.jpg',
                'api': {
                    'spot': 'https://www.okex.com/api/spot/v3',
                    'account': 'https://www.okex.com/api/account/v3',
                },
                'www': 'https://www.okex.com',
                'doc': 'https://www.okex.com/docs/en',
                'fees': 'https://www.okex.com/pages/products/fees.html',
            },
            'api': {
                'spot': {
                    'get': [
                        'instruments',
                        'instruments/{id}/book',
                        'instruments/{id}/ticker',
                        'instruments/{id}/trades',
                        'orders/{id}',
                        'orders',
                        'orders_pending',
                        'instruments/{id}/candles',
                    ],
                    'post': [
                        'orders',
                        'cancel_orders/{id}',
                    ],
                },
                'account': {
                    'get': [
                        'wallet',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'maker': 0.001,
                    'taker': 0.001,
                },
            },
            'limits': {
                'amount': {'min': 0.01, 'max': 100000},
            },
            'options': {
                'createMarketBuyOrderRequiresPrice': True,
                'limits': {},
            },
            'exceptions': {
                '400': NotSupported,  # Bad Request
                '401': AuthenticationError,
                '405': NotSupported,
                '429': DDoSProtection,  # Too Many Requests, exceed api request limit
                '1002': ExchangeNotAvailable,  # System busy
                '1016': InsufficientFunds,
                '3008': InvalidOrder,
                '6004': InvalidNonce,
                '6005': AuthenticationError,  # Illegal API Signature
            },
        })

    async def fetch_markets(self, params={}):
        response = await self.spotGetInstruments()
        result = []
        markets = response
        for i in range(0, len(markets)):
            market = markets[i]
            id = market['instrument_id']
            baseId = market['base_currency']
            quoteId = market['quote_currency']
            base = baseId.upper()
            base = self.common_currency_code(base)
            quote = quoteId.upper()
            quote = self.common_currency_code(quote)
            symbol = base + '/' + quote
            precision = {
                'price': self.safe_float(market, 'tick_size'),
                'amount': self.safe_float(market, 'size_increment'),
            }
            limits = {
                'price': {
                    'min': math.pow(10, -precision['price']),
                    'max': math.pow(10, precision['price']),
                },
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': True,
                'precision': precision,
                'limits': limits,
                'info': market,
            })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.accountGetWallet(params)
        result = {'info': response}
        balances = response
        for i in range(0, len(balances)):
            balance = balances[i]
            currencyId = balance['currency']
            code = currencyId.upper()
            if currencyId in self.currencies_by_id:
                code = self.currencies_by_id[currencyId]['code']
            else:
                code = self.common_currency_code(code)
            account = self.account()
            account['free'] = float(balance['available'])
            account['total'] = float(balance['balance'])
            account['used'] = float(balance['hold'])
            result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol=None, limit=5, params={}):
        await self.load_markets()
        request = self.extend({
            'symbol': self.market_id(symbol),
            'size': limit,
            'id': self.market_id(symbol),
        }, params)
        response = await self.spotGetInstrumentsIdBook(request)
        orderbook = response
        return self.parse_order_book(orderbook, orderbook['timestamp'], 'bids', 'asks', 0, 1)

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        ticker = await self.spotGetInstrumentsIdTicker({'id': self.market_id(symbol)})
        return self.parse_ticker(ticker, market)

    def parse_ticker(self, ticker, market=None):
        timestamp = ticker['timestamp']
        last = ticker['last']
        return {
            'symbol': market['symbol'],
            'timestamp': self.parse8601(timestamp),
            'datetime': self.iso8601(timestamp),
            'high': ticker['high_24h'],
            'low': ticker['low_24h'],
            'bid': ticker['bid'],
            'bidVolume': None,
            'ask': ticker['ask'],
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': ticker['base_volume_24h'],
            'quoteVolume': ticker['quote_volume_24h'],
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        symbol = None
        if market is not None:
            symbol = market['symbol']
        datetime = trade['time']
        side = trade['side'].lower()
        orderId = self.safe_string(trade, 'trade_id')
        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'size')
        cost = price * amount
        fee = None
        return {
            'id': orderId,
            'info': trade,
            'timestamp': self.parse8601(datetime),
            'datetime': datetime,
            'symbol': symbol,
            'type': None,
            'order': orderId,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
        }

    async def fetch_trades(self, symbol, since=None, limit=50, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'symbol': market['id'],
            'limit': limit,
            'id': market['id'],
        }
        response = await self.spotGetInstrumentsIdTrades(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type == 'market':
            # for market buy it requires the amount of quote currency to spend
            if side == 'buy':
                if self.options['createMarketBuyOrderRequiresPrice']:
                    if price is None:
                        raise InvalidOrder(self.id + " createOrder() requires the price argument with market buy orders to calculate total order cost(amount to spend), where cost = amount * price. Supply a price argument to createOrder() call if you want the cost to be calculated for you from price and amount, or, alternatively, add .options['createMarketBuyOrderRequiresPrice'] = False to supply the cost in the amount argument(the exchange-specific behaviour)")
                    else:
                        amount = amount * price
        await self.load_markets()
        orderType = type
        request = {
            'instrument_id': self.market_id(symbol),
            'size': self.amount_to_precision(symbol, amount),
            'side': side,
            'type': orderType,
        }
        if type == 'limit':
            request['price'] = self.price_to_precision(symbol, price)
        else:
            request['notional'] = self.amount_to_precision(symbol, amount)
        result = await self.spotPostOrders(self.extend(request, params))
        return {
            'info': result,
            'id': result['order_id'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        params['instrument_id'] = self.market(symbol)['id']
        response = await self.spotPostCancelOrdersId(self.extend({
            'id': id,
        }, params))
        order = self.parse_order(response)
        return self.extend(order, {
            'id': id,
            'status': 'canceled',
        })

    def parse_order_status(self, status):
        statuses = {
            'open': 'open',
            'ordering': 'open',
            'canceled': 'canceled',
            'cancelled': 'canceled',
            'canceling': 'canceled',
            'part_filled': 'open',
            'filled': 'closed',
            'failure': 'canceled',
        }
        if status in statuses:
            return statuses[status]
        return status

    def parse_order(self, order, market=None):
        id = self.safe_string(order, 'order_id')
        side = self.safe_string(order, 'side')
        status = self.parse_order_status(self.safe_string(order, 'status'))
        symbol = None
        if market is None:
            marketId = self.safe_string(order, 'instrument_id')
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        orderType = self.safe_string(order, 'type')
        timestamp = self.safe_string(order, 'timestamp')
        timestamp = self.parse8601(timestamp)
        amount = self.safe_float(order, 'size')
        filled = self.safe_float(order, 'filled_size')
        remaining = None
        price = self.safe_float(order, 'price')
        cost = self.safe_float(order, 'filled_notional')
        if filled is not None:
            if amount is not None:
                remaining = amount - filled
            if cost is None:
                if price is not None:
                    cost = price * filled
            elif (cost > 0) and(filled > 0):
                price = cost / filled
        feeCurrency = None
        if market is not None:
            symbol = market['symbol']
            feeCurrency = market['base'] if (side == 'buy') else market['quote']
        feeCost = 0
        result = {
            'info': order,
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'symbol': symbol,
            'type': orderType,
            'side': side,
            'price': price,
            'cost': cost,
            'amount': amount,
            'remaining': remaining,
            'filled': filled,
            'average': None,
            'status': status,
            'fee': {
                'cost': feeCost,
                'currency': feeCurrency,
            },
            'trades': None,
        }
        return result

    async def fetch_order(self, id, symbol=None, params={}):
        await self.load_markets()
        request = self.extend({
            'instrument_id': self.market(symbol)['id'],
            'id': id,
        }, params)
        response = await self.spotGetOrdersId(request)
        return self.parse_order(response)

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        symbol = self.market(symbol)['id']
        result = await self.spotGetOrdersPending(symbol, since, limit)
        return self.parse_orders(result)

    async def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        result = await self.fetch_orders(symbol, since, limit, {'status': 'filled'})
        return result

    async def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'instrument_id': market['id'],
            'status': 'all',
        }
        if limit is not None:
            request['limit'] = limit
        response = await self.spotGetOrders(self.extend(request, params))
        return self.parse_orders(response, market, since, limit)

    def parse_ohlcv(self, ohlcv, market=None, timeframe='1m', since=None, limit=None):
        return [
            self.parse8601(ohlcv[0]),
            ohlcv[1],
            ohlcv[2],
            ohlcv[3],
            ohlcv[4],
            ohlcv[5],
        ]

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=100, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = self.extend({
            'id': market['id'],
            'granularity': self.timeframes[timeframe],
        }, params)
        if since:
            request['start'] = self.iso8601(since)
        response = await self.spotGetInstrumentsIdCandles(request)
        return self.parse_ohlcvs(response, market, timeframe, since, limit)

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='spot', method='GET', params={}, headers=None, body=None):
        request = '/'
        request += self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        url = self.urls['api'][api] + request
        # console.log(path, request, url)
        nonce = str(self.nonce())
        timestamp = self.iso8601(nonce) or ''
        payloadPath = url.replace(self.urls['www'], '')
        payload = timestamp + method
        if payloadPath:
            payload += payloadPath
        if method == 'GET':
            if query:
                url += '?' + self.urlencode(query)
                payload += '?' + self.urlencode(query)
        else:
            payload += self.json(query)
            body = self.json(query)
        signature = ''
        if payload and self.secret:
            signature = self.hmac(payload, self.secret, hashlib.sha256, 'base64')
        headers = {
            'OK-ACCESS-KEY': self.apiKey,
            'OK-ACCESS-SIGN': self.decode(signature),
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.password,
            'Content-Type': 'application/json',
        }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
