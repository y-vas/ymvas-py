from .stock import StockTrading
from jict import jict
import requests, yaml, os

class Ymvas:
    _auth = None
    _config = None
    _url  = 'https://api.ymvas.com'

    def __init__( self , auth = None , base = None ):
        if auth == None:
            auth = self.get_config()['auth']
            auth = '' if auth == {} else auth

        self._auth = auth
        self.stock = StockTrading( self )

        if base is not None:
            self._url = base

    def api( self , url ):
        data = requests.get(
            self._url + url,
            headers = { "API_PASS" : self._auth }
        )
        return jict(data.json())

    def get_config( self ):
        if self._config != None:
            return self._config
        main = os.popen('cd && pwd').read().strip()
        self._config = jict(f'{main}/.config/ymvas/setup.json')
        return self._config

    def set_config( self , ndict ):
        jct = self.get_config()
        for c in ndict:
            jct[c] = ndict[c]
        jct.save()

    def set_project(self,project,save=False):
        self._config['project'] = project
        if save:
            self._config.save()

    def _getpath(self , data , path ):
        keys = path.split('.')
        dt = data
        for x in keys:
            dt = dt[x]
        return dt

    def dict( self , label='@' , path = None ):
        project = self._config['project']

        info = self.api(
            f'/in/{project}/storages/data/{label}'
        )['data']

        if path is not None:
            info = self._getpath( info , path )

        return info

    def secrets( self , project = None ):
        if project == None:
            project = self._config['project']

        info = self.api(f'/in/{project}/secrets')['data']
        df = { x['key'] : yaml.safe_load(x['value']) for x in info }
        return df
