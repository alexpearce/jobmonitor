from flask import (
    # Blueprint creation
    Blueprint,
    # The request context
    request,
    # JSON encode Python dictionaries
    jsonify,
    # Generate URLs
    url_for,
    # Raise HTTP error code exceptions
    abort
)

# Job queues
from rq import Queue
from rq.exceptions import NoSuchJobError
from start_worker import conn
queue = Queue(connection=conn)

jobs = Blueprint('jobs', __name__)

# TODO finalise response format, i.e. what metadata we send with each response
def serialize_job(job):
    """Return a dictionary representing the job."""
    d = dict(
        id=job.get_id(),
        uri=url_for('jobs.get_job', job_id=job.get_id(), _external=True),
        status=job.get_status(),
        result=job.result
    )
    return d


@jobs.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = [serialize_job(j) for j in queue.get_jobs()]
    return jsonify({'jobs': jobs})


@jobs.route('/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
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
        # TODO we don't have introspection as we don't know what methods are
        # to the worker. are there any sanity check we can do?
        task = 'monitoring_app.tasks.{0}'.format(task_name)
    except AttributeError:
        return jsonify(dict(
            message='Invalid task name `{0}`'.format(task_name)
        )), 400
    # Enqueue the task, passing empty arguments if none were provided
    args = data.get('args', {})
    job = queue.enqueue(task, **args)
    return jsonify(dict(job=serialize_job(job))), 201


@jobs.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    # Try to fetch the job, 404'ing if it's not found
    try:
        job = queue.fetch_job(job_id)
    except NoSuchJobError:
        abort(404)
    return jsonify(dict(job=serialize_job(job)))
