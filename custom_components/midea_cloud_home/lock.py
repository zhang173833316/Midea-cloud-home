# custom_components/midea_cloud_home/lock.py
import logging
from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import MideaCoordinator  # 您的数据协调器类

_LOGGER = logging.getLogger(__name__)

class MideaLockEntity(CoordinatorEntity, LockEntity):
    """美的智能门锁实体（显示状态+操控）"""
    _attr_has_entity_name = True
    _attr_supported_features = LockEntityFeature.OPEN  # 支持开门操作

    def __init__(self, coordinator: MideaCoordinator, device_id: str, device_info: dict):
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_info = device_info
        self._attr_unique_id = f"{device_id}_lock"  # 唯一ID（不能重复）
        self._attr_name = "智能门锁"  # 实体名称
        self._attr_device_info = {  # 关联设备（与门锁分组）
            "identifiers": {(DOMAIN, device_id)},
            "name": device_info.get("name", "美的智能门锁"),
            "manufacturer": "Midea",
            "model": device_info.get("model", "BF530-S3B"),
        }

    @property
    def is_locked(self) -> bool | None:
        """获取锁状态（锁定=True，解锁=False）"""
        device_data = self.coordinator.data.get(self._device_id, {})
        lock_state = device_data.get("lock_state")  # 从协调器数据中获取锁状态（需确保协调器解析了该字段）
        return lock_state == "locked"  # 假设API返回"locked"或"unlocked"
