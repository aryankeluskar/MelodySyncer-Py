import pip
import sys
package = 'uvicorn[standard]'
if not package in sys.modules:
    pip.main(['install', package])