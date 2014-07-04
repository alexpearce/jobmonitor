// For more information on the 'revealing module' pattern, see
//   http://addyosmani.com/resources/essentialjsdesignpatterns/book/#modulepatternjavascript
var WebMonitor = (function($, undefined) {
  'use strict';

  var settings = {
    // Show `console.log` messages?
    debug: false,
    // Default job status polling timeout in milliseconds
    pollRate: 300,
    // Defaults for histogram drawing
    histogramDefaults: {
    },
    // See http://fgnass.github.io/spin.js/ for options and customisation
    spinnerDefaults: {
      lines: 12,
      length: 5,
      width: 2,
      radius: 5,
      trail: 50,
      shadow: false
    },
    // See http://eternicode.github.io/bootstrap-datepicker/
    datepickerDefaults: {
      format: 'dd/mm/yyyy',
      // This app doesn't now about the future
      endDate: '+0d',
      todayBtn: 'linked',
      // Always pop under the field
      orientation: 'top auto',
      autoclose: true,
      todayHighlight: true
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
  //     If the jQuery object references multiple DOM nodes, the first is used
  //   data: An array of data points formatted for d3.chart.histogram
  //   options: Object of options passed to the plotting library
  //     Any present options override those in WebMonitor.settings.histogramDefaults
  // Returns:
  //   undefined
  var drawHistogram = function(container, data, options) {
    var opt = $.extend(true, {}, WebMonitor.settings.histogramDefaults, options);
    d3.select(container.get()[0]).append('svg')
      .attr('width', container.width())
      .attr('height', container.height())
      .chart('HistogramZoom')
      .xAxisLabel(opt.xAxis.title.text)
      .yAxisLabel(opt.yAxis.title.text)
      .draw(data);
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
        axisTitles = data['axis_titles'];
    var v, binCenter, uLow, uHigh;
    // We need to manipulate the values slightly for d3.chart.histogram
    // See the d3.chart.histogram documentation for the specifics
    var formattedData = [];
    for (var i = 0; i < values.length; i++) {
      var bins = binning[i];
      formattedData.push({
        x: bins[0],
        dx: bins[1],
        y: data['values'][i],
        xErr: uncertainties[i]
      });
    }
    var options = {
      title: {
        text: title
      },
      xAxis: {
        title: {
          text: axisTitles[0]
        }
      },
      yAxis: {
        title: {
          text: axisTitles[1]
        }
      },
    };
    // Remove the spinner
    container.find('.spinner').remove();
    // Draw the histogram in the container
    drawHistogram(container, formattedData, options);
  };

  // Fetches and draws the named `histogram`, residing in `file`, in to the `container`.
  // Accepts:
  //   histogram: String of the histogram's full path key name with in the file
  //   file: String of the file name
  //   container: jQuery element the histogram should be drawn in to. Any existing content will be replaced.
  var loadHistogramFromFileIntoContainer = function(histogram, file, container) {
      var task = createTask('get_key_from_file', {filename: file, key_name: histogram});
      task.done(function(job) {
          displayHistogram(job['result']['data']['key_data'], container);
      });
      task.fail(function(message) {
        var failMsg = '<p>There was a problem retrieving histogram '
          + '<code>' + histogram + '</code>'
          + ' from file '
          + '<code>' + file + '</code>'
          + '. Please contact the administrator.</p>'
          + message;
        displayFailure(container, failMsg);
      });
  };

  // Submit a job to the server
  // Accepts:
  //   taskName: Name of the task the job will run
  //   args: Object of arguments passed to the task as named arguments
  //   poll: Whether to poll the job until completion (default: true)
  //     The job is polled in intervals of WebMonitor.settings.pollRate until
  //     the job status is not `queued` or `started`.
  // Returns:
  //   jQuery.Deferred object which fires `resolve` on job completion and fires
  //     `reject` on either submission failure or job polling failure
  var submitJob = function(taskName, args, doPoll) {
    if (doPoll === undefined) {
      doPoll = true;
    }
    var jobRequest =  $.ajax('/jobs', {
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      dataType: 'json',
      data: JSON.stringify({task_name: taskName, args: args})
    });
    var jobPromise = $.Deferred();
    var poll = function(job) {
      var jobID = job['id'],
          jobStatus = job['status'];
      // Poll the job if it hasn't not completed, else fire `resolve`
      if (jobStatus === 'queued' || jobStatus === 'started') {
        setTimeout(function() {
          log('Polling job ID ' + jobID + ': ' + jobStatus);
          $.getJSON(job['uri'])
            .done(function(data, status) { poll(data['job']); })
            .fail(function(data, status) { jobPromise.reject(data, status); });
        }, settings.pollRate);
      } else {
        log('Job ' + jobID + ' completed: ' + jobStatus);
        jobPromise.resolve(job);
      }
    };
    jobRequest.done(function(data, status) {
      var job = data['job'];
      if (doPoll === true) {
        poll(job);
      }
    });
    // Fire `reject` if the submission fails
    jobRequest.fail(function(data, status) { jobPromise.reject(data, status); });
    return jobPromise;
  };

  // Create a task and submit a job for it to the queue
  //
  // Unlike submitJob, this method handles job failures by creating descriptive
  // HTML error messages.
  // This relies on the JSON response containing a `result` key which is the
  // task's return value, which itself contains a `success` key determining
  // whether the task completed successfully.
  // If `success` if false, the task's `message` key is retrieved.
  // Accepts:
  //   taskName: Name of the task the job will run
  //   args: Object of arguments passed to the task as named arguments
  // Returns:
  //   jQuery.Deferred object which fires `resolve` on job completion and fires
  //     `reject` on either submission failure, job polling failure, or task
  //     failure. On resolution, the JSON response object is passed, whereas
  //     on rejection a descriptive HTML error message is passed.
  var createTask = function(taskName, args) {
    // Create a polling job
    var jobPromise = submitJob(taskName, args, true);
    var taskPromise = $.Deferred();
    jobPromise.done(function(job) {
      // Did the job complete successfully or not?
      if (job['status'] === 'failed') {
        var message = '<p>The job completed unsuccessfully.</p>';
        taskPromise.reject(message);
      } else {
        // Did the task the job was running finish successfully or not?
        var result = job['result'];
        if (result['success'] === false) {
          var message = '<p>The task could not complete successfully. It returned the error message '
            + '<code>' + result['message'] + '</code>.'
            + '</p>';
          taskPromise.reject(message);
        } else {
          taskPromise.resolve(job);
        }
      }
    });
    jobPromise.fail(function(data, status) {
      var message;
      try {
        message = JSON.parse(data.responseText)['message'];
      } catch(e) {
        message = data.statusText;
      }
      message = '<p>The server responded with the error code '
        + '<code>' + data.status + '</code>'
        + ' and the message '
        + '<code>' + message + '</code>.'
        + '</p>';
      taskPromise.reject(message);
    });
    return taskPromise;
  };

  // Display msg inside container, styled as a red error box
  // Accepts:
  //   container: jQuery element to insert msg into
  //   msg: HTML message to display inside container
  var displayFailure = function(container, msg) {
    container.html('<div class="alert alert-danger">' + msg + '</div>');
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
    examples: {
      init: function() {
        log('examples.init');
      },
      table: {
        init: function() {
          log('examples.table.init');
        }
      },
      singeLayout: {
        init: function() {
          log('examples.singleLayout.init');
        }
      },
      gridLayout: {
        init: function() {
          log('examples.gridLayout.init');
        }
      },
      tabs: {
        init: function() {
          log('examples.tabs.init');
        }
      },
    }
  };

  // Initialise globally required features, and call the chain of inits required for pageModule.
  // Accepts:
  //   pageModule: String of the form `x.y.z`. Starting from the top (`x`), the `init` function on each module is called, if it exists.
  // Returns:
  //   undefined
  var init = function(pageModule) {
    var components = pageModule.split('/'),
        parentModule = pages,
        modules = [],
        $main = $('.main');

    // Work our way down the module chain, top to bottom, calling `init` on each successive child, if it exists.
    $.each(components, function(index, component) {
      var current = parentModule[component];
      modules.push(current);
      parentModule = current;
      if (current !== undefined && current.init !== undefined) {
        current.init();
      }
    });

    // Find any elements requiring histograms from files and load them
    $main.find('.histogram').each(function(index, el) {
      var $el = $(el),
          file = $el.data('file'),
          histogram = $el.data('histogram');
      if (file && histogram) {
        appendSpinner(el);
        loadHistogramFromFileIntoContainer(histogram, file, $el);
      }
    });

    // Add datepicker to appropriate fields
    $main.find('.input-daterange').datepicker(settings.datepickerDefaults);
  };

  return {
    init: init,
    submitJob: submitJob,
    createTask: createTask,
    settings: settings
  };
})(jQuery);

$(function() {
  WebMonitor.settings.debug = true;
  // Away we go!
  WebMonitor.init(activePage);
});
