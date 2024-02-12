from fastapi import APIRouter, Request, Form
from typing import Annotated

from connections.connection_api import APIConnection

router = APIRouter(
    prefix='/session/api-connection',
    tags=['Connection', 'API']
)


@router.post('/update-base-data/')
async def get_start_page(request:Request,  prjct_name:Annotated[str, Form()], cn_name:Annotated[str, Form()],
                   protocol:Annotated[str, Form()], host:Annotated[str, Form()], 
                   port:Annotated[str, Form()], shortcut:Annotated[str, Form()]):
    api = APIConnection()
    api.set_prjct_name(prjct_name=prjct_name)
    api.set_cn_name(cn_name=cn_name)
    await api.load_prjct_and_cn_ids()
    await api.load_base_data_from_db()
    
    api.set_protocol(protocol=protocol)
    api.set_host(host=host)
    api.set_port(port=port)
    api.set_shortcut(shortcut=shortcut)

    await api.update_entry_in_db()
    return 