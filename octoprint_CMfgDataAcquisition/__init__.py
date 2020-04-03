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

from influxdb import InfluxDBClient
import requests


# job related data
def data_convert_job(data):
    converted_data = []
    job_data = data.get("job")
    progress_data = data.get("progress")

    converted_data.append({
        "measurement": "job_progress",
        "tags": {
            "X-API-KEY": "xxxxxxxx1"
        },
        "fields": {
            "completion": progress_data.get("completion") if progress_data.get("completion") is not None else 0.0,
            "filepos": progress_data.get("filepos"),
            "printTime":progress_data.get("printTime"),
            "printTimeLeft": progress_data.get("printTimeLeft"),
            "printTimeLeftOrigin": progress_data.get("printTimeLeftOrigin"),
        }
    })

    if job_data.get("filament") is None:
        return converted_data

    for filament_toolname, filament_info in job_data.get("filament").items():
        if filament_info is None:
            break

        converted_data.append({
            "measurement": "job_info",
            "tags": {
                "X-API-KEY": "xxxxxxxx1",
                "filament": filament_toolname
            },
            "fields": {
                "averagePrintTime": job_data.get("averagePrintTime", 0.0) if filament_info.get("averagePrintTime") is None else 0.0,
                "estimatedPrintTime": job_data.get("averagePrintTime", 0.0) if filament_info.get("estimatedPrintTime") is None else 0.0,
                "filament_length": filament_info.get("length", 0.0) if filament_info.get("length") is None else 0.0,
                "filament_volume": filament_info.get("volume", 0.0) if filament_info.get("volume") is None else 0.0,
                "file_date": job_data.get("file").get("date"),
                "file_display": job_data.get("file").get("display"),
                "file_name": job_data.get("file").get("name"),
                "file_origin":job_data.get("file").get("origin"),
                "file_path": job_data.get("file").get("path"),
                "file_size": job_data.get("file").get("size"),
                "lastPrintTime": job_data.get("lastPrintTime", 0.0) if filament_info.get("lastPrintTime") is None else 0.0,
                "user": job_data.get("user")
            }
        })

    return converted_data


def load_data_job():
    url = "http://octopi.local/api/job"

    headers = {
        "X-Api-Key": "F07E6EF39FE74433BD23541996E98FFA",
        "Content-Type": "application/json"
    }
    res_job = requests.get(url, headers=headers).json()

    dbClient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database="myPluginDB")
    dbClient.write_points(data_convert_job(res_job))


# connection related data
def data_convert_connection(data):
    converted_data = []
    current_data = data.get("current")

    converted_data.append({
        "measurement": "connection_current",
        "tags": {
            "X-API-KEY": "xxxxxxxx1"
        },
        "fields": {
            "baudrate": current_data.get("baudrate"),
            "port": current_data.get("port"),
            "printerProfile": current_data.get("printerProfile"),
            "state": current_data.get("state"),
        }
    })

    return converted_data


def load_data_connection():
    url = "http://octopi.local/api/connection"

    headers = {
        "X-Api-Key": "F07E6EF39FE74433BD23541996E98FFA",
        "Content-Type": "application/json"
    }
    res_connection = requests.get(url, headers=headers).json()

    dbClient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database="myPluginDB")
    dbClient.write_points(data_convert_connection(res_connection))


