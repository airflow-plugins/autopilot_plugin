from airflow.utils.decorators import apply_defaults

from airflow.models import BaseOperator
from airflow.hooks.S3_hook import S3Hook

from autopilot_plugin.hooks.autopilot_hook import AutopilotHook

from tempfile import NamedTemporaryFile
import json


class AutopilotToS3Operator(BaseOperator):
    """
    Autopilot to S3 Operator
    :param autopilot_conn_id:       The Airflow connection id used to store
                                    the Airflow credentials.
    :type autopilot_conn_id:        string
    :param autopilot_resource :     Resource to call. Possible values are:
                                     - lists
                                     - smart_segments
                                     - contacts/custom_fields
                                     - triggers
                                    Leave blank if you want to list all contacts.
    :type autopilot_resource:       string
    :param payload:                 *(optional)* payload to send with request.
    :type payload:                  dict
    :param results_field:           *(optional* the field with the results from
                                    the api's response. Default to "contacts",
                                    if contacts field is true else defaults
                                    to the resource's name
    :type results_field:            string
    :param ids:                     *(optional)* ids for the api call
                                    (for smart_segments)
    :type ids:                      array
    :param contacts:                *(optional)* true if the operator should get
                                    all contacts from resource.
                                    Defaults to false
    :type contacts:                 boolean
    :param s3_conn_id:              The Airflow connection id used
                                    to store the S3 credentials.
    :type s3_conn_id:               string
    :param s3_bucket:               The S3 bucket to be used
                                    to store the Autopilot data.
    :type s3_bucket:                string
    :param s3_key:                  The S3 key to be used to store
                                    the Autopilot data.
    :type s3_bucket:                string
    """
    template_field = ('s3_key', )

    @apply_defaults
    def __init__(self,
                 autopilot_conn_id,
                 autopilot_resource='',
                 results_field=None,
                 ids=None,
                 contacts=False,
                 s3_conn_id=None,
                 s3_bucket=None,
                 s3_key=None,
                 payload=None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.autopilot_conn_id = autopilot_conn_id
        self.autopilot_resource = autopilot_resource
        self.results_field = results_field
        self.ids = ids
        self.contacts = contacts
        self.s3_conn_id = s3_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.payload = payload

        if self.autopilot_resource.lower() not in ('lists',
                                                   'smart_segments',
                                                   'contacts/custom_fields',
                                                   'triggers'):
            raise Exception('Specified Autopilot resource not currently supported.')

    def execute(self, context):
        hook = AutopilotHook(http_conn_id=self.autopilot_conn_id)

        results = []

        if self.ids:
            for id in self.ids:
                id_endpoint = "{}/{}".format(self.autopilot_resource, id)

                if self.contacts:
                    results += self.get_all_contacts(hook,
                                                     id_endpoint,
                                                     data=self.payload
                                                     )
                else:
                    results += self.get(hook,
                                        id_endpoint,
                                        data=self.payload
                                        )
        elif self.contacts:
            results += self.get_all_contacts(hook,
                                             self.autopilot_resource,
                                             data=self.payload
                                             )
        else:
            results += self.get(hook,
                                self.autopilot_resource,
                                results_field=self.results_field,
                                data=self.payload
                                )

        with NamedTemporaryFile("w") as tmp:
            for result in results:
                tmp.write(json.dumps(result) + '\n')

            tmp.flush()

            dest_s3 = S3Hook(s3_conn_id=self.s3_conn_id)

            dest_s3.load_file(
                filename=tmp.name,
                key=self.s3_key,
                bucket_name=self.s3_bucket,
                replace=True
            )

            dest_s3.connection.close()

    def get_all_contacts(self,
                         hook,
                         resource,
                         data=None,
                         headers=None,
                         extra_options=None):
        """
        Get contacts from all pages.
        """
        all_pages = []
        total_contacts = -1
        next_token = None

        while len(all_pages) != total_contacts:
            if not next_token:
                result = hook.run('{}/contacts'.format(resource),
                                  data,
                                  headers,
                                  extra_options).json()
            else:
                result = hook.run('{}/contacts/{}'.format(resource, next_token),
                                  data,
                                  headers,
                                  extra_options).json()

            all_pages += result.get('contacts', None)

            total_contacts = result.get('total_contacts', None)

            if 'bookmark' in result:
                next_token = result.get('bookmark', None)

        return all_pages

    def get(self,
            hook,
            endpoint,
            results_field=None,
            data=None,
            headers=None,
            extra_options=None):

        result = hook.run(endpoint, data, headers, extra_options).json()
        if not results_field:
            results_field = endpoint

        if results_field in result:
            return result.get(results_field)
        else:
            return result
