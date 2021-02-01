# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
from apscheduler.schedulers.background import BackgroundScheduler

from influxdb_client import InfluxDBClient, Point
import requests


INFLUXDB_CLOUD_HOST = "https://us-central1-1.gcp.cloud2.influxdata.com"
INFLUXDB_TOKEN = "e4Z0o1Xi9VlQH8V4Axuuf1gFNeAEdu1DXwcJ4ENpkjSIB9a67EEajiSN3GOu3JCOQakTjpPTxS2woXRseW-fPQ=="

INFLUXDB_BUCKETID = "6bf8ad0732605327"
INFLUXDB_ORGID = "b6cceae0afcd3264"

X_API_KEY = "B887E7558B4C4AA8A5EC1138F6E5F8D8"



# job related data
def data_convert_job(data):
    converted_data = []
    job_data = data.get("job")
    progress_data = data.get("progress")

    job_progress_point = Point("job_progress").tag("X-API-KEY", X_API_KEY)\
        .field("completion", progress_data.get("completion") if progress_data.get("completion") is not None else 0.0)\
        .field("filepos", progress_data.get("filepos"))\
        .field("printTime", progress_data.get("printTime"))\
        .field("printTimeLeft", progress_data.get("printTimeLeft"))\
        .field("printTimeLeftOrigin", progress_data.get("printTimeLeftOrigin"))
    converted_data.append(job_progress_point)

    if job_data.get("filament") is None:
        return converted_data

    for filament_toolname, filament_info in job_data.get("filament").items():
        if filament_info is None:
            break

        job_info_point = Point("job_info").tag("X-API-KEY", X_API_KEY)\
            .tag("filament", filament_toolname) \
            .field("averagePrintTime",
                   job_data.get("averagePrintTime", 0.0) if filament_info.get("averagePrintTime") is None else 0.0) \
            .field("estimatedPrintTime", job_data.get("averagePrintTime", 0.0) if filament_info.get("estimatedPrintTime") is None else 0.0) \
            .field("filament_length", filament_info.get("length", 0.0) if filament_info.get("length") is None else 0.0) \
            .field("filament_volume", filament_info.get("volume", 0.0) if filament_info.get("volume") is None else 0.0) \
            .field("file_date", job_data.get("file").get("date"))\
            .field("file_display", job_data.get("file").get("display")) \
            .field("file_name", job_data.get("file").get("name")) \
            .field("file_origin", job_data.get("file").get("origin"))\
            .field("file_path", job_data.get("file").get("path"))\
            .field("file_size", job_data.get("file").get("size")) \
            .field("lastPrintTime", job_data.get("lastPrintTime", 0.0) if filament_info.get("lastPrintTime") is None else 0.0) \
            .field("user", job_data.get("user"))

        converted_data.append(job_info_point)

    return converted_data


def load_data_job():
    url = "http://octopi.local/api/job"

    headers = {
        "X-Api-Key": X_API_KEY,
        "Content-Type": "application/json"
    }
    res_job = requests.get(url, headers=headers).json()
    print(res_job)

    dbClient = InfluxDBClient(url=INFLUXDB_CLOUD_HOST, token=INFLUXDB_TOKEN)
    write_api = dbClient.write_api()

    for data_point in data_convert_job(res_job):
        write_api.write(INFLUXDB_BUCKETID, INFLUXDB_ORGID, data_point)


# connection related data

def data_convert_connection(data):
    converted_data = []
    current_data = data.get("current")

    connection_current_point = Point("connection_current").tag("X-API-KEY", X_API_KEY)\
        .field("baudrate", current_data.get("baudrate"))\
        .field("port", current_data.get("port"))\
        .field("printerProfile", current_data.get("printerProfile"))\
        .field("state", current_data.get("state"))
    converted_data.append(connection_current_point)

    return converted_data

def load_data_connection():
    url = "http://octopi.local/api/connection"

    headers = {
        "X-Api-Key": X_API_KEY,
        "Content-Type": "application/json"
    }
    res_connection = requests.get(url, headers=headers).json()
    print(res_connection["current"])

    dbClient = InfluxDBClient(url=INFLUXDB_CLOUD_HOST, token=INFLUXDB_TOKEN)
    write_api = dbClient.write_api()

    for data_point in data_convert_connection(res_connection):
        write_api.write(INFLUXDB_BUCKETID, INFLUXDB_ORGID, data_point)



