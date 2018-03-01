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
