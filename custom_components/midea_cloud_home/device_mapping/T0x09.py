# T0x09设备类型映射配置文件
# 定义了美的智能门锁在Home Assistant中的表示方式和控制逻辑

# 导入Home Assistant相关常量和设备类
from homeassistant.const import Platform, UnitOfTemperature, UnitOfVolume, UnitOfTime, PERCENTAGE, PRECISION_HALVES, \
    UnitOfEnergy, UnitOfPower, PRECISION_WHOLE
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.lock import LockState

# 设备映射配置字典
DEVICE_MAPPING = {
    "default": {
        # 控制选项映射，定义了设备可以执行的操�?
        "rationale": ["unlock", "lock"],
        # 查询命令列表，用于获取设备状�?
        "queries": [{}],
        # 集中式控制功能列�?
        "centralized": [],
        # Home Assistant实体映射配置
        "entities": {
            Platform.LOCK: {
                "door_lock": {
                    # 门锁设备类定�?
                    "device_class": LockState,
                    # 门锁的控制选项映射
                    "rationale": ['unlock', 'lock']
                }
            },
            Platform.SENSOR: {
                "battery_level": {
                    # 电池电量传感器配�?
                    "device_class": SensorDeviceClass.BATTERY,
                    "unit_of_measurement": PERCENTAGE,
                    "state_class": SensorStateClass.MEASUREMENT
                }
            },
            Platform.BINARY_SENSOR: {
                "door_status": {
                    # 门状态二进制传感器配�?
                    "device_class": BinarySensorDeviceClass.DOOR,
                    "rationale": ['closed', 'open']
                },
                "lock_status": {
                    # 锁状态二进制传感器配�?
                    "device_class": BinarySensorDeviceClass.LOCK,
                    "rationale": ['locked', 'unlocked']
                }
            }
        }
    }
}
