"""
Autopilot Hook
https://autopilot.docs.apiary.io/

This hook extends the Http Hook, changing the default method to "GET".

To authenticate with this hook, set your Autopilot API Key as the value of a
dictionary with the key "api_key" in the extras section of the connection
object.

Example. {"api_key":"XXXXXXXXXXX"}
"""

from airflow.hooks.http_hook import HttpHook


class AutopilotHook(HttpHook):
    def __init__(self, method='GET', http_conn_id='autopilot_conn'):
        super().__init__(method, http_conn_id)

    def get_conn(self, headers=None):
        conn = super().get_connection(self.http_conn_id)
        self.headers = {'autopilotapikey': conn.extra_dejson.get('api_key'),
                        'accept-encoding': 'application/json'}

        session = super().get_conn(self.headers)

        return session
