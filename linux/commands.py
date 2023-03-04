from ymvas import Ymvas
from argparse import ArgumentParser

parser = ArgumentParser(description='Ymvas command line')

parser.add_argument("--project")
parser.add_argument( "--auth"  )
parser.add_argument("--storage")
parser.add_argument("--secrets")

parser.add_argument("--label"  , default = '@' )

args = parser.parse_args()
vs = Ymvas()

if args.auth != None:
    vs.set_config({ 'auth' : args.auth })

if args.project != None:
    vs.set_config({ 'project' : args.project })

if args.storage != None:
    dict = vs.dict( args.label , args.storage )
    print( dict )

if args.secrets != None:
    dict = vs.secrets( None , args.secrets )
    print( dict )
