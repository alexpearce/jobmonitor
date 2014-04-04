# Flask API: http://flask.pocoo.org/docs/api/
from flask import (
    # Creating app instances
    Flask,
    # Rendering Jinja2 templates
    render_template,
    # Serving assets
    send_from_directory,
    # Serving custom filetypes
    send_file,
    # JSON encode Python dictionaries
    jsonify,
    # Set and access variables global to the app instance and views
    g,
    # Raise HTTP error code exceptions
    abort
)
# So we can catch Jinja2 exception
from jinja2.exceptions import TemplateNotFound

# ROOT tasks
import tasks

# Define the app and its configuration
app = Flask(__name__)
app.config['ASSETS_DIRECTORY'] = './assets'
app.config['FILES_DIRECTORY'] = '{0}/files'.format(app.config['ASSETS_DIRECTORY'])
# Define mapping of parent path to its default child
app.config['DEFAULT_CHILDREN'] = {
    '': 'velo_view',
    'velo_view': 'velo_view/overview',
    'velo_view/trends': 'velo_view/trends/nzs'
}

def add_file_extension(filename):
    """Add `.root` extension to `filename`, if it's not already present."""
    return (filename + '.root') if filename[-5:] != '.root' else filename

def tfile_path(filename):
    """Return the path to the TFile with `filename`."""
    return '{0}/{1}'.format(app.config['FILES_DIRECTORY'], filename)

def default_child_path(path):
    """Return the default child of the parent path, if it exists, else return path.

    For example, the path `parent` should show the page `parent/child` by default,
    unless another child is specified. This method will then return `parent/child`,
    given `parent`. If `parent/child` should show `parent/child/grandchild` by default,
    this method will return `parent/child/grandchild` given `parent`.
    If no default child path exists, then `path` is returned.
    Keyword arguments:
    path -- The parent path to resolve in to its deepest default child path.
    """
    try:
        # Recurse until we find a path with no default child
        child_path = default_child_path(app.config['DEFAULT_CHILDREN'][path])
    except KeyError:
        child_path = path
    return child_path

# Root URL shows VELO view
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_page(path):
    # Find the default child page
    child_path = default_child_path(path)
    # Expose the child path value
    g.active_page = child_path
    # Try find a template called path.html, else 404
    try:
        return render_template('{0}.html'.format(child_path))
    except TemplateNotFound:
        abort(404)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

# Assets API
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(app.config['ASSETS_DIRECTORY'], filename)

# Files API
# The Files API defines the endpoints for retrieving and querying TFiles and their contents.
@app.route('/files/<filename>')
def get_file(filename):
    filename = add_file_extension(filename)
    return send_file(
        tfile_path(filename),
        mimetype='application/octet-stream',
        as_attachment=True,
        attachment_filename=filename
    )

@app.route('/files/<filename>/list')
def list_file(filename):
    filename = add_file_extension(filename)
    return jsonify(tasks.list_file(tfile_path(filename)))

@app.route('/files/<filename>/<key_name>')
def get_key_from_file(filename, key_name):
    filename = add_file_extension(filename)
    return jsonify(tasks.get_key_from_file(tfile_path(filename), key_name))

if __name__ == '__main__':
    app.debug = True
    app.run()
