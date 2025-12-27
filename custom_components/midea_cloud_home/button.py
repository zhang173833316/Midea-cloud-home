from homeassistant.components.button import ButtonEntity
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
    """Set up button entities for Midea devices."""
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
        entities_cfg = (config.get("entities") or {}).get(Platform.BUTTON, {})
        manufacturer = config.get("manufacturer")
        rationale = config.get("rationale")
        coordinator = coordinator_map.get(device_id)
        device = coordinator.device if coordinator else None
        for entity_key, ecfg in entities_cfg.items():
            devs.append(MideaButtonEntity(
                coordinator, device, manufacturer, rationale, entity_key, ecfg
            ))
    async_add_entities(devs)


class MideaButtonEntity(MideaEntity, ButtonEntity):
    """Midea button entity."""

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

    async def async_press(self) -> None:
        """Handle the button press."""
        # 从配置中获取要执行的命令或操�?
        command = self._config.get("command")
        attribute = self._config.get("attribute", self._entity_key)
        value = self._config.get("value")
        
        # 判断是否为中央空调设备（T0x21�?
        is_central_ac = self._device.device_type == 0x21 if self._device else False
        
        if command:
            # 如果配置中指定了命令，执行该命令
            if isinstance(command, dict):
                # 如果是字典，可能需要发送多个属�?
                await self.async_set_attributes(command)
            elif isinstance(command, str):
                # 如果是字符串，可能是特殊命令类型
                await self._async_execute_command(command)
        elif value is not None:
            # 如果配置中指定了值，设置该属性�?
            await self.async_set_attribute(attribute, value)
        else:
            # 默认行为：如果没有指定命令或值，记录警告
            MideaLogger.warning(
                f"Button {self._entity_key} has no command or value configured"
            )

    async def _async_execute_command(self, command: str) -> None:
        """Execute a special command."""
        # 这里可以处理特殊的命令类�?
        # 例如：重启、重置、测试等
        if command == "reset" or command == "restart":
            # 可以在这里实现重置或重启逻辑
            MideaLogger.debug(f"Executing {command} command for button {self._entity_key}")
        else:
            # 对于其他命令，可以通过 coordinator 发�?
            await self.coordinator.async_send_command(0, command)

