'''angdia.py'''

from math import atan2, pi
import json
import logging
import os
import re
import falcon
from .. import Config
from .. import DB
from .db import Schemas


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

KONFIG = Config()
config = KONFIG.config['traveller_api.misc']


class AngDia(object):
    '''Angular diameter API'''
    # GET /misc/angdia/<distance>/<diameter>
    # Return ang_dia (deg), ang_dia (rad)

    def on_get(self, req, resp, distance, diameter):
        '''Return angular diameter of object diameter <diameter> at range <distance>
        GET /misc/angdia/<distance>/<diameter>

        Returns
        {
            "ang_dia_deg": <angular diameter (degrees)>,
            "ang_dia_rad": <angular diameter (radians)>
        }
        '''
        distance = float(distance)
        diameter = float(diameter)
        angdia_deg = round(
            atan2(diameter, distance) * 180 / pi, 3)
        angdia_rad = round(
            atan2(diameter, distance))
        doc = {
            'ang_dia_deg': angdia_deg,
            'ang_dia_rad': angdia_rad
        }
        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200


class StarColor(object):
    '''Star color API
    GET /misc/starcolor/<code>
    Return (r, G, B) corresponding to star color'''
    # See star_color.sqlite for RGB

    def __init__(self):
        self.code = None
        self.rgb = {
            'red': None,
            'blue': None,
            'green': None
        }
        self.clear_data()
        # Path
        sqlite_file = '{}/{}'.format(
            os.path.dirname(os.path.realpath(__file__)),
            config.get('dbfile'))
        self.db = DB(sqlite_file)
        self.session = self.db.session()

    def on_get(self, req, resp, code):
        '''Return (R, G, B) colour for star of type <type><decimal><size
        GET /misc/starcolor/<code>

        Returns
        {
            "code": <code>,
            "RGB": {"red": <red>, "blue": <blue>, "green": <green>}
        }
        '''
        self.clear_data()
        self._validate_code(code)
        try:
            assert self.code is not None
            assert self.code != ''
        except AssertionError:
            raise falcon.HTTPUnprocessableEntity(
                title='Unprocessable request',
                description='Invalid code {}'.format(code))
        self.get_details()
        doc = {
            'code': self.code,
            'rgb': self.rgb
        }
        resp.body = json.dumps(doc)
        resp.status = falcon.HTTP_200

    def clear_data(self):
        '''Clear data on new request'''
        self.code = ''
        self.rgb = {'red': None, 'green': None, 'blue': None}

    def get_details(self):
        '''Get RGB details for code from DB'''
        LOGGER.debug('code = %s', self.code)
        details = self.session.query(Schemas.StarColorTable).\
            filter_by(code=self.code).first()
        LOGGER.debug('starcolor = %s', details)
        if details:
            self.rgb['red'] = details.red
            self.rgb['green'] = details.green
            self.rgb['blue'] = details.blue

    def _validate_code(self, code):
        '''Validate code -> type, decimal, size'''
        LOGGER.debug('code = %s', code)
        if code:
            if code.endswith('D'):
                self._validate_code_dwarf(code)
            else:
                self._validate_code_star(code)

    def _validate_code_star(self, code):
        '''Validate code for non-dwarf'''
        mtch = re.match(
            r'([OBAFGKM])([0-9])\s*([IVDab]{1,3}$)',
            code)
        if mtch:
            LOGGER.debug('Code matches RE')
            typ = mtch.group(1)
            decimal = int(mtch.group(2))
            if mtch.group(3) in ['Ia', 'Ib', 'II', 'III', 'IV', 'V', 'VI']:
                size = mtch.group(3)
            else:
                raise TypeError
            LOGGER.debug(
                'type = %s decimal = %s size = %s',
                typ, decimal, size)

            # Check for invalid types
            if size == 'IV':
                LOGGER.debug('size = IV')
                # M[0-9] IV not possible, use V instead
                if typ == 'M':
                    LOGGER.debug('type = M, setting size=V')
                    size = 'V'
                # K[5-9] IV not possible, use V instead
                if typ == 'K' and decimal >= 5:
                    LOGGER.debug('type = K, size = 5-9, setting size=V')
                    size = 'V'
            if size == 'VI':
                # B[0-9] VI not possible, use V instead
                if typ == 'B':
                    size = 'V'
                # F[0-4] VI not possible, use V instead
                if typ == 'F' and decimal <= 4:
                    size = 'V'
            self.code = '{}{} {}'.format(typ, decimal, size)

    def _validate_code_dwarf(self, code):
        '''Validate code for dwarf'''
        mtch = re.match(r'([OBAFGKM])\s*D', code)
        if mtch:
            LOGGER.debug('code matches RE')
            typ = mtch.group(1)
            self.code = '{}D'.format(typ)
