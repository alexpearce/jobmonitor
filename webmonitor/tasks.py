import ROOT

from webmonitor import app

def add_file_extension(filename):
    """Add `.root` extension to `filename`, if it's not already present."""
    return (filename + '.root') if filename[-5:] != '.root' else filename


def tfile_path(filename):
    """Return the path to the TFile with `filename`."""
    return '{0}/{1}'.format(app.config['FILES_DIRECTORY'], filename)


def data_for_object(obj):
    """Return a dictionary representing the data inside the object."""
    obj_class = obj.ClassName()
    d = {}
    if obj_class[0:3] == 'TH1':
        # For histograms, we provide
        #   binning: Array of 2-tuples defining the (low, high) binning edges,
        #   values: Array of bin contents, ith entry falling in the ith bin
        #   uncertainties: Array of 2-tuples of (low, high) errors on the contents
        #   axis_titles: 2-tuple of (x, y) axis titles
        xaxis = obj.GetXaxis()
        yaxis = obj.GetYaxis()
        nbins = xaxis.GetNbins()
        d['binning'] = [
            (xaxis.GetBinLowEdge(i), xaxis.GetBinUpEdge(i))
            for i in range(nbins)
        ]
        d['values'] = [obj.GetBinContent(i) for i in range(nbins)]
        d['uncertainties'] = [
            (obj.GetBinErrorLow(i), obj.GetBinErrorUp(i))
            for i in range(nbins)
        ]
        d['axis_titles'] = (xaxis.GetTitle(), yaxis.GetTitle())
    return d

def list_file(filename):
    """Return a list of keys, as strings, in `filename`.

    Keyword arguments:
    filename -- Name of file with full path, e.g. `/a/b/my_file.root`
    """
    f = ROOT.TFile(filename)
    if f.IsZombie():
        d = dict(
            success=False,
            message='Could not open file `{0}`'.format(filename)
        )
    else:
        d = dict(
            success=not f.IsZombie(),
            data=dict(
                filename=filename,
                keys=[key.GetName() for key in f.GetListOfKeys()]
            )
        )
    f.Close()
    return d


def get_key_from_file(filename, key_name):
    """Return the object, stored under `key_name`, in `filename`.

    Keyword arguments:
    filename -- Name of file with full path, e.g. `/a/b/my_file.root`
    key_name -- Name of key object is stored as
    """
    filename = tfile_path(add_file_extension(filename))
    f = ROOT.TFile(filename)
    if f.IsZombie():
        return dict(
            success=False,
            message='Could not open file `{0}`'.format(filename)
        )
    obj = None
    # This method, opposed to TFile.Get, is more robust against odd key names
    for key in f.GetListOfKeys():
        if key.GetName() == key_name:
            obj = key.ReadObj()
    if not obj:
        d = dict(
            success=False,
            message='Could not find key `{0}` in file `{1}`'.format(
                filename, key_name
            )
        )
    else:
        d = dict(
            success=True,
            data=dict(
                filename=filename,
                key_name=obj.GetName(),
                key_title=obj.GetTitle(),
                key_class=obj.ClassName(),
                key_data=data_for_object(obj)
            )
        )
    f.Close()
    return d
