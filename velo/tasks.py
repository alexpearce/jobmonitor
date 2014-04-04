import ROOT

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

def list_file(filename):
    """Return a list of keys, as strings, in `filename`.

    Keyword arguments:
    filename -- Name of file with full path, e.g. `/a/b/my_file.root`
    """
    f = ROOT.TFile(filename)
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
    return d


def get_key_from_file(filename, key_name):
    """Return the object, stored under `key_name`, in `filename`.

    Keyword arguments:
    filename -- Name of file with full path, e.g. `/a/b/my_file.root`
    key_name -- Name of key object is stored as
    """
    f = ROOT.TFile(filename)
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
    return d
