import logging
from typing import Any

from homeassistant.components.lock import LockEntity, LockDeviceClass
from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .core.logger import MideaLogger
from .midea_entity import MideaEntity
from . import load_device_config

_LOGGER = logging.getLogger(__name__)

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
        self._is_locked = None

    @property
    def is_locked(self) -> bool:
        """Return True if the lock is locked."""
        # 从设备属性获取锁状�?
        lock_status = self._get_nested_value(self._entity_key)
        if lock_status is not None:
            return self._get_status_on_off(self._entity_key)
        
        # 尝试从其他可能的属性获取状�?
        for attr in ["lock_status", "door_status"]:
            status = self._get_nested_value(attr)
            if status is not None:
                return status in ["locked", "closed", "1", 1, True]
        
        return self._is_locked

    @property
    def is_locking(self) -> bool:
        """Return True if the lock is locking."""
        return False

    @property
    def is_unlocking(self) -> bool:
        """Return True if the lock is unlocking."""
        return False

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the lock."""
        # 使用rationale中的锁定�?
        lock_value = self._rationale[1] if len(self._rationale) > 1 else "lock"
        await self._async_set_status_on_off(self._entity_key, True)
        self._is_locked = True

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the lock."""
        # 使用rationale中的解锁�?
        unlock_value = self._rationale[0] if len(self._rationale) > 0 else "unlock"
        await self._async_set_status_on_off(self._entity_key, False)
        self._is_locked = False

    async def async_open(self, **kwargs: Any) -> None:
        """Open the door latch."""
        # 如果设备支持开门功�?
        await self.async_unlock(**kwargs)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.data.available

    @property
    def assumed_state(self) -> bool:
        """Return True if unable to access real state of the entity."""
        return False
