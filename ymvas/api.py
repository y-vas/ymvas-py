from jict import jict
from .stock.data import StockTrading

class API:
    _auth = None
    _url  = 'https://api.ymvas.com'

    def __init__( self , auth , base = None ):
        self._auth = auth
        if env is not None:
            self._url = env

    def api( self , url ):
        data = requests.get(
            self._url + url,
            headers = { "API_PASS" : self._auth }
        )
        return jict(data.json())

    def _getpath(self , data , path ):
        keys = path.split('.')
        dt = data
        for x in keys:
            dt = dt[x]
        return dt

    def dict( self , project , path = None  ):
        label = '@'

        if '/' in project:
            project, label = project.split('/')

        info = self.api(
            f'/in/vas/{project}/storages/data/{label}'
        )['data']

        if path is not None:
            info = self.-getpath(info,path)

        return info
