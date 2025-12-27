from homeassistant.const import Platform
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

DEVICE_MAPPING = {
    "default": {
        "rationale": [0, 1],
        "queries": [{}],
        "centralized": ["lock", "door_status"],
        "entities": {
            Platform.LOCK: {
                "lock": {
                    "device_class": "lock",
                },
            },
            Platform.BINARY_SENSOR: {
                "door_status": {
                    "device_class": BinarySensorDeviceClass.DOOR,
                },
            },
        }
    }
}