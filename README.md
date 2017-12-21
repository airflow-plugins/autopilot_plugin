# Plugin - Autopilot to S3

This plugin moves data from the [Autopilot](https://autopilot.docs.apiary.io) API to S3.

## Hooks
### AutopilotHook
This hook handles the authentication and requests to Autopilot.
Inherits from the [HttpHook](https://pythonhosted.org/airflow/_modules/http_hook.html)

### S3Hook
[Core Airflow S3Hook](https://pythonhosted.org/airflow/_modules/S3_hook.html) with the standard boto dependency.

## Operators
### AutopilotToS3Operator
This operator composes the logic for this plugin. It fetches the autopilot specified resource and saves the result in a S3 Bucket, under a specified key, in ndjson format. The parameters it can accept include the following.

 - `autopilot_conn_id`: The Airflow connection id used to store
        the Airflow credentials.
 - `autopilot_resource` : resource to call. Possible values are [lists, smart_segments, contacts/custom_fields, triggers].
        Leave blank if you want to list all contacts.
 - `payload`: *(optional)* payload to send with request.
 -  `results_field`: *(optional* the field with the results from 
        the api's response. Default to "contacts",  if contacts field
         is true else defaults to the resource's name
 -  `ids`: *(optional)* ids for the api call (for smart_segments)
 - `contacts`: *(optional)* true if the operator should get all contacts from resource.
 - `s3_conn_id` :The Airflow connection id used to store the S3 credentials.
 - `s3_bucket`: The S3 bucket to be used to store the Autopilot data. 
 - `s3_key`: The S3 key to be used to store the Autopilot data.

