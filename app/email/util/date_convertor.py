import datetime

import dateutil.parser



def convert_dates_to_format(dates_converter=None,req=None):
    if dates_converter is not None:
        for elem in dates_converter:
            if 'data' in req:
                if elem in req['data']:
                    if req['data'][elem] is not None:
                        if req['data'][elem] != "":
                            if req['data'][elem] != "No Access":
                                date_formatted = dateutil.parser.parse(req['data'][elem]).strftime("%d %b %Y")
                                req['data'][elem] = date_formatted    
        return req
    raise Exception("Dates not should be none in request")