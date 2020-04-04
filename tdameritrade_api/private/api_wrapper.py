import datetime
import json

class BaseTDAAPIWrapper:
    def __init__(self, api_key, session, account_id=None):
        self.api_key = api_key
        self.session = session
        self.account_id = account_id

    def __account_id(self):
        if self.account_id is None:
            raise ValueError('client initialized without account ID')
        return self.account_id


    def __format_datetime(self, dt):
        '''Formats datetime objects appropriately, depending on whether they are 
        naive or timezone-aware'''
        tz_offset = dt.strftime('%z')
        tz_offset = tz_offset if tz_offset else '+0000'

        return dt.strftime('%Y-%m-%dT%H:%M:%S') + tz_offset


    def __datetime_as_millis(self, dt):
        'Converts datetime objects to compatible millisecond values'
        return int(dt.timestamp() * 1000)

    
    def __get_request(self, path, params):
        dest = 'https://api.tdameritrade.com' + path
        resp = self.session.get(dest, params=params)
        return resp


    def __post_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.post(dest, json=data)


    def __put_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.put(dest, json=data)


    def __delete_request(self, path):
        dest = 'https://api.tdameritrade.com' + path
        return self.session.delete(dest)

    
    ############################################################################
    # Orders


    def cancel_order(self, order_id, account_id):
        'Cancel a specific order for a specific account.'
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__delete_request(path)


    def get_order(self, order_id, account_id):
        'Get a specific order for a specific account.'
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__get_request(path)


    def __make_order_query(self,
            max_results=None,
            from_entered_datetime=None,
            to_entered_datetime=None,
            status=None,
            statuses=None):
        if from_entered_datetime is None:
            from_entered_datetime = datetime.datetime.min
        if to_entered_datetime is None:
            to_entered_datetime = datetime.datetime.utcnow()

        params = {
            'fromEnteredTime': self.__format_datetime(from_entered_datetime),
            'toEnteredTime': self.__format_datetime(to_entered_datetime),
        }

        if max_results:
            params['maxResults'] = max_results

        if status is not None and statuses is not None:
            raise ValueError('at most one of status or statuses may be set')
        if status:
            params['status'] = status
        if statuses:
            params['status'] = ','.join(statuses)

        return params


    def get_orders_by_path(self,
            account_id,
            max_results=None,
            from_entered_datetime=None, 
            to_entered_datetime=None,
            status=None,
            statuses=None):
        'Orders for a specific account.'
        path = '/v1/accounts/{}/orders'.format(account_id)
        return self.__get_request(path, self.__make_order_query(
            max_results, from_entered_datetime, to_entered_datetime, status, 
            statuses))


    def get_orders_by_query(self,
            max_results=None,
            from_entered_datetime=None, 
            to_entered_datetime=None,
            status=None,
            statuses=None):
        'Orders for a specific account.'
        path = '/v1/orders'
        return self.__get_request(path, self.__make_order_query(
            max_results, from_entered_datetime, to_entered_datetime, status, 
            statuses))


    def place_order(self, account_id, order_spec):
        'Place an order for a specific account.'
        path = '/v1/accounts/{}/orders'.format(account_id)
        return self.__post_request(path, order_spec)


    def replace_order(self, account_id, order_id, order_spec):
        '''Replace an existing order for an account. The existing order will be 
        replaced by the new order. Once replaced, the old order will be canceled 
        and a new order will be created.'''
        path = '/v1/accounts/{}/orders/{}'.format(account_id, order_id)
        return self.__post_request(path, order_spec)


    ############################################################################
    # Saved Orders


    def create_saved_order(self, account_id, order_spec):
        'Save an order for a specific account.'
        path = '/v1/accounts/{}/savedorders'.format(account_id)
        return self.__post_request(path, order_spec)


    def delete_saved_order(self, account_id, order_id):
        'Delete a specific saved order for a specific account.'
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__delete_request(path)


    def get_saved_order(self, account_id, order_id):
        'Specific saved order by its ID, for a specific account.'
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__get_request(path, {})


    def get_saved_orders_by_path(self, account_id):
        'Saved orders for a specific account.'
        path = '/v1/accounts/{}/savedorders'.format(account_id)
        return self.__get_request(path, {})


    def replace_saved_order(self, account_id, order_id, order_spec):
        '''Replace an existing saved order for an account. The existing saved 
        order will be replaced by the new order.'''
        path = '/v1/accounts/{}/savedorders/{}'.format(account_id, order_id)
        return self.__put_request(path, order_spec)


    ############################################################################
    # Accounts


    def get_account(self, account_id, fields=None):
        'Account balances, positions, and orders for a specific account.'
        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        path = '/v1/accounts/{}'.format(account_id)
        return self.__get_request(path, params)


    def get_accounts(self, fields=None):
        'Account balances, positions, and orders for a specific account.'
        params = {}
        if fields:
            params['fields'] = ','.join(fields)

        path = '/v1/accounts'
        return self.__get_request(path, params)


    ############################################################################
    # Instruments


    def search_instruments(self, symbol, projection):
        'Search or retrieve instrument data, including fundamental data.'
        params = {
                'apikey': self.api_key,
                'symbol': symbol,
                'projection': projection,
        }

        path = '/v1/instruments'
        return self.__get_request(path, params)


    def get_instrument(self, cusip):
        'Get an instrument by CUSIP'
        if not isinstance(cusip, str):
            raise ValueError('CUSIPs must be passed as strings to preserve ' +
                             'leading zeroes')

        params = {
                'apikey': self.api_key,
        }

        path = '/v1/instruments/{}'.format(cusip)
        return self.__get_request(path, params)


    ############################################################################
    # Market Hours


    def get_hours_for_multiple_markets(self, markets, date):
        'Retrieve market hours for specified markets'
        params = {
                'apikey': self.api_key,
                'markets': ','.join(markets),
                'date': self.__format_datetime(date),
        }
        print(params)

        path = '/v1/marketdata/hours'
        return self.__get_request(path, params)


    def get_hours_for_a_single_market(self, market, date):
        'Retrieve market hours for specified single market'
        params = {
                'apikey': self.api_key,
                'date': self.__format_datetime(date),
        }
        print(params)

        path = '/v1/marketdata/{}/hours'.format(market)
        return self.__get_request(path, params)

    
    ############################################################################
    # Movers


    def get_movers(self, index, direction, change):
        'Search or retrieve instrument data, including fundamental data.'
        params = {
                'apikey': self.api_key,
                'direction': direction,
                'change': change,
        }

        path = '/v1/marketdata/{}/movers'.format(index)
        return self.__get_request(path, params)


    ############################################################################
    # Option Chains


    def get_option_chain(
            self,
            symbol,
            contract_type='ALL',
            strike_count=None,
            include_quotes=False,
            strategy=None,
            interval=None,
            strike=None,
            strike_range='ALL',
            strike_from_date=None,
            strike_to_date=None,
            volatility=None,
            underlying_price=None,
            interest_rate=None,
            days_to_expiration=None,
            exp_month='ALL',
            option_type='ALL'):
        'Get option chain for an optionable Symbol'
        params = {
                'apikey': self.api_key,
                'symbol': symbol,
                'includeQuotes': include_quotes,
                'contractType': contract_type,
                'range': strike_range,
                'expMonth': exp_month,
                'optionType': option_type,
        }

        if strike_count is not None:
            params['strikeCount'] = strike_count
        if strategy is not None:
            params['strategy'] = strategy
        if interval is not None:
            params['interval'] = interval
        if strike is not None:
            params['strike'] = strike
        if strike_from_date is not None:
            params['fromDate'] = self.__format_datetime(strike_from_date)
        if strike_to_date is not None:
            params['toDate'] = self.__format_datetime(strike_to_date)
        if volatility is not None:
            params['volatility'] = volatility
        if underlying_price is not None:
            params['underlyingPrice'] = underlying_price
        if interest_rate is not None:
            params['interestRate'] = interest_rate
        if days_to_expiration is None:
            params['daysToExpiration'] = days_to_expiration

        path = '/v1/marketdata/chains'
        return self.__get_request(path, params)


    ############################################################################
    # Price History


    def get_price_history(
            self,
            symbol,
            period_type='day',
            num_periods=None,
            frequency_type=None,
            frequency=1,
            start_date=None,
            end_date=None,
            need_extended_hours_data=False):
        'Get price history for a symbol'
        params = {
                'apikey': self.api_key,
                'symbol': symbol,
                'periodType': period_type,
                'frequency': frequency,
                'needExtendedHoursData': need_extended_hours_data,
        }

        if num_periods is not None:
            params['period'] = num_periods
        if frequency_type is not None:
            params['frequencyType'] = frequency_type
        if start_date is not None:
            params['startDate'] = self.__datetime_as_millis(start_date)
        if end_date is not None:
            params['endDate'] = self.__datetime_as_millis(end_date)

        path = '/v1/marketdata/{}/pricehistory'.format(symbol)
        return self.__get_request(path, params)


    ############################################################################
    # Quotes


    def get_quote(self, symbol):
        'Get quote for a symbol'
        params = {
                'apikey': self.api_key,
        }

        path = '/v1/marketdata/{}/quotes'.format(symbol)
        return self.__get_request(path, params)


    def get_quotes(self, symbols):
        'Get quote for a symbol'
        params = {
                'apikey': self.api_key,
                'symbol': ','.join(symbols)
        }

        path = '/v1/marketdata/quotes'
        return self.__get_request(path, params)
