"""Perform tests for the REST endpoint `/trials`"""
import copy
import datetime
import random

from orion.core.io import experiment_builder
from orion.core.worker.trial import Trial
from orion.storage.base import get_storage

base_experiment = dict(
    name='experiment-name',
    space={'x': 'uniform(0, 200)'},
    metadata={'user': 'test-user',
              'orion_version': 'x.y.z',
              'datetime': datetime.datetime(1, 1, 1),
              'VCS': {"type": "git",
                      "is_dirty": False,
                      "HEAD_sha": "test",
                      "active_branch": None,
                      "diff_sha": "diff"}},
    refers={},
    version=1,
    pool_size=1,
    max_trials=10,
    working_dir='',
    algorithms={'random': {'seed': 1}},
)

base_trial = {
    'experiment': None,
    'status': 'new',
    'worker': None,
    'submit_time': datetime.datetime(1, 1, 1),
    'start_time': datetime.datetime(1, 1, 1, second=10),
    'end_time': datetime.datetime(1, 1, 2),
    'heartbeat': None,
    'results': [
        {'name': 'loss', 'type': 'objective', 'value': 0.05},
        {'name': 'a', 'type': 'statistic', 'value': 10},
        {'name': 'b', 'type': 'statistic', 'value': 5},
    ],
    'params': [
        {'name': 'x',
         'type': 'real',
         'value': 10.0},
    ],
}


def add_experiment(**kwargs):
    """Adds experiment to the dummy orion instance"""
    base_experiment.update(copy.deepcopy(kwargs))
    experiment_builder.build(branching=dict(branch_from=base_experiment['name']), **base_experiment)


def add_trial(experiment: int, status: str = None, **kwargs):
    """
    Add trials to the dummy orion instance

    Parameters
    ----------
    experiment
        The ID of the experiment (stored in Experiment._id)
    status
        The status of the trial to add.
    **kwargs
        Any other attribute to modify from the base trial config.
    """
    if not status:
        status = random.choice(Trial.allowed_stati)

    kwargs['experiment'] = experiment
    kwargs['status'] = status

    base_trial.update(copy.deepcopy(kwargs))
    get_storage().register_trial(Trial(**base_trial))


def test_root_endpoint_not_supported(client):
    """Tests that the server return a 404 when accessing trials/ with no experiment"""
    response = client.simulate_get('/trials')

    assert response.status == "404 Not Found"
    assert not response.json


def test_trials_for_unknown_experiment(client):
    """Tests that an unknown experiment returns a bad request"""
    response = client.simulate_get('/trials/unknown-experiment')

    assert response.status == "404 Not Found"
    assert response.json['message'] == "Experiment 'unknown-experiment' does not exist"


def test_unknown_parameter(client):
    """
    Tests that if an unknown parameter is specified in
    the query string, an error is returned even if the experiment doesn't exist.
    """
    expected_body = "Parameter 'unknown' is not supported. " \
                    "Expected one of ['ancestors', 'status', 'version']."

    response = client.simulate_get('/trials/a?unknown=true')

    assert response.status == "400 Bad Request"
    assert response.json['message'] == expected_body

    add_experiment(name='a', version=1, _id=1)

    response = client.simulate_get('/trials/a?unknown=true')

    assert response.status == "400 Bad Request"
    assert response.json['message'] == expected_body


def test_trials_for_latest_version(client):
    """Tests that it returns the trials of the latest version of the experiment"""
    add_experiment(name='a', version=1, _id=1)
    add_experiment(name='a', version=2, _id=2)

    add_trial(experiment=1, id_override="00")
    add_trial(experiment=2, id_override="01")
    add_trial(experiment=1, id_override="02")
    add_trial(experiment=2, id_override="03")

    response = client.simulate_get('/trials/a')

    assert response.status == "200 OK"
    assert response.json == [{'id': '01'}, {'id': '03'}]


def test_trials_for_specific_version(client):
    """Tests specific version of experiment"""
    add_experiment(name='a', version=1, _id=1)
    add_experiment(name='a', version=2, _id=2)
    add_experiment(name='a', version=3, _id=3)

    add_trial(experiment=1, id_override="00")
    add_trial(experiment=2, id_override="01")
    add_trial(experiment=3, id_override="02")

    # Happy case
    response = client.simulate_get('/trials/a?version=2')

    assert response.status == "200 OK"
    assert response.json == [{'id': '01'}]

    # Version doesn't exist
    response = client.simulate_get('/trials/a?version=4')

    assert response.status == "404 Not Found"
    assert response.json['message'] == "Experiment 'a' has no version '4'"


def test_trials_for_all_versions(client):
    """Tests that trials from all ancestors are shown"""
    add_experiment(name='a', version=1, _id=1)
    add_experiment(name='a', version=2, _id=2)
    add_experiment(name='a', version=3, _id=3)

    add_trial(experiment=1, id_override="00")
    add_trial(experiment=2, id_override="01")
    add_trial(experiment=3, id_override="02")

    # Happy case default
    response = client.simulate_get('/trials/a?ancestors=true')

    assert response.status == "200 OK"
    assert response.json == [{'id': '00'}, {'id': '01'}, {'id': '02'}]

    # Happy case explicitly false (call latest version test)
    response = client.simulate_get('/trials/a?ancestors=false')

    assert response.status == "200 OK"
    assert response.json == [{'id': '02'}]

    # Not a boolean parameter
    response = client.simulate_get('/trials/a?ancestors=42')

    expected = "Incorrect type for parameter 'ancestors'. Expected type 'bool'."
    assert response.status == "400 Bad Request"
    assert response.json['message'] == expected


def test_trials_by_status(client):
    add_experiment(name='a', version=1, _id=1)

    # There exist no trial of the given status in an empty experiment
    response = client.simulate_get('/trials/a?status=completed')

    assert response.status == "200 OK"
    assert response.json == []

    # There exist no trial of the given status while other status are present
    add_trial(experiment=1, id_override="00", status="broken")

    response = client.simulate_get('/trials/a?status=completed')
    assert response.status == "200 OK"
    assert response.json == []

    # There exist at least one trial of the given status
    add_trial(experiment=1, id_override="01", status="completed")

    response = client.simulate_get('/trials/a?status=completed')

    assert response.status == "200 OK"
    assert response.json == [{'id': '01'}]

    # Status doesn't exist
    response = client.simulate_get('/trials/a?status=invalid')

    assert response.status == "400 Bad Request"
    error_message = "Invalid status value. " \
                    "Expected one of " \
                    "['new', 'reserved', 'suspended', 'completed', 'interrupted', 'broken']"
    assert response.json == {'message': error_message}


def test_trials_by_from_specific_version_by_status_with_ancestors(client):
    # Mixed parameters
    add_experiment(name='a', version=1, _id=1)
    add_experiment(name='b', version=1, _id=2)
    add_experiment(name='a', version=2, _id=3)
    add_experiment(name='a', version=3, _id=4)

    add_trial(experiment=1, id_override="00", status='completed')
    add_trial(experiment=3, id_override="01", status='broken')
    add_trial(experiment=3, id_override="02", status='completed')
    add_trial(experiment=2, id_override="03", status='completed')

    response = client.simulate_get('/trials/a?ancestors=true&version=2&status=completed')

    assert response.status == "200 OK"
    assert response.json == [{'id': '00'}, {'id': '02'}]