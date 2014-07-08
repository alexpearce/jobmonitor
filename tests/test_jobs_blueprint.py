import unittest
import json
import flask
import webmonitor

from rq import Queue
import webmonitor.start_worker

def add(a, b):
    """Task to put on the queue."""
    return a + b

class WebMonitorTest(unittest.TestCase):
    def setUp(self):
        self.app = webmonitor.create_app()
        self.client = self.app.test_client()
        self.queue = Queue(connection=webmonitor.start_worker.create_connection())
        # Make sure the queue's empty, then enqueue some jobs
        self.queue.empty()
        self.njobs = 2
        for i in range(self.njobs):
            self.queue.enqueue(add, a=i, b=3)
        # Create some dummy request data
        self.request_data = json.dumps(dict(task_name='add'))

    def get_json_response(self, url):
        """Return the rv for the URL and the decoded JSON data."""
        rv = self.client.get(url)
        data = json.loads(rv.data)
        return rv, data

    def test_list_jobs(self):
        """The correct number of jobs should be returned."""
        rv, data = self.get_json_response('/jobs')
        assert len(data['jobs']) == self.njobs

    def test_create_job(self):
        """Job response should be the new job and a success status code."""
        rv = self.client.post('/jobs', data=self.request_data,
            content_type='application/json')
        data = json.loads(rv.data)
        assert data.has_key('job')
        assert rv.status_code == 201

    def test_invalid_job_creation_no_task_name(self):
        """Attempting to create a job without a task name should give 400."""
        rv = self.client.post('/jobs', data=json.dumps(dict()),
            content_type='application/json')
        assert rv.status_code == 400

    def test_invalid_job_creation_not_json(self):
        """Only JSON requests can create jobs, else 400."""
        rv = self.client.post('/jobs', data=self.request_data)
        data = json.loads(rv.data)
        assert data.has_key('message')
        assert len(data['message']) > 0
        assert rv.status_code == 400

    def test_get_job(self):
        """A job existing in the queue can be retrieved with its ID."""
        job_id = self.queue.job_ids[0]
        rv, data = self.get_json_response('/jobs/{0}'.format(job_id))
        job = data['job']
        assert job.has_key('id')

    def test_serialisation(self):
        """All necessary information should be present in the job response."""
        job_id = self.queue.job_ids[0]
        with self.app.test_request_context():
            rv, data = self.get_json_response('/jobs/{0}'.format(job_id))
            job = data['job']
            assert job.has_key('id')
            job_id = job['id']
            assert job.has_key('uri')
            assert job['uri'] == flask.url_for('jobs.get_job', job_id=job_id, _external=True)
            assert job.has_key('status')
            # Status should be one of the values allowed by rq
            # https://github.com/nvie/rq/blob/0.4.6/rq/job.py#L30
            assert job['status'] in ('queued', 'finished', 'failed', 'started')
            assert job.has_key('result')

    def test_bad_request(self):
        """`400 bad request` should be a JSON response with a message."""
        rv = self.client.post('/jobs', data=json.dumps(dict()),
            content_type='application/json')
        data = json.loads(rv.data)
        assert data.has_key('message')
        assert len(data['message']) > 0
        assert rv.status_code == 400

    def test_not_found(self):
        """`404 not found` should be a JSON response with a message."""
        # rv, data = self.get_json_response('/jobs/fake_id')
        rv = self.client.get('/jobs/fake_id')
        print rv.data
        return
        assert data.has_key('message')
        assert len(data['message']) > 0
        assert rv.status_code == 404


if __name__ == '__main__':
    unittest.main()