# printer related data

def data_convert_printer(data):
    converted_data = []
    state_data = data.get("state")
    temperature_data = data.get("temperature")

    printer_state_point = Point("printer_state").tag("X-API-KEY", X_API_KEY)\
        .field("flags_cancelling", state_data.get("flags").get("cancelling"))\
        .field("flags_closedOrError", state_data.get("flags").get("error"))\
        .field("flags_finishing", state_data.get("flags").get("finishing"))\
        .field("flags_operational", state_data.get("flags").get("operational"))\
        .field("flags_paused", state_data.get("flags").get("paused"))\
        .field("flags_pausing", state_data.get("flags").get("pausing"))\
        .field("flags_printing", state_data.get("flags").get("printing"))\
        .field("flags_ready", state_data.get("flags").get("ready"))\
        .field("flags_resuming", state_data.get("flags").get("resuming"))\
        .field("flags_sdReady", state_data.get("flags").get("sdReady"))\
        .field("text", state_data.get("text"))
    converted_data.append(printer_state_point)

    printer_temperature_point = Point("printer_temperature").tag("X-API-KEY", X_API_KEY)\
        .field("bed_actual", temperature_data.get("bed").get("actual") if temperature_data.get("bed").get("actual") is not None else 0.0)\
        .field("bed_offset", temperature_data.get("bed").get("offset") if temperature_data.get("bed").get("offset") is not None else 0.0)\
        .field("bed_target", temperature_data.get("bed").get("target") if temperature_data.get("bed").get("target") is not None else 0.0)\
        .field("tool0_actual", temperature_data.get("tool0").get("actual") if temperature_data.get("tool0").get("actual") is not None else 0.0)\
        .field("tool0_offset", temperature_data.get("tool0").get("offset") if temperature_data.get("tool0").get("offset") is not None else 0.0)\
        .field("tool0_target", temperature_data.get("tool0").get("target") if temperature_data.get("tool0").get("target") is not None else 0.0)
    converted_data.append(printer_temperature_point)

    return converted_data


def load_data_printer():
    url = "http://octopi.local/api/printer"

    headers = {
        "X-Api-Key": X_API_KEY,
        "Content-Type": "application/json"
    }
    res_printer = requests.get(url, headers=headers).json()
    print(res_printer["state"]["flags"])
    print(res_printer["temperature"]["bed"])
    print(res_printer["temperature"]["tool0"])

    dbClient = InfluxDBClient(url=INFLUXDB_CLOUD_HOST, token=INFLUXDB_TOKEN)
    write_api = dbClient.write_api()

    for data_point in data_convert_printer(res_printer):
        write_api.write(INFLUXDB_BUCKETID, INFLUXDB_ORGID, data_point)



# printer profiles related data

def data_convert_printer_profiles(data, current_profile):
    converted_data = []
    current_profile = data.get(current_profile)

    specification_axes = current_profile.get("axes")
    specification_axes_e = specification_axes.get("e")
    specification_axes_x = specification_axes.get("x")
    specification_axes_y = specification_axes.get("y")
    specification_axes_z = specification_axes.get("z")
    specification_extruder = current_profile.get("extruder")
    specification_volume = current_profile.get("volume")

    printer_profiles_specification_point = Point("printer_profiles_specification").tag("X-API-KEY", X_API_KEY)\
            .tag("current_profile", current_profile)\
        .field("specification_axes_e_inverted", specification_axes_e.get("inverted"))\
        .field("specification_axes_e_speed", specification_axes_e.get("speed"))\
        .field("specification_axes_x_inverted", specification_axes_x.get("inverted"))\
        .field("specification_axes_x_speed", specification_axes_x.get("speed"))\
        .field("specification_axes_y_inverted", specification_axes_y.get("inverted"))\
        .field("specification_axes_y_speed", specification_axes_y.get("speed"))\
        .field("specification_axes_z_inverted", specification_axes_z.get("inverted"))\
        .field("specification_axes_z_speed", specification_axes_z.get("speed"))\
        .field("specification_extruder_count", specification_extruder.get("count"))\
        .field("specification_extruder_nozzleDiameter", specification_extruder.get("nozzleDiameter") if specification_extruder.get("nozzleDiameter") is not None else 0.0)\
        .field("specification_extruder_sharedNozzle", specification_extruder.get("sharedNozzle"))\
        .field("specification_volume_custom_box", specification_volume.get("custom_box"))\
        .field("specification_volume_depth", specification_volume.get("depth") if specification_extruder.get("depth") is not None else 0.0)\
        .field("specification_volume_formFactor", specification_volume.get("formFactor"))\
        .field("specification_volume_height", specification_volume.get("height") if specification_extruder.get("height") is not None else 0.0)\
        .field("specification_volume_origin", specification_volume.get("origin"))\
        .field("specification_volume_width", specification_volume.get("width") if specification_extruder.get("width") is not None else 0.0)\
        .field("id", current_profile.get("id"))\
        .field("model", current_profile.get("model"))\
        .field("name", current_profile.get("name"))
    converted_data.append(printer_profiles_specification_point)

    return converted_data


