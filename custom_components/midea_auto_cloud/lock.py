from homeassistant.components.lock import LockEntity
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from . import load_device_config


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lock entities for Midea devices."""
    account_bucket = hass.data.get(DOMAIN, {}).get("accounts", {}).get(config_entry.entry_id)
    if not account_bucket:
        async_add_entities([])
        return
    device_list = account_bucket.get("device_list", {})
    coordinator_map = account_bucket.get("coordinator_map", {})

    devs = []
    for device_id, info in device_list.items():
        device_type = info.get("type")
        sn8 = info.get("sn8")
        config = await load_device_config(hass, device_type, sn8) or {}
        entities_cfg = (config.get("entities") or {}).get(Platform.LOCK, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaLockEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


class MideaLockEntity(MideaEntity, LockEntity):
    """Midea lock entity."""

    def __init__(self, coordinator, device, manufacturer, rationale, entity_key, ecfg):
        # 自动判断是否为特定设备类型（如果需要）
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
            config=ecfg,
        )

    @property
    def is_locked(self) -> bool:
        """Return true if the lock is locked."""
        # Use attribute from config if available, otherwise fall back to entity_key
        attribute = self._config.get("attribute", self._entity_key)
        value = self.device_attributes.get(attribute)
        MideaLogger.debug(f"Lock status check - Attribute: {attribute}, Value: {value}, Device ID: {self._device_id}")
        
        # Special handling for lock status
        if value is None:
            return False
        
        try:
            # Try to use the standard rationale mechanism first
            result = self._get_status_on_off(attribute)
            MideaLogger.debug(f"Lock status result using rationale: {result}")
            return result
        except Exception as e:
            MideaLogger.debug(f"Lock status check exception: {e}")
            # Fallback to direct value checking
            if isinstance(value, bool):
                return value
            if isinstance(value, int) or value in ['0', '1']:
                return int(value) == 1
            if isinstance(value, str):
                return value.lower() in ['locked', '1', 'on', 'true']
            return False

    async def async_lock(self, **kwargs):
        """Lock the lock."""
        attribute = self._config.get("attribute", self._entity_key)
        MideaLogger.debug(f"Lock command - Attribute: {attribute}, Device ID: {self._device_id}")
        await self._async_set_status_on_off(attribute, True)

    async def async_unlock(self, **kwargs):
        """Unlock the lock."""
        attribute = self._config.get("attribute", self._entity_key)
        MideaLogger.debug(f"Unlock command - Attribute: {attribute}, Device ID: {self._device_id}")
        await self._async_set_status_on_off(attribute, False)

    @property
    def device_class(self):
        """Return the device class."""
        return self._config.get("device_class", "lock")

    @property
    def entity_id_suffix(self) -> str:
        """Return the suffix for entity ID."""
        return "lock"