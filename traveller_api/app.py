'''app.py'''

import falcon
import traveller_api.ct as ct
import traveller_api.misc as misc
import traveller_api.mt as mt
import traveller_api.t5.cargogen as t5_cargogen
import traveller_api.t5.orbit as t5_orbit
import traveller_api.util as util

api = application = falcon.API()

# Misc APIs
# api.add_route('/misc/angdia/{distance}/{diameter}', misc.AngDia())
api.add_route('/misc/angdia', misc.AngDia())

# Classic Traveller APIs
api.add_route('/ct/lbb6/star/{code}', ct.lbb6.star.Star())
api.add_route(
    '/ct/lbb6/star/{code}/orbit/{orbit_no:int}',
    ct.lbb6.orbit.Orbit())
api.add_route(
    '/ct/lbb6/star/{code}/orbit/{orbit_no:int}/planet/{uwp}',
    ct.lbb6.planet.Planet())

# MegaTraveller World Builder's Handbook APIs
api.add_route('/mt/wbh/star/{code}', mt.wbh.star.Star())
api.add_route(
    '/mt/wbh/star/{code}/orbit/{orbit_no:int}',
    mt.wbh.orbit.Orbit())

# T5 Cargogen API
api.add_route('/t5/cargogen/source/{source_uwp}', t5_cargogen.CargoGen())
api.add_route(
    '/t5/cargogen/source/{source_uwp}/market/{market_uwp}',
    t5_cargogen.CargoGen())
api.add_route(
    '/t5/cargogen/source/{source_uwp}/market/{market_uwp}/' +
    'broker/{broker_skill:int}',
    t5_cargogen.BrokerGen())

# CT Cargogen API
api.add_route('/ct/lbb2/cargogen/purchase', ct.lbb2.cargogen.Purchase())
api.add_route('/ct/lbb2/cargogen/sale', ct.lbb2.cargogen.Sale())

# T5 orbit API
api.add_route('/t5/orbit/{orbit_number}', t5_orbit.Orbit())

# Misc starcolor API
# api.add_route('/misc/starcolor/{code}', misc.StarColor())
# api.add_route('/misc/starcolour/{code}', misc.StarColor())
api.add_route('/misc/starcolor', misc.StarColor())
api.add_route('/misc/starcolour', misc.StarColor())

# Metrics
api.add_route('/metrics', util.Metrics())