# printer related data
def data_convert_printer(data):
    converted_data = []
    state_data = data.get("state")
    temperature_data = data.get("temperature")

    converted_data.append({
        "measurement": "printer_state",
        "tags": {
            "X-API-KEY": "xxxxxxxx1"
        },
        "fields": {
            "flags_cancelling": state_data.get("flags").get("cancelling"),
            "flags_closedOrError": state_data.get("flags").get("closedOrError"),
            "flags_error": state_data.get("flags").get("error"),
            "flags_finishing": state_data.get("flags").get("finishing"),
            "flags_operational": state_data.get("flags").get("operational"),
            "flags_paused": state_data.get("flags").get("paused"),
            "flags_pausing": state_data.get("flags").get("pausing"),
            "flags_printing": state_data.get("flags").get("printing"),
            "flags_ready": state_data.get("flags").get("ready"),
            "flags_resuming": state_data.get("flags").get("resuming"),
            "flags_sdReady": state_data.get("flags").get("sdReady"),
            "text": state_data.get("text")
        }
    })

    converted_data.append({
        "measurement": "printer_temperature",
        "tags": {
            "X-API-KEY": "xxxxxxxx1"
        },
        "fields": {
            "bed_actual": temperature_data.get("bed").get("actual") if temperature_data.get("bed").get("actual") is not None else 0.0,
            "bed_offset": temperature_data.get("bed").get("offset") if temperature_data.get("bed").get("offset") is not None else 0.0,
            "bed_target": temperature_data.get("bed").get("target") if temperature_data.get("bed").get("target") is not None else 0.0,
            "tool0_actual": temperature_data.get("tool0").get("actual") if temperature_data.get("tool0").get("actual") is not None else 0.0,
            "tool0_offset": temperature_data.get("tool0").get("offset") if temperature_data.get("tool0").get("offset") is not None else 0.0,
            "tool0_target": temperature_data.get("tool0").get("target") if temperature_data.get("tool0").get("target") is not None else 0.0
        }
    })

    return converted_data

def load_data_printer():
    url = "http://octopi.local/api/printer"

    headers = {
        "X-Api-Key": "F07E6EF39FE74433BD23541996E98FFA",
        "Content-Type": "application/json"
    }
    res_printer = requests.get(url, headers=headers).json()

    dbClient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database="myPluginDB")
    dbClient.write_points(data_convert_printer(res_printer))


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

    converted_data.append({
        "measurement": "printer_profiles_specification",
        "tags": {
            "X-API-KEY": "xxxxxxxx1",
            "current_profile": current_profile
        },
        "fields": {
            "specification_axes_e_inverted": specification_axes_e.get("inverted"),
            "specification_axes_e_speed": specification_axes_e.get("speed"),

            "specification_axes_x_inverted": specification_axes_x.get("inverted"),
            "specification_axes_x_speed": specification_axes_x.get("speed"),

            "specification_axes_y_inverted": specification_axes_y.get("inverted"),
            "specification_axes_y_speed": specification_axes_y.get("speed"),

            "specification_axes_z_inverted": specification_axes_z.get("inverted"),
            "specification_axes_z_speed": specification_axes_z.get("speed"),

            "specification_extruder_count": specification_extruder.get("count"),
            "specification_extruder_nozzleDiameter": specification_extruder.get("nozzleDiameter") if specification_extruder.get("nozzleDiameter") is not None else 0.0,
            "specification_extruder_sharedNozzle": specification_extruder.get("sharedNozzle"),

            "specification_volume_custom_box": specification_volume.get("custom_box"),
            "specification_volume_depth": specification_volume.get("depth") if specification_extruder.get("depth") is not None else 0.0,
            "specification_volume_formFactor": specification_volume.get("formFactor"),
            "specification_volume_height": specification_volume.get("height") if specification_extruder.get("height") is not None else 0.0,
            "specification_volume_origin": specification_volume.get("origin"),
            "specification_volume_width": specification_volume.get("width") if specification_extruder.get("width") is not None else 0.0,

            "id": current_profile.get("id"),
            "model": current_profile.get("model"),
            "name": current_profile.get("name")
        }
    })

    return converted_data


def load_data_printer_profile():
    url_connection = "http://octopi.local/api/connection"

    headers = {
        "X-Api-Key": "F07E6EF39FE74433BD23541996E98FFA",
        "Content-Type": "application/json"
    }
    res_connection = requests.get(url_connection, headers=headers).json()
    current_profile = res_connection["current"].get("printerProfile", "_default")
    url_printerprofiles = "http://octopi.local/api/printerprofiles"

    res_printer_profiles = requests.get(url_printerprofiles, headers=headers).json()["profiles"]

    dbClient = InfluxDBClient(host='localhost', port=8086, username='root', password='root', database="myPluginDB")
    dbClient.write_points(data_convert_printer_profiles(res_printer_profiles, current_profile))


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
				user="JackySu1994",
				repo="OctoPrint-Cmfgdataacquisition",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/JackySu1994/OctoPrint-Cmfgdataacquisition/archive/{target_version}.zip"
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
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = CmfgdataacquisitionPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

