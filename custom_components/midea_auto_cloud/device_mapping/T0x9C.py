from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower, PRECISION_WHOLE, UnitOfPressure
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["off", "on"],
        "queries": [{}],
        "centralized": [],
        "entities": {
            Platform.NUMBER: {
                "b6_lightness": {
                    "min": 0,
                    "max": 100,
                    "step": 1
                }
            },
            Platform.SWITCH: {
                "total_power": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "power"
                },
                "total_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "translation_key": "lock"
                },
                "b6_light": {
                    "device_class": SwitchDeviceClass.SWITCH,
                },
            },
            Platform.SELECT: {
                "b3_function_control":{
                    "options": {
                        "关闭": {"b3_work_cabinet_control": 1, "b3_function_control": 1},
                        "消毒": {"b3_work_cabinet_control": 1, "b3_function_control": 2, "b3_work_destination_time": 60},
                        "烘干": {"b3_work_cabinet_control": 1, "b3_function_control": 4, "b3_work_destination_time": 120},
                    }
                },
                "b6_gear": {
                    "options": {
                        "�?: {"b6_gear": "0"},
                        "�?: {"b6_gear": "1"},
                        "�?: {"b6_gear": "2"},
                        "�?: {"b6_gear": "3"},
                        "爆炒": {"b6_gear": "4"}
                    }
                },
                "b6_power_on_light": {
                    "options": {
                        "�?: {"b6_power_on_light": "off", "b6_setting": "power_on_light"},
                        "开": {"b6_power_on_light": "on", "b6_setting": "power_on_light"}
                    }
                },
                "b6_lock": {
                    "options": {
                        "�?: {"b6_lock": "off", "b6_setting": "lock"},
                        "开": {"b6_lock": "on", "b6_setting": "lock"}
                    }
                },
                "b6_smoke_stove_linkage_gear": {
                    "options": {
                        "1�?: {"b6_smoke_stove_linkage_gear": 1, "b6_setting": "smoke_stove_linkage"},
                        "2�?: {"b6_smoke_stove_linkage_gear": 2, "b6_setting": "smoke_stove_linkage"},
                        "3�?: {"b6_smoke_stove_linkage_gear": 3, "b6_setting": "smoke_stove_linkage"},
                    }
                },
                "b6_delay_gear_linkage_gear": {
                    "options": {
                        "1�?: {"b6_delay_gear_linkage_gear": 1, "b6_setting": "delay_gear_linkage"},
                        "2�?: {"b6_delay_gear_linkage_gear": 2, "b6_setting": "delay_gear_linkage"},
                        "3�?: {"b6_delay_gear_linkage_gear": 3, "b6_setting": "delay_gear_linkage"},
                    }
                },
                "b6_delay_time_value": {
                    "options": {
                        "�?: {"b6_delay_time": "off", "b6_setting": "delay_time"},
                        "1分钟": {"b6_delay_time": "on", "b6_delay_time_value": 1, "b6_setting": "delay_time"},
                        "2分钟": {"b6_delay_time": "on", "b6_delay_time_value": 2, "b6_setting": "delay_time"},
                        "3分钟": {"b6_delay_time": "on", "b6_delay_time_value": 3, "b6_setting": "delay_time"},
                        "4分钟": {"b6_delay_time": "on", "b6_delay_time_value": 4, "b6_setting": "delay_time"},
                        "5分钟": {"b6_delay_time": "on", "b6_delay_time_value": 5, "b6_setting": "delay_time"},
                        "6分钟": {"b6_delay_time": "on", "b6_delay_time_value": 6, "b6_setting": "delay_time"},
                        "7分钟": {"b6_delay_time": "on", "b6_delay_time_value": 7, "b6_setting": "delay_time"},
                        "8分钟": {"b6_delay_time": "on", "b6_delay_time_value": 8, "b6_setting": "delay_time"},
                        "9分钟": {"b6_delay_time": "on", "b6_delay_time_value": 9, "b6_setting": "delay_time"},
                        "10分钟": {"b6_delay_time": "on", "b6_delay_time_value": 10, "b6_setting": "delay_time"},
                    }
                }
            },
            Platform.SENSOR: {
                "b3_upstair_status": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "b6_wind_pressure": {
                    "device_class": SensorDeviceClass.PRESSURE,
                    "unit_of_measurement": UnitOfPressure.PA,
                    "state_class": SensorStateClass.MEASUREMENT
                },
                "b7_left_status": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "b7_left_gear": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "b7_right_status": {
                    "device_class": SensorDeviceClass.ENUM,
                },
                "b7_right_gear": {
                    "device_class": SensorDeviceClass.ENUM,
                }
            }
        }
    }
}
