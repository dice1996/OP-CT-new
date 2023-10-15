import os
from datetime import datetime as dt


class Helpers:
    def __init__(self):
        pass

    @staticmethod
    def format_offer_id(year, month, offer_id):
        year_str = str(year)[2:]  # Take the last two digits of the year
        month_str = str(month).zfill(2)  # Pad the month with zeros if necessary
        offer_id_str = str(offer_id).zfill(4)  # Pad the offer ID with zeros to have a length of 4
        return f"{year_str}{month_str}-WEB-{offer_id_str}", f"{year_str}{month_str}-{offer_id_str}"
