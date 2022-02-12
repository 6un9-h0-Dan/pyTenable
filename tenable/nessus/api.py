'''
Nessus
======

This package covers the Nessus interface.

.. autoclass:: Nessus
    :members:


.. toctree::
    :hidden:
    :glob:

    agent_groups
    agents
    editor
    files
    folders
    groups
    mail
    migration
    permissions
    plugin_rules
    plugins
    policies
    proxy
    scanners
    scans
    server
    settings
    software_update
    tokens
    users
'''
from tenable.base.platform import APIPlatform
from .agent_groups import AgentGroupsAPI
from .agents import AgentsAPI
from .files import FilesAPI
from .folders import FoldersAPI
from .groups import GroupsAPI
from .mail import MailAPI
from .permissions import PermissionsAPI
from .plugins import PluginsAPI


class Nessus(APIPlatform):
    '''
    The Nessus object is the primary interaction point for users to
    interface with Nessus via the pyTenable library.  All of the API
    endpoint classes that have been written will be grafted onto this class.
    '''
    _env_base = 'NESSUS'
    _ssl_verify = False
    _conv_json = True

    def _session_auth(self, username, password):  # noqa: PLW0221,PLW0613
        token = self.post('session', json={
            'username': username,
            'password': password
        }).get('token')
        self._session.headers.update({
            'X-Cookie': f'token={token}'
        })
        self._auth_mech = 'user'

    @property
    def agent_groups(self):
        '''
        The interface object for the
        :doc:`Nessus Agent Groups APIs <agent_groups>`.
        '''
        return AgentGroupsAPI(self)

    @property
    def agents(self):
        '''
        The interface object for the :doc:`Nessus Agents APIs <agents>`.
        '''
        return AgentsAPI(self)
    
    @property
    def files(self):
        '''
        The interface object for the :doc:`Nessus File APIs <files>`.
        '''
        return FilesAPI(self)
    
    @property
    def folders(self):
        '''
        The interface object for the :doc:`Nessus Folders APIs <folders>`.
        '''
        return FoldersAPI(self)
    
    @property
    def groups(self):
        '''
        The interface object for the :doc:`Nessus Groups APIs <groups>`.
        '''
        return GroupsAPI(self)
    
    @property
    def mail(self):
        '''
        The interface object for the :doc:`Nessus Mail APIs <mail>`.
        '''
        return MailAPI(self)
    
    @property
    def permissions(self):
        '''
        The interface object for the 
        :doc:`Nessus Permissions APIs <permissions>`.
        '''
        return PermissionsAPI(self)

    @property
    def plugins(self):
        '''
        The interface object for the :doc:`Nessus Plugins APIs <plugins>`.
        '''
        return PluginsAPI(self)
