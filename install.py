import pip
import sys
package = 'google-api-python-client'
if not package in sys.modules:
    pip.main(['install', package])