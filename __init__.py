from airflow.plugins_manager import AirflowPlugin
from autopilot_plugin.operators.autopilot_to_s3_operator import AutopilotToS3Operator
from autopilot_plugin.hooks.autopilot_hook import AutopilotHook

class autopilot_plugin(AirflowPlugin):
    name = "autopilot_plugin"
    operators = [AutopilotToS3Operator]
    hooks = [AutopilotHook]
    # Leave in for explicitness
    executors = []
    macros = []
    admin_views = []
    flask_blueprints = []
    menu_links = []
