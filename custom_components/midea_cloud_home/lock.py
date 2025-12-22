import logging
from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import MideaCoordinator  # 替换为你的协调器类名（如DataUpdateCoordinator）

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置门锁实体（锁状态+操控）。"""
    coordinator: MideaCoordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    new_entities = []
    
    # 遍历所有设备，筛选出门锁（根据设备类型，比如type="lock"或型号包含"BF530"）
    for device_id, device_info in coordinator.device_list.items():  # 替换为你的设备列表变量名
        device_type = device_info.get("type", "")
        model = device_info.get("model", "")  # 型号（如BF530-S3B）
        
        # 判断是否为门锁：设备类型是"lock"，或型号包含"BF530"（根据你的实际情况调整）
        if device_type == "lock" or "BF530" in model:
            # 添加锁实体
            new_entities.append(MideaLockEntity(coordinator, device_id, device_info))
    
    if new_entities:
        async_add_entities(new_entities)

class MideaLockEntity(CoordinatorEntity, LockEntity):
    """美的智能门锁实体（显示状态+操控）。"""
    _attr_has_entity_name = True
    _attr_supported_features = LockEntityFeature.OPEN  # 支持“开门”操作（若门锁支持）
    
    def __init__(self, coordinator, device_id, device_info):
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_info = device_info
        self._attr_unique_id = f"{device_id}_lock"  # 唯一标识（不能重复）
        self._attr_name = "智能门锁"  # 实体名称（前端显示）
        self._attr_device_info = {  # 关联设备（与门锁设备分组）
            "identifiers": {(DOMAIN, device_id)},
            "name": device_info.get("name", "美的智能门锁"),
            "manufacturer": "Midea",
            "model": device_info.get("model", "BF530-S3B"),
        }
    
    @property
    def is_locked(self) -> bool | None:
        """返回锁的当前状态（锁定=True，解锁=False）。"""
        # 从协调器数据中获取锁状态（需确保协调器已解析该字段）
        device_data = self.coordinator.data.get(self._device_id, {})
        lock_state = device_data.get("lock_state")  # 假设API返回"locked"/"unlocked"
        if lock_state == "locked":
            return True
        elif lock_state == "unlocked":
            return False
        return None  # 未知状态
    
    async def async_lock(self, **kwargs) -> None:
        """远程锁定门锁（调用美的云API）。"""
        _LOGGER.info(f"锁定门锁：{self._device_id}")
        # 调用API（需替换为你的API方法，比如coordinator.api.lock_device）
        # await self.coordinator.api.lock_device(self._device_id)
        # 模拟延迟（实际需等待API响应）
        import asyncio
        await asyncio.sleep(2)
        # 刷新数据（更新状态）
        await self.coordinator.async_request_refresh()
    
    async def async_unlock(self, **kwargs) -> None:
        """远程解锁门锁（调用美的云API）。"""
        _LOGGER.info(f"解锁门锁：{self._device_id}")
        # await self.coordinator.api.unlock_device(self._device_id)
        import asyncio
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()
    
    async def async_open(self, **kwargs) -> None:
        """开门（若门锁支持，比如虚掩状态）。"""
        _LOGGER.info(f"开门：{self._device_id}")
        # await self.coordinator.api.open_door(self._device_id)
        import asyncio
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()