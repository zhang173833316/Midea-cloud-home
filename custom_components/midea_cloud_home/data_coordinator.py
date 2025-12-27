"""Data coordinator for Midea Auto Cloud integration."""

import logging
import traceback
from datetime import datetime, timedelta
from typing import NamedTuple

from attr import attributes
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .core.device import MiedaDevice
from .core.logger import MideaLogger

_LOGGER = logging.getLogger(__name__)


class MideaDeviceData(NamedTuple):
    """Data structure for Midea device state."""
    attributes: dict
    available: bool
    connected: bool


class MideaDataUpdateCoordinator(DataUpdateCoordinator[MideaDeviceData]):
    """Data update coordinator for Midea devices."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: MiedaDevice,
        cloud=None,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{device.device_name} ({device.device_id})",
            update_method=self.poll_device_state,
            update_interval=timedelta(seconds=30),
            always_update=False,
        )
        self.device = device
        self.state_update_muted: CALLBACK_TYPE | None = None
        self._device_id = device.device_id
        self._cloud = cloud

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        # Immediate first refresh to avoid waiting for the interval
        self.data = await self.poll_device_state()
        
        # Register for device updates
        self.device.register_update(self._device_update_callback)

    def mute_state_update_for_a_while(self) -> None:
        """Mute subscription for a while to avoid state bouncing."""
        if self.state_update_muted:
            self.state_update_muted()

        @callback
        def unmute(now: datetime) -> None:
            self.state_update_muted = None

        self.state_update_muted = async_call_later(self.hass, 10, unmute)

    def _device_update_callback(self, status: dict) -> None:
        """Callback for device status updates."""
        if self.state_update_muted:
            return
        
        # Update device attributes (allow new keys to be added)
        for key, value in status.items():
            self.device.attributes[key] = value
        
        # Update coordinator data
        self.async_set_updated_data(
            MideaDeviceData(
                attributes=self.device.attributes,
                available=self.device.connected,
                connected=self.device.connected,
            )
        )

    async def poll_device_state(self) -> MideaDeviceData:
        """Poll device state."""
        if self.state_update_muted:
            return self.data

        try:
            # 检查是否为中央空调设备（T0x21�?
            if self.device.device_type == 0x21:
                await self._poll_central_ac_state()
            else:
                await self.device.refresh_status()

            # 返回并推送当前状�?
            updated = MideaDeviceData(
                attributes=self.device.attributes,
                available=self.device.connected,
                connected=self.device.connected,
            )
            self.async_set_updated_data(updated)
            return updated
        except Exception as e:
            _LOGGER.error(f"Error polling device state: {e}")
            return MideaDeviceData(
                attributes=self.device.attributes,
                available=False,
                connected=False,
            )
    
    async def _poll_central_ac_state(self) -> None:
        """轮询中央空调状�?""
        try:
            cloud = self._cloud
            if cloud and hasattr(cloud, "get_central_ac_status"):
                status_data = await cloud.get_central_ac_status([self._device_id])
                if status_data and "appliances" in status_data:
                    # 找到对应的设备数据并更新到设备属性中
                    for appliance in status_data["appliances"]:
                        if appliance.get("type") == "0x21" and "extraData" in appliance:
                            extra_data = appliance["extraData"]
                            if "attr" in extra_data:
                                if "nodeid" in extra_data["attr"]:
                                    self.device._attributes["nodeid"] = extra_data["attr"]["nodeid"]
                                if "masterId" in extra_data["attr"]:
                                    self.device._attributes["masterId"] = extra_data["attr"]["masterId"]
                                if "modelid" in extra_data["attr"]:
                                    self.device._attributes["modelid"] = extra_data["attr"]["modelid"]
                                if "idType" in extra_data["attr"]:
                                    self.device._attributes["idType"] = extra_data["attr"]["idType"]

                                if "state" in extra_data["attr"] and "condition_attribute" in extra_data["attr"]["state"]:
                                    state = extra_data["attr"]["state"]
                                    condition = state["condition_attribute"]
                                    # 将状态数据更新到设备属性中
                                    for key, value in condition.items():
                                        # 尝试将数字字符串转换为数�?
                                        if key.find("temp") > -1:
                                            try:
                                                # 尝试转换为整�?
                                                if '.' not in value:
                                                    self.device._attributes[key] = int(value)
                                                else:
                                                    # 尝试转换为浮点数
                                                    self.device._attributes[key] = float(value)
                                            except (ValueError, TypeError):
                                                # 如果转换失败，保持原�?
                                                self.device._attributes[key] = value
                                        else:
                                            self.device._attributes[key] = value

                                if "endlist" in extra_data["attr"]:
                                    endlist = extra_data["attr"]["endlist"]
                                    # endlist是一个数组，包含多个endpoint对象
                                    if isinstance(endlist, list):
                                        for endpoint in endlist:
                                            if "event" in endpoint:
                                                event = endpoint["event"]
                                                endpoint_id = endpoint.get("endpoint", 1)
                                                endpoint_name = endpoint.get("name", f"按键{endpoint_id}")
                                                
                                                # 为每个endpoint创建独立的状态属�?
                                                for key, value in event.items():
                                                    # 创建带endpoint标识的属性名
                                                    attr_key = f"endpoint_{endpoint_id}_{key}"
                                                    attr_name_key = f"endpoint_{endpoint_id}_name"
                                                    
                                                    # 保存endpoint名称
                                                    self.device._attributes[attr_name_key] = endpoint_name
                                                    self.device._attributes[attr_key] = value
                                                
                                                # 同时保持原有的属性名（用于兼容性）
                                                for key, value in event.items():
                                                    # 尝试将数字字符串转换为数�?
                                                    self.device._attributes[key] = value

                                break
        except Exception as e:
            MideaLogger.debug(f"Error polling central AC state: {e}")

    async def async_set_attribute(self, attribute: str, value) -> None:
        """Set a device attribute."""
        attributes = {}
        attributes[attribute] = value
        await self.async_set_attributes(attributes)

    async def async_set_attributes(self, attributes: dict) -> None:
        """Set multiple device attributes."""
        # 云端控制：构�?control �?status（携带当前状态作为上下文�?
        for c in self.device._calculate_set:
            lvalue = c.get("lvalue")
            rvalue = c.get("rvalue")
            if lvalue and rvalue:
                calculate = False
                for s, v in attributes.items():
                    if rvalue.find(f"[{s}]") >= 0:
                        calculate = True
                        break
                if calculate:
                    calculate_str1 = \
                        (f"{lvalue.replace('[', 'attributes[').replace("]", "\"]")} = "
                         f"{rvalue.replace('[', 'attributes[').replace(']', "\"]")}") \
                            .replace("[", "[\"")
                    try:
                        exec(calculate_str1)
                    except Exception as e:
                        traceback.print_exc()
                        MideaLogger.warning(
                            f"Calculation Error: {lvalue} = {rvalue}, calculate_str1: {calculate_str1}",
                            self._device_id
                        )
        await self.device.set_attributes(attributes)
        self.device.attributes.update(attributes)
        self.mute_state_update_for_a_while()
        self.async_update_listeners()

    async def async_send_command(self, cmd_type: int, cmd_body: str) -> None:
        """Send a command to the device."""
        try:
            cmd_body_bytes = bytearray.fromhex(cmd_body)
            self.device.send_command(cmd_type, cmd_body_bytes)
        except ValueError as e:
            _LOGGER.error(f"Invalid command body: {e}")
            raise

    async def async_send_central_ac_control(self, control: dict) -> bool:
        """发送中央空调控制命�?""
        try:
            cloud = self._cloud
            if cloud and hasattr(cloud, "send_central_ac_control"):
                # 从设备属性中获取nodeid
                masterid = self.device.attributes.get("masterId")
                nodeid = self.device.attributes.get("nodeid")
                modelid = self.device.attributes.get("modelid")
                idtype = int(self.device.attributes.get("idType"))

                if not nodeid:
                    MideaLogger.warning(f"No nodeid found for central AC device {self._device_id}")
                    return False
                
                # 构建完整的控制命令，包含centralized中的所有字�?
                full_control = self._build_full_central_ac_control(control)
                MideaLogger.debug(f"Sending control to {self.device.device_name}: {full_control}")
                success = await cloud.send_central_ac_control(
                    masterid,
                    nodeid,
                    modelid,
                    idtype,
                    full_control
                )

                if success:
                    # 更新本地状�?
                    self.device.attributes.update(control)
                    self.mute_state_update_for_a_while()
                    self.async_update_listeners()
                    return True
                else:
                    MideaLogger.debug(f"Failed to send control to {self.device.device_name}")
                    return False
            else:
                MideaLogger.debug("Cloud service not available for central AC control")
                return False
        except Exception as e:
            MideaLogger.debug(f"Error sending control to {self.device.device_name}: {e}")
            return False

    async def async_send_switch_control(self, control: dict) -> bool:
        """发送开关控制命令（subtype�?0000000的设备）"""
        try:
            cloud = self._cloud
            if cloud and hasattr(cloud, "send_switch_control"):
                # 获取设备ID和nodeId
                masterid = str(self.device.attributes.get("masterId"))
                nodeid = str(self.device.attributes.get("nodeid"))
                
                if not nodeid:
                    MideaLogger.warning(f"No nodeid found for switch device {self._device_id}")
                    return False
                
                # 根据控制命令确定endPoint和attribute�?
                end_point = control.get("endpoint", 1)  # 从control中获取endpoint，默�?
                attribute = 0  # 默认attribute
                
                # 根据control内容设置attribute�?
                if "run_mode" in control:
                    if control["run_mode"] == "1":
                        attribute = 1  # 开�?
                    else:
                        attribute = 0  # 关闭
                
                # 构建控制数据
                switch_control = {
                    "endPoint": end_point,
                    "attribute": attribute
                }
                
                MideaLogger.debug(f"Sending switch control to {self.device.device_name}: {switch_control}")
                success = await cloud.send_switch_control(masterid, nodeid, switch_control)
                
                if success:
                    # 更新本地状�?- 使用类似poll_central的解析方�?
                    await self._update_switch_status_from_control(control)
                    self.mute_state_update_for_a_while()
                    self.async_update_listeners()
                    return True
                else:
                    MideaLogger.debug(f"Failed to send switch control to {self.device.device_name}")
                    return False
            else:
                MideaLogger.debug("Cloud service not available for switch control")
                return False
        except Exception as e:
            MideaLogger.debug(f"Error sending switch control to {self.device.device_name}: {e}")
            return False

    async def _update_switch_status_from_control(self, control: dict) -> None:
        """根据控制命令更新开关状态，参照poll_central的解析方�?""
        try:
            # 获取endpoint ID
            endpoint_id = control.get("endpoint", 1)
            run_mode = control.get("run_mode", "0")
            
            # 模拟endlist数据结构来更新状�?
            # 根据run_mode设置OnOff状�?
            onoff_value = "1" if run_mode == "1" else "0"
            
            # 更新endpoint特定的状态属�?
            attr_key = f"endpoint_{endpoint_id}_OnOff"
            self.device._attributes[attr_key] = onoff_value
            
            # 同时更新兼容性属�?
            self.device._attributes["OnOff"] = onoff_value
            
            MideaLogger.debug(f"Updated switch status for endpoint {endpoint_id}: OnOff={onoff_value}")
            
        except Exception as e:
            MideaLogger.debug(f"Error updating switch status from control: {e}")

    def _build_full_central_ac_control(self, new_control: dict) -> dict:
        """构建完整控制命令"""
        full_control = {}
        full_control["run_mode"] = self.device.attributes.get("run_mode")
        full_control["cooling_temp"] = str(self.device.attributes.get("cool_temp_set") or 26.0)
        full_control["heating_temp"] = str(self.device.attributes.get("heat_temp_set") or 20.0)
        full_control["fan_speed"] = self.device.attributes.get("fan_speed")
        swing_mode = self.device.attributes.get("is_swing")
        is_elec_heat = self.device.attributes.get("is_elec_heat")

        if swing_mode == "1":
            # 开启摆风：如果当前有电辅热(2)，则设为6(电辅�?摆风)，否则设�?(摆风)
            if is_elec_heat == "1":
                new_extflag = "6"  # 电辅�?摆风
            else:
                new_extflag = "4"  # 仅摆�?
        else:
            # 关闭摆风：如果当前是6(电辅�?摆风)，则设为2(仅电辅热)，否则设�?(关闭)
            if is_elec_heat == "1":
                new_extflag = "2"  # 仅电辅热
            else:
                new_extflag = "0"  # 关闭

        full_control["extflag"] = new_extflag

        # 然后用新的控制值覆�?
        full_control.update(new_control)
        return full_control
