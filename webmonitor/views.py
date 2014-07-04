# Flask API: http://flask.pocoo.org/docs/api/
from flask import (
    # The request context
    request,
    # Rendering Jinja2 templates
    render_template,
    # Serving custom filetypes
    send_file,
    # JSON encode Python dictionaries
    jsonify,
    # Set and access variables global to the app instance and views
    g,
    # Generate URLs
    url_for,
    # Raise HTTP error code exceptions
    abort
)
# So we can catch Jinja2 exception
from jinja2.exceptions import TemplateNotFound

# Job queues
from rq import Queue
from start_worker import conn
queue = Queue(connection=conn)

# ROOT tasks
import tasks

# The application
from webmonitor import app

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


# TODO should respond with JSON when 404'ing from the jobs API
@app.errorhandler(404)
def page_not_found(e):
    g.active_page = '404'
    return render_template('errors/404.html'), 404


# Jobs API
# TODO finalise response format, i.e. what metadata we send with each response
##########

def serialize_job(job):
    """Return a dictionary representing the job."""
    d = dict(
        id=job.get_id(),
        uri=url_for('get_job', job_id=job.get_id(), _external=True),
        status=job.status,
        result=job.result
    )
    return d


@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = [serialize_job(j) for j in queue.get_jobs()]
    return jsonify({'jobs': jobs})


@app.route('/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    # Only handle JSON requests
    # TODO when Flask 0.11 is released, use request.is_json instead
    if not data:
        abort(400)
    # Try read the task name and load the task, returning a 400 error on fail
    try:
        task_name = data['task_name']
    except KeyError:
        return jsonify(dict(
            message='No task name provided'
        )), 400
    try:
        # TODO how can this be made extensible by derivative apps?
        # Maybe webmonitor.add_tasks(...), then we look in a list/dict here?
        task = getattr(tasks, task_name)
    except AttributeError:
        return jsonify(dict(
            message='Invalid task name `{0}`'.format(task_name)
        )), 400
    # Enqueue the task, passing empty arguments if none were provided
    args = data.get('args', {})
    job = queue.enqueue(task, **args)
    return jsonify(dict(job=serialize_job(job))), 201


@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    # Try to fetch the job, 404'ing if it's not found
    job = queue.safe_fetch_job(job_id)
    if job is None:
        abort(404)
    return jsonify(dict(job=serialize_job(job)))


if __name__ == '__main__':
    app.debug = True
    app.run()
