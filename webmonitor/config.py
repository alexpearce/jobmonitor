"""
Configuration for the WebMonitor server.
"""
# Application name, used in page titles etc.
APP_NAME = 'Web Monitor'

# Run the server in debug mode?
DEBUG = False

# Where static assets are stored (images, stylesheets, and JavaScripts)
# TODO where is this relative to? what happens if the config file moves?
ASSETS_DIRECTORY = './static'

# Where ROOT files are stored
FILES_DIRECTORY = '{0}/files'.format(ASSETS_DIRECTORY)

# Mappings of parent paths to their default children
DEFAULT_CHILDREN = {
    '': 'examples',
    'examples': 'examples/table',
    'examples/tabs': 'examples/tabs/tab1'
}