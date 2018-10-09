#!/usr/bin/env python3

"""
CLI tool for mass update of env variables in CircleCI.
Will update all projects that user with provided token follows

Use case - rotate AWS keys

Usage:
  circleci-manage-env-vars.py [--debug] --token TOKEN --action ACTION --name NAME [--value VALUE]

Options:
  --debug           Print debug info
  --help            Print this message
  --action          Should be one of create/update/delete
  --name            Environment variable name to create/update/delete
  --value           New value for environemnt variable, ignored for delete
  --token           CircleCI token
"""

import json
import logging
import sys

import requests
from docopt import docopt


def get_arg(args, key, default=None):
    if key in args:
        return args[key]
    else:
        return default


def send_request(url, params, request_type='get', data={}):
    headers = {'Accept': 'application/json'}
    logging.debug('Sending {} request to URL: {}, headers: {}'.format(
        request_type, url, headers))
    request_method = getattr(requests, request_type)
    result = request_method(url, params=params, headers=headers, data=data)
    if result.status_code == 200 or result.status_code == 201:
        return json.loads(result.text)
    else:
        raise IOError('Received code {}: {}'.format(
            result.status_code, result.text))


def get_all_projects(token):
    logging.info('Getting all projects known to the user')

    params = {'circle-token': token, 'limit': 1000}
    url = 'https://circleci.com/api/v1.1/projects'
    response = send_request(url, params)
    logging.debug(json.dumps(response, sort_keys=True, indent=4))

    projects = list()
    for project in response:
        projects.append((project['reponame'], project['username'], project['vcs_type']))
    logging.info('Found {} projects'.format(len(projects)))
    logging.debug(projects)

    return projects


def is_env_var_set(token, vcs, username, project, name):
    logging.debug(f'Check if environment variable {name} is set for project {project}')
    params = {'circle-token': token}
    url = f'https://circleci.com/api/v1.1/project/{vcs}/{username}/{project}/envvar'
    response = send_request(url, params)
    logging.debug(json.dumps(response, sort_keys=True, indent=4))
    env_vars = [env_var['name'] for env_var in response]
    logging.debug(env_vars)

    if name in env_vars:
        logging.debug(f'Env variable f{name} is set for project {project}')
        return True
    else:
        logging.debug(f'Environment variable {name} is not set for {project}')
        return False


def update(token, vcs, username, project, name, value):
    if is_env_var_set(token, vcs, username, project, name):
        create(token, vcs, username, project, name, value)
    else:
        logging.info(f'Environment variable {name} is not set for {project}. Skip it')


def create(token, vcs, username, project, name, value):
    logging.info(f'Set environment variable {name} for project {project}')
    params = {'circle-token': token}
    data = {"name": name, "value": value}
    url = f'https://circleci.com/api/v1.1/project/{vcs}/{username}/{project}/envvar'
    response = send_request(url, params, 'post', data)
    logging.info(response)


def delete(token, vcs, username, project, name, value=None):
    if is_env_var_set(token, vcs, username, project, name):
        logging.info(f'Delete environment variable {name} for project {project}')
        params = {'circle-token': token}
        url = f'https://circleci.com/api/v1.1/project/{vcs}/{username}/{project}/envvar/{name}'
        response = send_request(url, params, 'delete')
        logging.info(response)
    else:
        logging.info(f'Environment variable {name} is not set for {project}. Skip it')


def main():
    arguments = docopt(__doc__)

    token = get_arg(arguments, 'TOKEN')
    name = get_arg(arguments, 'NAME')
    value = get_arg(arguments, 'VALUE')
    action = get_arg(arguments, 'ACTION')

    if action not in ['create', 'update', 'delete']:
        raise ValueError(f'--action should be one of the create/update/delete, not {action}')

    if arguments['--debug'] is True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.basicConfig(format='%(message)s', level=logging.INFO)

    projects = get_all_projects(token)
    for project, username, vcs in projects:
        this_module = sys.modules[__name__]
        function_to_call = getattr(this_module, action)
        function_to_call(token, vcs, username, project, name, value)

    logging.info('Done')


if __name__ == "__main__":
    main()
