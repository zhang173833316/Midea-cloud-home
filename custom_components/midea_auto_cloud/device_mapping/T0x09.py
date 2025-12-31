from homeassistant.const import Platform, PERCENTAGE
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": ["0", "1"],
        "queries": [{}],
        "centralized": ["electronLock_config"],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "device_class": "lock",
                    "attribute": "electronLock_config",
                },
            },
            Platform.BINARY_SENSOR: {
                "door_status": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                    "attribute": "electronLock_config",
                },
                "battery_low": {
                    "device_class": BinarySensorDeviceClass.BATTERY,
                    "attribute": "battery_low",
                },
                "alarm": {
                    "device_class": BinarySensorDeviceClass.PROBLEM,
                    "attribute": "alarm",
                },
                "door_open": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                    "attribute": "door_state",
                },
            },
            Platform.SENSOR: {
                "battery_level": {
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT,
                    "attribute": "battery_level",
                },
                "fingerprint_count": {
                    "icon": "mdi:fingerprint",
                    "unit_of_measurement": "count",
                    "attribute": "fingerprint_count",
                },
                "password_count": {
                    "icon": "mdi:numeric",
                    "unit_of_measurement": "count",
                    "attribute": "password_count",
                },
                "card_count": {
                    "icon": "mdi:card",
                    "unit_of_measurement": "count",
                    "attribute": "card_count",
                },
                "lock_records": {
                    "icon": "mdi:history",
                    "unit_of_measurement": "records",
                    "attribute": "lock_records",
                },
            },
            Platform.SWITCH: {
                "auto_lock": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "auto_lock",
                    "rationale": ["0", "1"],
                },
                "sound": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "sound",
                    "rationale": ["0", "1"],
                },
                "security_mode": {
                    "device_class": SwitchDeviceClass.SWITCH,
                    "attribute": "security_mode",
                    "rationale": ["0", "1"],
                },
            },
        }
    }
}