def load_data_printer_profile():
    url_connection = "http://octopi.local/api/connection"

    headers = {
        "X-Api-Key": X_API_KEY,
        "Content-Type": "application/json"
    }
    res_connection = requests.get(url_connection, headers=headers).json()
    print(res_connection["current"])
    current_profile = res_connection["current"].get("printerProfile", "_default")

    url_printerprofiles = "http://octopi.local/api/printerprofiles"

    res_printer_profiles = requests.get(url_printerprofiles, headers=headers).json()["profiles"]
    print(res_printer_profiles[current_profile]["axes"])
    print(res_printer_profiles[current_profile]["extruder"])
    print(res_printer_profiles[current_profile]["id"])
    print(res_printer_profiles[current_profile]["model"])
    print(res_printer_profiles[current_profile]["name"])
    print(res_printer_profiles[current_profile]["volume"])

    dbClient = InfluxDBClient(url=INFLUXDB_CLOUD_HOST, token=INFLUXDB_TOKEN)
    write_api = dbClient.write_api()

    for data_point in data_convert_printer_profiles(res_printer_profiles, current_profile):
        write_api.write(INFLUXDB_BUCKETID, INFLUXDB_ORGID, data_point)


class CmfgdataacquisitionPlugin(octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.AssetPlugin,
                                octoprint.plugin.TemplatePlugin,
							 	octoprint.plugin.StartupPlugin,
							 	octoprint.plugin.ShutdownPlugin):

	def __init__(self):
		super().__init__()
		self.backgroundScheduler = BackgroundScheduler()

	def on_after_startup(self):
		self.start_schedule()

	def on_shutdown(self):
		self.backgroundScheduler.shutdown()

	def call_job_api(self):
		# Data of print time (average, estimate, last print time), tool information, file (g-code) information, user information;
		# progress information (completion, filepos, printTime, printTimeLeft, printTimeLeftOrigin)
		# (Availability and Feasibility related information)
		load_data_job()

	def call_connection_api(self):
		# Data of printer's ID and name, baud rate and port, and printer state as well (Capability related data)
		load_data_connection()

	def call_printer_api(self):
		# Data of printer's state, tool and bed's real-time and target temperature (Availability related data)
		load_data_printer()

	def call_printer_profiles_api(self):
		# Data of printer specifications, including printer speed, extruder information,
		# printer's model, volume, and name. (Capability and Feasibility related information)
		load_data_printer_profile()

	def start_schedule(self):
		self._logger.info("Schedule starting")
		self.backgroundScheduler.add_job(self.call_job_api, 'interval', seconds=5)
		self.backgroundScheduler.add_job(self.call_connection_api, 'interval', seconds=30)
		self.backgroundScheduler.add_job(self.call_printer_api, 'interval', seconds=3)
		self.backgroundScheduler.add_job(self.call_printer_profiles_api, 'interval', seconds=60)
		self.backgroundScheduler.start()

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/CMfgDataAcquisition.js"],
			css=["css/CMfgDataAcquisition.css"],
			less=["less/CMfgDataAcquisition.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			CMfgDataAcquisition=dict(
				displayName="Cmfgdataacquisition Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="qinzhaojun93",
				repo="test_ZS",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/qinzhaojun93/test_ZS/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Cmfgdataacquisition Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CmfgdataacquisitionPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

