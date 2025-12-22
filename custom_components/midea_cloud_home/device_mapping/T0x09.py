from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass

DEVICE_MAPPING = {
    "T0x09": {  # 门锁的设备类型编码
        "name": "美的智能门锁",
        "manufacturer": "Midea",
        "model": "BF530-S3B",
        "rationale": "智能门锁，支持远程锁定/解锁、电池监控等功能",
        
        # 传感器实体配置
        "entities": {
            "sensor": {
                "connectivity": {  # 连通性传感器
                    "name": "连通性",
                    "icon": "mdi:wifi",
                    "state_class": "measurement",
                    "native_unit_of_measurement": None,
                    "device_class": None,
                    "value_parser": lambda data: "在线" if data.get("online", True) else "离线"
                },
                "battery": {  # 电池电量传感器
                    "name": "电池电量",
                    "icon": "mdi:battery",
                    "state_class": "measurement",
                    "native_unit_of_measurement": "%",
                    "device_class": "battery",
                    "value_parser": lambda data: data.get("battery", 100)
                },
                "signal_strength": {  # 信号强度传感器
                    "name": "信号强度",
                    "icon": "mdi:wifi-strength-4",
                    "state_class": "measurement",
                    "native_unit_of_measurement": "dBm",
                    "device_class": "signal_strength",
                    "value_parser": lambda data: data.get("rssi", -50)
                }
            },
            
            # 锁实体配置
            "lock": {
                "main_lock": {  # 主锁实体
                    "name": "智能门锁",
                    "icon": "mdi:door-closed-lock",
                    "value_parser": lambda data: "locked" if data.get("lock_state") == 1 else "unlocked"
                }
            },
            
            # 按钮实体配置
            "button": {
                "remote_unlock": {  # 远程开锁按钮
                    "name": "远程开锁",
                    "icon": "mdi:key-wireless",
                    "device_class": "restart"
                },
                "lock_action": {  # 锁定按钮
                    "name": "锁定门锁",
                    "icon": "mdi:lock",
                    "device_class": "lock"
                },
                "unlock_action": {  # 解锁按钮
                    "name": "解锁门锁", 
                    "icon": "mdi:lock-open",
                    "device_class": "lock"
                }
            },
            
}}}
