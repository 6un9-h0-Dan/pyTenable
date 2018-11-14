'''
alerts
======

The following methods allow for interaction into the SecurityCenter 
`Alert <https://docs.tenable.com/sccv/api/Alert.html>`_ API.

Methods available on ``sc.alerts``:

.. rst-class:: hide-signature
.. autoclass:: AlertAPI

    .. automethod:: create
    .. automethod:: delete
    .. automethod:: details
    .. automethod:: execute
    .. automethod:: list
    .. automethod:: update

.. _iCal Date-Time:
    https://tools.ietf.org/html/rfc5545#section-3.3.5
.. _iCal Recurrance Rule:
    https://tools.ietf.org/html/rfc5545#section-3.3.10
'''
from .base import SCEndpoint
from tenable.utils import dict_merge

class AlertAPI(SCEndpoint):
    def _alert_creator(self, *filters, **kw):
        '''
        Handles building an alert document.
        '''

        # call the analysis query constructor to assemble a query.
        if len(filters) > 0:
            # checking to see if data_type was passed.  If it wasn't then we
            # will set the value to the default of 'vuln'.
            if 'data_type' not in kw:
                kw['data_type'] = 'vuln'
            kw['analysis_type'] = kw['data_type']
            kw['query'] = self._api.analysis._query_constructor(*filters, **kw)
            del(kw['analysis_type'])
            del(kw['data_type'])

        if 'name' in kw:
            kw['name'] = self._check('name', kw['name'], str)

        if 'description' in kw:
            kw['description'] = self._check(
                'description', kw['description'], str)

        if 'query' in kw:
            doc['query'] = self._check('query', kw['query'], dict)

        if 'always_exec_on_trigger' in kw:
            # executeOnEveryTrigger expected a boolean response as a lower-case
            # string.  We will accept a boolean and then transform it into a
            # string value.
            kw['executeOnEveryTrigger'] = str(self._check(
                'always_exec_on_trigger', kw['always_exec_on_trigger'], bool)).lower()
            del(kw['always_exec_on_trigger'])

        if 'trigger' in kw:
            # here we will be expanding the trigger from the common format of 
            # tuples that we are using within pytenable into the native 
            # supported format that SecurityCenter expects.
            self._check('trigger', kw['trigger'], tuple)
            kw['triggerName'] = self._check(
                'triggerName', kw['trigger'][0], str)
            kw['triggerOperator'] = self._check(
                'triggerOperator', kw['trigger'][1], str, 
                choices=['>=', '<=', '=', '!='])
            kw['triggerValue'] = self._check(
                'triggerValue', kw['trigger'][2], str)
            del(kw['trigger'])

        if ('schedule_type' in kw and kw['schedule_type'] == 'ical'
            and 'schedule_start' in kw 
            and 'schedule_repeat' in kw):
            # effectively here we are flattening the schedule subdocument on the
            # developer end and reconstructing it for the SecurityCenter end.
            #
            # FR: eventually we should start checking the repeating rule and the
            #     datetime against the ical format.
            kw['schedule'] = {
                'type': 'ical',
                'start': self._check(
                    'schedule_start', kw['schedule_start'], str),
                'repeatRule': self._check(
                    'schedule_repeat', kw['schedule_repeat'], str),
            }
            del(kw['schedule_type'])
            del(kw['schedule_start'])
            del(kw['schedule_repeat'])

        elif 'schedule_type' in kw:
            # if the schedule type is not an ical repeating rule, then we will
            # populate a schedule document with just the type.
            kw['schedule'] = {'type': self._check('schedule_type', 
                kw['schedule_type'], str, choices=[
                    'dependent', 'never', 'rollover', 'template'])}
            del(kw['schedule_type'])

        # FR: at some point we should start looking into checking and 
        #     normalizing the action document.
        return kw



    def list(self, fields=None):
        '''
        Retreives the list of alerts.

        + `SC Alert List <https://docs.tenable.com/sccv/api/Alert.html#AlertRESTReference-/alert>`_

        Args:
            fields (list, optional): 
                A list of attributed to return for each alert.

        Returns:
            list: A list of alert resources.

        Examples:
            >>> for alert in sc.alerts.list():
            ...     pprint(alert)
        '''
        params = dict()
        if fields:
            params['fields'] = ','.join([self._check('field', f, str) for f in fields])

        return self._api.get('alert', params=params).json()['response']

    def details(self, id, fields=None):
        '''
        Returns the details for a specific alert.

        + `SC Alert Details <https://docs.tenable.com/sccv/api/Alert.html#AlertRESTReference-/alert/{id}>`_

        Args:
            id (int): The identifier for the alert.
            fields (list, optional): A list of attributes to return.

        Returns:
            dict: The alert resource record.

        Examples:
            >>> alert = sc.alerts.detail(1)
            >>> pprint(alert)
        '''
        params = dict()
        if fields:
            params['fields'] = ','.join([self._check('field', f, str) for f in fields])

        return self._api.get('alert/{}'.format(self._check('id', id, int)),
            params=params).json()['response']

    def create(self, *filters, **kw):
        '''
        Creates a new alert.  The fields below are explicitly checked, however
        any attitional parameters mentioned in the API docs can be passed to the
        document constructer.

        + `SC Alert Create <https://docs.tenable.com/sccv/api/Alert.html#alert_POST>`_

        Args:
            *filters (tuple): 
                A filter expression.  Refer to the detailed description within
                the analysis endpoint documentation for more details on how to
                formulate filter expressions.
            data_type (str):
                The type of filters being used.  Must be of type ``lce``, 
                ``ticket``, ``user``, or ``vuln``.  If no data-type is
                specified, then the default of ``vuln`` will be set.
            name (str): The name of the alert.
            description (str, optional): A description for the alert.
            trigger (tuple): 
                A tuple in the filter-tuple format detailing what would
                constitute a trigger.  For example: ``('sumip', '=', '1000')``.
            always_exec_on_trigger (bool, optional):
                Should the trigger always execute when the trigger fires, or
                only execute when the returned data changes?  
                Default is ``False``.
            schedule_type (str, optional):
                What type of alert schedule shall this be?  Available supported
                values are ``dependent``, ``ical``, ``never``, ``rollover``, and
                ``template``.  The default value if unspecified is ``never``.
            schedule_start (str, optional):
                The time in which the trigger should start firing.  This value
                must conform to the `iCal Date-Time`_ standard.  Further this
                parameter is only required when specifying the schedule_type as
                ``ical``.
            schedule_repeat (str, optional):
                The rule that dictates the frequency and timing that the alert
                will run.  This value must conform to the `iCal Recurrance Rule`_
                format.  Further this parameter is only required when specifying
                the schedule_type as ``ical``.
            action (list):
                The action(s) that will be performed when the alert trigger
                fires.  Each action is a dictionary detailing what type of
                action to take, and the details surrounding that action.  The
                supported type of actions are ``email``, ``notifications``,
                ``report``, ``scan``, ``syslog``, and ``ticket``.  The following
                examples lay out each type of action as an example:

                * Email action type:
                .. code-block:: python
                    
                    {'type': 'email',
                     'subject': 'Example Email Subject',
                     'message': 'Example Email Body'
                     'addresses': 'user1@company.com\\nuser2@company.com',
                     'users': [{'id': 1}, {'id': 2}],
                     'includeResults': 'true'}

                * Notification action type:
                .. code-block:: python

                    {'type': 'notification',
                     'message': 'Example notification',
                     'users': [{'id': 1}, {'id': 2}]}

                * Report action type:
                .. code-block:: python

                    {'type': 'report',
                     'report': {'id': 1}}

                * Scan action type:
                .. code-block:: python

                    {'type': 'scan',
                     'scan': {'id': 1}}

                * Syslog action type:
                .. code-block:: python

                    {'type': 'syslog',
                     'host': '127.0.0.1',
                     'port': '514',
                     'message': 'Example Syslog Message',
                     'severity': 'Critical'}

                * Ticket action type:
                .. code-block:: python

                    {'type': 'ticket',
                     'assignee': {'id': 1},
                     'name': 'Example Ticket Name',
                     'description': 'Example Ticket Description',
                     'notes': 'Example Ticket Notes'}

        Returns:
            dict: The alert resource created.

        Examples:
            >>> sc.alerts.create(
            ...     ('severity', '=', '3,4'),
            ...     ('exploitAvailable', '=', 'true'),
            ...     analysis_type
            ...     trigger=('sumip', '>=', '100'),
            ...     name='Too many Hig or Critical and Exploitables',
            ...     action=[{'type': 'notification', 'users': [{'id': 1}]}]
            ... )
        '''
        payload = self._alert_creator(*filters, **kw)
        return self._api.post('alert', json=payload).json()['response']

    def update(self, id, *filters, **kw):
        '''
        Updates an existing alert.  All fields are optional and will overwrite
        the existing value.

        + `SC Alert Update <https://docs.tenable.com/sccv/api/Alert.html#alert_id_PATCH>`_

        Args:
            if (int): The alert identifier.
            *filters (tuple): 
                A filter expression.  Refer to the detailed description within
                the analysis endpoint documentation for more details on how to
                formulate filter expressions.
            data_type (str):
                The type of filters being used.  Must be of type ``lce``, 
                ``ticket``, ``user``, or ``vuln``.  If no data-type is
                specified, then the default of ``vuln`` will be set.
            name (str, optional): The name of the alert.
            description (str, optional): A description for the alert.
            trigger (tuple, optional): 
                A tuple in the filter-tuple format detailing what would
                constitute a trigger.  For example: ``('sumip', '=', '1000')``.
            always_exec_on_trigger (bool, optional):
                Should the trigger always execute when the trigger fires, or
                only execute when the returned data changes?  
                Default is ``False``.
            schedule_type (str, optional):
                What type of alert schedule shall this be?  Available supported
                values are ``dependent``, ``ical``, ``never``, ``rollover``, and
                ``template``.  The default value if unspecified is ``never``.
            schedule_start (str, optional):
                The time in which the trigger should start firing.  This value
                must conform to the `iCal Date-Time`_ standard.  Further this
                parameter is only required when specifying the schedule_type as
                ``ical``.
            schedule_repeat (str, optional):
                The rule that dictates the frequency and timing that the alert
                will run.  This value must conform to the `iCal Recurrance Rule`_
                format.  Further this parameter is only required when specifying
                the schedule_type as ``ical``.
            action (list):
                The action(s) that will be performed when the alert trigger
                fires.  Each action is a dictionary detailing what type of
                action to take, and the details surrounding that action.

        Returns:
            dict: The modified alert resource.

        Examples:
            >>> sc.alerts.update(1, name='New Alert Name')
        '''
        payload = self._alert_creator(*filters, **kw)
        return self._api.patch('alert/{}'.format(
            self._check('id', id, int)), json=payload).json()['response']

    def delete(self, id):
        '''
        Deletes the specified alert.

        + `SC Alert Delete <https://docs.tenable.com/sccv/api/Alert.html#alert_id_DELETE>`_

        Args:
            id (int): The alert identifier.

        Returns:
            str: The response code of the action.

        Examples:
            >>> sc.alerts.delete(1)
        '''
        return self._api.delete('alert/{}'.format(
            self._check('id', id, int))).json()['response']

    def execute(self, id):
        '''
        Executes the specified alert.

        + `SC Alert Execute <https://docs.tenable.com/sccv/api/Alert.html#AlertRESTReference-/alert/{id}/execute>`_

        Args:
            id (int): The alert identifier.

        Returns:
            dict: The alert resource.
        '''
        return self._api.post('alert/{}/execute'.format(
            self._check('id', id, int))).json()['response']