"""Exercise the SDK HTTP service against the separately running Mock API."""
import asyncio, os
from itertools import cycle
from coc import Client
from coc.http import HTTPClient, Route
from coc.errors import Maintenance, GatewayError, Forbidden, PrivateWarLog
async def main():
    origin=os.environ['CLASH_CONTRACT_TEST_ORIGIN']
    assert origin.startswith('http://127.0.0.1:')
    client=Client()
    service=HTTPClient(client,asyncio.get_running_loop(),None,None,'fixture',1,[],100,cache_max_size=0,base_url=origin)
    service.keys=cycle(['disposable'])
    await service.create_session(None,5)
    try:
        client.http=service
        for scenario,expected in [('forbidden',PrivateWarLog),('invalidIp',Forbidden)]:
            service.base_url=origin+'/scenario/'+scenario
            try: await client.get_war_log('#2PP')
            except expected as error:
                assert (type(error) is PrivateWarLog) == (scenario == 'forbidden')
            else: raise AssertionError(scenario)
        service.base_url=origin+'/scenario/forbidden'
        for request in [lambda:client.get_league_group('#2PP'),lambda:client.get_league_war('#2PP'),lambda:client.get_raid_log('#2PP')]:
            try: await request()
            except Forbidden as error: assert type(error) is Forbidden
            else: raise AssertionError('Public CWL/raid endpoint misclassified privacy')
        for scenario,expected in [('maintenance',Maintenance),('unavailable',GatewayError)]:
            try: await service.request(Route('GET',origin,'/players/%232PP',scenario=scenario))
            except expected: pass
            else: raise AssertionError(scenario)
    finally: await service.close()
    print('PASS real Python SDK: maintenance and generic 503 remain distinct')
asyncio.run(main())
