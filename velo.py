import ROOT
from flask import (
    Flask,
    render_template,
    send_from_directory,
    send_file,
    jsonify
)

# Define the app and its configuration
app = Flask(__name__)
app.config['ASSETS_DIRECTORY'] = './assets'
app.config['FILES_DIRECTORY'] = '{0}/files'.format(app.config['ASSETS_DIRECTORY'])

def add_file_extension(filename):
    """Add `.root` extension to `filename`, if it's not already present."""
    return (filename + '.root') if filename[-5:] != '.root' else filename

def tfile_path(filename):
    """Return the path to the TFile with `filename`."""
    return '{0}/{1}'.format(app.config['FILES_DIRECTORY'], filename)

def data_for_object(obj):
    """Return a dictionary representing the data inside the object."""
    obj_class = obj.ClassName()
    d = {
        'name': obj.GetName(),
        'title': obj.GetTitle()
    }
    if obj_class[0:3] == 'TH1':
        # For histograms, we provide
        #   binning: Array of 2-tuples defining the (low, high) binning edges,
        #   values: Array of bin contents, ith entry falling in the ith bin
        #   uncertainties: Array of 2-tuples of (low, high) errors on the contents
        #   axis_titles: 2-tuple of (x, y) axis titles
        x_axis = obj.GetXaxis()
        num_bins = x_axis.GetNbins()
        d['binning'] = [
            (x_axis.GetBinLowEdge(i), x_axis.GetBinUpEdge(i))
            for i in range(num_bins)
        ]
        d['values'] = [obj.GetBinContent(i) for i in range(num_bins)]
        d['uncertainties'] = [
            (obj.GetBinErrorLow(i), obj.GetBinErrorUp(i))
            for i in range(num_bins)
        ]
        d['axis_titles'] = (x_axis.GetTitle(), obj.GetYaxis().GetTitle())
    return d

# Root URL shows VELO view
@app.route('/')
@app.route('/velo_view', endpoint='velo_view')
@app.route('/velo_view/overview')
def velo_view_overview():
    return render_template('velo_view/overview.html')

@app.route('/velo_view/trends', endpoint='velo_view_trends')
@app.route('/velo_view/trends/nzs')
def velo_view_trends_nzs():
    return render_template('velo_view/trends/nzs.html')

@app.route('/velo_view/trends/clusters')
def velo_view_trends_clusters():
    return render_template('velo_view/trends/clusters.html')

@app.route('/velo_view/trends/tracks')
def velo_view_trends_tracks():
    return render_template('velo_view/trends/tracks.html')

@app.route('/velo_view/trends/vertices')
def velo_view_trends_vertices():
    return render_template('velo_view/trends/vertices.html')

@app.route('/velo_view/detailed_trends')
def velo_view_detailed_trends():
    return render_template('velo_view/detailed_trends.html')

@app.route('/sensor_view')
def sensor_view():
    return render_template('sensor_view.html')

@app.route('/run_view')
def run_view():
    return render_template('run_view.html')

@app.route('/tell1_view')
def tell1_view():
    return render_template('tell1_view.html')

@app.route('/special_analyses')
def special_analyses():
    return render_template('special_analyses.html')

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
    f = ROOT.TFile(tfile_path(filename))
    if f.IsZombie():
        d = {
            'success': False,
            'message': 'Could not open file `{0}`'.format(filename)
        }
    else:
        d = {
            'success': not f.IsZombie(),
            'data': {
                'filename': filename,
                'keys': [key.GetName() for key in f.GetListOfKeys()]
            }
        }
    f.Close()
    return jsonify(d)

@app.route('/files/<filename>/<key_name>')
def get_file_key(filename, key_name):
    filename = add_file_extension(filename)
    f = ROOT.TFile(tfile_path(filename))
    if f.IsZombie():
        return jsonify({
            'success': False,
            'message': 'Could not open file `{0}`'.format(filename)
        })
    obj = None
    # This method, opposed to TFile.Get, is more robust against odd key names
    for key in f.GetListOfKeys():
        if key.GetName() == key_name:
            obj = key.ReadObj()
    if not obj:
        d = {
            'success': False,
            'message': 'Could not find key `{0}` in file `{1}`'.format(filename, key_name)
        }
    else:
        d = {
            'success': True,
            'data': {
                'filename': filename,
                'key_name': obj.GetName(),
                'key_class': obj.ClassName(),
                'key_data': data_for_object(obj)
            }
        }
    f.Close()
    return jsonify(d)

if __name__ == '__main__':
    app.debug = True
    app.run()
