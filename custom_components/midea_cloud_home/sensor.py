from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .midea_entity import MideaEntity
from . import load_device_config


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities for Midea devices."""
    account_bucket = hass.data.get(DOMAIN, {}).get("accounts", {}).get(config_entry.entry_id)
    if not account_bucket:
        async_add_entities([])
        return
    device_list = account_bucket.get("device_list", {})
    coordinator_map = account_bucket.get("coordinator_map", {})

    devs = []
    for device_id, info in device_list.items():
        device_type = info.get("type")
        if device_type == "lock" or "BF530" in model:
        # 添加电池传感器（示例）
        new_entities.append(MideaLockBatterySensor(coordinator, device_id, device_info))
        sn8 = info.get("sn8")
        config = await load_device_config(hass, device_type, sn8) or {}
        entities_cfg = (config.get("entities") or {}).get(Platform.SENSOR, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaSensorEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


class MideaSensorEntity(MideaEntity, SensorEntity):
    """Midea sensor entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, config):
        super().__init__(
            coordinator,
            device.device_id,
            device.device_name,
            f"T0x{device.device_type:02X}",
            device.sn,
            device.sn8,
            device.model,
            entity_key,
            device=device,
            manufacturer=manufacturer,
            rationale=rationale,
            config=config,
        )

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        value = self._get_nested_value(attribute)
        
        # Handle invalid string values
        if isinstance(value, str) and value.lower() in ['invalid', 'none', 'null', '']:
            return None
            
        # Try to convert to number if it's a string that looks like a number
        if isinstance(value, str):
            try:
                # Try integer first
                if '.' not in value:
                    return int(value)
                # Then float
                return float(value)
            except (ValueError, TypeError):
                # If conversion fails, return None for numeric sensors
                # or return the original string for enum sensors
                device_class = self._config.get("device_class")
                if device_class and "enum" not in device_class.lower():
                    return None
                return value
                
        return value

class MideaLockBatterySensor(CoordinatorEntity, SensorEntity):
    """美的门锁电池电量传感器。"""
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "%"  # 单位：百分比
    _attr_device_class = "battery"  # 设备类型（前端显示电池图标）

    def __init__(self, coordinator, device_id, device_info):
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_battery"
        self._attr_name = "电池电量"
        self._attr_device_info = {  # 关联门锁设备
            "identifiers": {(DOMAIN, device_id)},
            "name": device_info.get("name", "美的智能门锁"),
        }

    @property
    def native_value(self) -> int | None:
        """返回电池电量（0-100%）。"""
        device_data = self.coordinator.data.get(self._device_id, {})
        return device_data.get("battery_level")  # 假设API返回电池电量