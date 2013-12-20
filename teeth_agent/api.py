"""
Copyright 2013 Rackspace, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import collections

from teeth_rest import component
from teeth_rest import encoding
from teeth_rest import errors
from teeth_rest import responses


class AgentCommand(encoding.Serializable):
    def __init__(self, name, params):
        self.name = name
        self.params = params

    @classmethod
    def deserialize(cls, obj):
        for field in ['name', 'params']:
            if field not in obj:
                msg = 'Missing command \'{}\' field.'.format(field)
                raise errors.InvalidContentError(msg)

        return cls(obj['name'], obj['params'])

    def serialize(self, view):
        """Turn a command into a dictionary."""
        return collections.OrderedDict([
            ('name', self.name),
            ('params', self.params),
        ])


class TeethAgentAPI(component.APIComponent):
    """The primary Teeth Agent API."""

    def __init__(self, agent):
        super(TeethAgentAPI, self).__init__()
        self.agent = agent

    def add_routes(self):
        """Called during initialization. Override to map relative routes to
        methods.
        """
        self.route('GET', '/status', self.get_agent_status)
        self.route('POST', '/command', self.execute_agent_command)

    def get_agent_status(self, request):
        """Get the status of the agent."""
        return responses.ItemResponse(self.agent.get_status())

    def execute_agent_command(self, request):
        """Execute a command on the agent."""
        command = AgentCommand.deserialize(self.parse_content(request))
        self.agent.execute_command(command)
        # TODO(russellhaering): implement actual responses
        return responses.ItemResponse({'result': 'success'})


class TeethAgentAPIServer(component.APIServer):
    """Server for the teeth agent API."""

    def __init__(self, agent):
        super(TeethAgentAPIServer, self).__init__()
        self.add_component('/v1.0', TeethAgentAPI(agent))