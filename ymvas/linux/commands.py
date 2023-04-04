from ymvas import Ymvas
from jict import jict
import os, sys

class YmvasCommandLine:
    def __init__(self):
        self.vs = Ymvas()
        self.config = self.vs._config

    def get_project_for_current_dir(self):
        path = os.popen('pwd').read().strip()
        dirs = self.config['project_by_directory']

        for dir in dirs:
            if dir == path:
                return dirs[dir]

        for dir in dirs:
            if path.startswith(dir):
                return dirs[dir]

    def set_project_for_current_dir( self , project ):
        path = os.popen('pwd').read().strip()
        dirs = self.config['project_by_directory']
        dirs[path] = project
        self.config.save()

    def _setyvprj( self ):
        self.vs.set_project(
            self.get_project_for_current_dir()
        )

    def get_storages( self , path = None , label = '@' ):
        p = self.get_project_for_current_dir()
        info = self.vs.api(f'/in/{p}/storages/data/{label}')
        if path == '*': return info

        info = info['data']
        if path == None or path == '':
            return info

        path = path.split('.')
        for x in path: info = info[x]

        return info

    def exec(self , comm ):
        if not (isinstance(comm,list) or isinstance(comm,str)):
            print('Invalid format for execution:\n')
            print( comm )
            return

        def interpret(cm):
            if not cm.strip().startswith('vs'):
                return cm

            cm = cm[2:].strip().split(' ')
            # print( cm )

            self.interpret_command( cm )

        if isinstance(comm,list):
            comm = ' && \ \n'.join([interpret(x) for x in comm])
        else:
            comm = interpret( comm )

        out = comm + '\n'
        out += '~'*os.get_terminal_size().columns

        print( out )
        exit()

        os.system( comm )

        return out

    def interpret_command(self , args):
        if len(args) <= 0:
            print('no command')
            return

        p,l,f = '','@',''
        if '::' in args[0]:
            f, p = args[0].split('::')
        if '/' in p:
            l, p = p.split('/')

        print( f'f:{f}, p:{p}, l:{l}' )

        # vs s || vs s::{path} || vs s::{label}/{path}
        if f == 's':
            return self.get_storages(p,l)

        # vs e || vs e::{path} || vs e::{label}/{path}
        if f == 'e':
            return self.exec(
                self.get_storages(p,l)
            )

        # vs p || vs p::
        if f == 'p':
            return self.show_secrets()


    def show_secrets( self ):
        self._setyvprj()
        return self.vs.secrets()

s = YmvasCommandLine()
s.set_project_for_current_dir('vas/yovdiy')
x = s.interpret_command( sys.argv[1:] )
print( x )
