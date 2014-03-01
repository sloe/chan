
import glob
import os

# Construct __all__ to contain all files startign with sloeplugin_)
__all__ = [os.path.splitext(os.path.basename(x))[0] for x in 
           glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sloeplugin*"))]
