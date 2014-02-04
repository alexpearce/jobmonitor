// For more information on the 'revealing module' pattern, see
//   http://addyosmani.com/resources/essentialjsdesignpatterns/book/#modulepatternjavascript
var VELO = (function($, undefined) {
  'use strict';

  var settings = {
    // Show `console.log` messages?
    debug: false,
    // Defaults for histogram drawing
    highchartsDefaults: {
      chart: {
        zoomType: 'x'
      },
      legend: {
        enabled: false
      },
      xAxis: {
        gridLineWidth: 1,
        minorTickInterval: 'auto'
      },
      yAxis: {
        gridLineWidth: 1,
        minorTickInterval: 'auto'
      },
      plotOptions: {
        series: {
          // Disable initialisation animation
          animation: false
        },
        column: {
          groupPadding: 0,
          pointPadding: 0,
          borderWidth: 0
        },
        errorbar: {}
      },
      credits: {
        enabled: false
      }
    },
    // See http://fgnass.github.io/spin.js/ for options and customisation
    spinnerDefaults: {
      lines: 12,
      length: 5,
      width: 2,
      radius: 5,
      trail: 50,
      shadow: false
    }
  };

  // Cross-browser compatible `console.log`. Only fires if settings.debug === true.
  // http://paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
  // Accepts:
  //   Any number of arguments of any type.
  // Returns:
  //   undefined
  var log = function() {
    log.history = log.history || [];
    log.history.push(arguments);
    if (window.console && settings.debug) {
      console.log(Array.prototype.slice.call(arguments));
    }
  };

  // Draw a histogram in the `container` using `options`.
  // Accepts:
  //   container: A jQuery object in which to draw the histogram
  //   options: Object of options passed to the plotting library
  // Returns:
  //   undefined
  var drawHistogram = function(container, options) {
    // Create a new object as the merge of the default options and those in the argument.
    // Properties in options will overrides the defaults.
    container.highcharts($.extend(true, {}, VELO.settings.highchartsDefaults, options));
  };

  // Display a histogram, described by `data`, in `container`.
  // Accepts:
  //   data: An object describing the histogram
  //   container: A jQuery object in which to draw the histogram
  // Returns:
  //   undefined
  var displayHistogram = function(data, container) {
    var name = data['name'],
        title = data['title'],
        binning = data['binning'],
        values = data['values'],
        uncertainties = data['uncertainties'],
        axisTitles = data['axis_titles'],
        points = [],
        errors = [];
    var v, binCenter, uLow, uHigh;
    // We need to manipulate the values slightly for Highcharts
    // 'Histogram' columns are defined by their x-axis bin centers
    // and their y-axis columns heights
    // We define the bin center as the average of the bin boundaries,
    // and the column height as the bin contents
    // Uncertainties need an x-value, the bin center, and (low, high) y-values
    for (var i = 0; i < values.length; i++) {
      v = values[i];
      uLow = v - uncertainties[i][0];
      uHigh = v + uncertainties[i][1];
      binCenter = (binning[i][0] + binning[i][1])/2.0;
      points.push([binCenter, v]);
      errors.push([binCenter, uLow, uHigh]);
    }
    // Draw the histogram in the container
    drawHistogram(container, {
      title: {
          text: title
      },
      series: [
        {
          name: 'Data',
          type: 'column',
          data: points,
          color: '#ccc'
        },
        {
          name: 'Data error',
          type: 'errorbar',
          data: errors
        }
      ],
      xAxis: {
        title: {
          text: axisTitles[0]
        }
      },
      yAxis: {
        title: {
          text: axisTitles[1]
        }
      }
    });
  };

  // Fetches and draws the named `histogram`, residing in `file`, in to the `container`.
  // Accepts:
  //   histogram: String of the histogram's full path key name with in the file
  //   file: String of the file name
  //   container: jQuery element the histogram should be drawn in to. Any existing content will be replaced.
  var loadHistogramFromFileIntoContainer = function(histogram, file, container) {
    var url = '/files/' + file + '/' + histogram;
    $.getJSON(url, function(data, status, jqXHR) {
      if (status === 'success' && data['success'] === true) {
        // We can only handle TH1F objects at the moment
        var payload = data['data'];
        if (payload['key_class'] !== 'TH1F') return;
        displayHistogram(payload['key_data'], container);
      }
    });
  };

  // Add a `Spinner` object to the `element`, using `settings.spinnerDefaults` as options.
  // Accepts:
  //   element: DOM element
  // Returns:
  //   Spinner object
  var appendSpinner = function(element) {
    return new Spinner(settings.spinnerDefaults).spin(element);
  }

  // Page-specific modules
  var pages = {
    veloView: {
      init: function() {
        log('veloView.init');
      },
      overview: {
        init: function() {
          log('veloView.overview.init');
        }
      },
      trends: {
        init: function () {
          log('veloView.trends.init');
        }
      },
      detailedTrends: {
        init: function () {
          log('veloView.detailedTrends.init');
        }
      }
    }
  };

  // Initialise globally required features, and call the chain of inits required for pageModule.
  // Accepts:
  //   pageModule: String of the form `x.y.z`. Starting from the top (`x`), the `init` function on each module is called, if it exists.
  // Returns:
  //   undefined
  var init = function(pageModule) {
    var components = pageModule.split('.'),
        parentModule = pages,
        modules = [];
    // Work our way down the chain, top to bottom, calling `init` on each successive child, if it exists.
    $.each(components, function(index, component) {
      var current = parentModule[component];
      modules.push(current);
      parentModule = current;
      if (current !== undefined && current.init !== undefined) {
        current.init();
      }
    });

    // Find any elements requiring histograms from files and load them
    $('.main').find('.histogram').each(function(index, el) {
      var $el = $(el),
          file = $el.data('file'),
          histogram = $el.data('histogram');
      if (file && histogram) {
        appendSpinner(el);
        loadHistogramFromFileIntoContainer(histogram, file, $el);
      }
    });
  };

  return {
    init: init,
    settings: settings
  };
})(jQuery);

$(function() {
  VELO.settings.debug = true;
  // Away we go!
  VELO.init(veloPageModule);
  return;
  var $main = $('#main'),
      $header = $main.find('h2'),
      $list = $main.find('ul'),
      $histogram = $('#histogram');

  // Attach the event handler for all current and future list item anchors
  $list.on('click', 'li a', function(e) {
    var $target = $(e.target),
        filename = $target.data('filename'),
        keyname = $target.data('keyname'),
        url = '/files/' + filename + '/' + keyname;
    $.getJSON(url, function(data, status, jqXHR) {
      // We can only handle TH1F objects at the moment
      var payload = data['data'];
      if (payload['key_class'] !== 'TH1F') return;
      VELO.displayHistogram(payload['key_data'], $histogram);
    });
    e.preventDefault();
  });
  listURL = '/files/histograms/list';
  $.getJSON(listURL, function(data, status, jqXHR) {
    if (data['success'] === true) {
      var payload = data['data'],
          filename = payload['filename'];
      $header.html('Listing <code>' + payload['filename'] + '</code>');
      // Clear the list and then populate it with one list item per key
      $list.html('');
      if (payload['keys'].length === 0) {
        $list.append('<li>File is empty</li>');
      }
      $.map(payload['keys'], function(key) {
        $list.append('<li><a data-filename="' + filename + '" data-keyname="' + key + '" href="#">' + key + '</a></li>');
      });
    } else {
      console.error('JSON request failed with message', data['message']);
    }
  });
});
