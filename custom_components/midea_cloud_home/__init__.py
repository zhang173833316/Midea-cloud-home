import asyncio
import os
import base64
import traceback
from importlib import import_module
import re
from homeassistant.config_entries import ConfigEntry
from homeassistant.util.json import load_json

try:
    from homeassistant.helpers.json import save_json
except ImportError:
    from homeassistant.util.json import save_json
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.core import (
    HomeAssistant,
)
from homeassistant.const import (
    Platform,
    CONF_TYPE,
    CONF_PORT,
    CONF_MODEL,
    CONF_IP_ADDRESS,
    CONF_DEVICE_ID,
    CONF_PROTOCOL,
    CONF_TOKEN,
    CONF_NAME,
    CONF_DEVICE,
    CONF_ENTITIES
)

from .core.logger import MideaLogger
from .core.device import MiedaDevice
from .data_coordinator import MideaDataUpdateCoordinator
from .core.cloud import get_midea_cloud
from .const import (
    DOMAIN,
    DEVICES,
    CONF_REFRESH_INTERVAL,
    CONFIG_PATH,
    CONF_KEY,
    CONF_ACCOUNT,
    CONF_SN8,
    CONF_SN,
    CONF_MODEL_NUMBER,
    CONF_SERVERS, STORAGE_PATH, CONF_MANUFACTURER_CODE,
    CONF_SELECTED_HOMES, CONF_SMART_PRODUCT_ID, STORAGE_PLUGIN_PATH
)
# 账号型：登录云端、获取设备列表，并为每台设备建立协调器（无本地控制）
from .const import CONF_PASSWORD as CONF_PASSWORD_KEY, CONF_SERVER as CONF_SERVER_KEY

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.WATER_HEATER,
    Platform.FAN,
    Platform.LIGHT,
    Platform.HUMIDIFIER,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.LOCK
]

async def import_module_async(module_name):
    # 在线程池中执行导入操�?
    return await asyncio.to_thread(import_module, module_name, __package__)

def get_sn8_used(hass: HomeAssistant, sn8):
    entries = hass.config_entries.async_entries(DOMAIN)
    count = 0
    for entry in entries:
        if sn8 == entry.data.get("sn8"):
            count += 1
    return count


def remove_device_config(hass: HomeAssistant, sn8):
    config_file = hass.config.path(f"{CONFIG_PATH}/{sn8}.json")
    try:
        os.remove(config_file)
    except FileNotFoundError:
        pass


async def load_device_config(hass: HomeAssistant, device_type, sn8):
    def _ensure_dir_and_load(path_dir: str, path_file: str):
        os.makedirs(path_dir, exist_ok=True)
        return load_json(path_file, default={})

    config_dir = hass.config.path(CONFIG_PATH)
    config_file = hass.config.path(f"{CONFIG_PATH}/{sn8}.json")
    raw = await hass.async_add_executor_job(_ensure_dir_and_load, config_dir, config_file)
    json_data = {}
    # if isinstance(raw, dict) and len(raw) > 0:
    #     # 兼容两种文件结构�?
    #     # 1) { "<sn8>": { ...mapping... } }
    #     # 2) { ...mapping... }（直接就是映射体�?
    #     if sn8 in raw:
    #         json_data = raw.get(sn8) or {}
    #     else:
    #         # 如果像映射体（包�?entities/centralized 等关键字段），直接使�?
    #         if any(k in raw for k in ["entities", "centralized", "queries", "manufacturer"]):
    #             json_data = raw
    # if not json_data:
    device_path = f".device_mapping.{'T0x%02X' % device_type}"
    try:
        mapping_module = await import_module_async(device_path)
        for key, config in mapping_module.DEVICE_MAPPING.items():
            # support tuple & regular expression pattern to support multiple sn8 sharing one mapping
            if (key == sn8) or (isinstance(key, tuple) and sn8 in key) or (isinstance(key, str) and re.match(key, sn8)):
                json_data = config
                break
        if not json_data:
            if "default" in mapping_module.DEVICE_MAPPING:
                json_data = mapping_module.DEVICE_MAPPING["default"]
            else:
                MideaLogger.warning(f"No mapping found for sn8 {sn8} in type {'T0x%02X' % device_type}")
    except ModuleNotFoundError:
        MideaLogger.warning(f"Can't load mapping file for type {'T0x%02X' % device_type}")

    save_data = {sn8: json_data}
    # offload save_json as well
    await hass.async_add_executor_job(save_json, config_file, save_data)
    return json_data

async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if device_id is not None:
        ip_address = config_entry.options.get(
            CONF_IP_ADDRESS, None
        )
        refresh_interval = config_entry.options.get(
            CONF_REFRESH_INTERVAL, None
        )
        device: MiedaDevice = hass.data[DOMAIN][DEVICES][device_id][CONF_DEVICE]
        if device:
            if ip_address is not None:
                device.set_ip_address(ip_address)
            if refresh_interval is not None:
                device.set_refresh_interval(refresh_interval)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    hass.data.setdefault(DOMAIN, {})
    os.makedirs(hass.config.path(STORAGE_PATH), exist_ok=True)
    lua_path = hass.config.path(STORAGE_PATH)

    cjson = os.path.join(lua_path, "cjson.lua")
    bit = os.path.join(lua_path, "bit.lua")

    # 只有文件不存在时才创�?
    if not os.path.exists(cjson):
        from .const import CJSON_LUA
        cjson_lua = base64.b64decode(CJSON_LUA.encode("utf-8")).decode("utf-8")
        try:
            with open(cjson, "wt") as fp:
                fp.write(cjson_lua)
        except PermissionError as e:
            MideaLogger.error(f"Failed to create cjson.lua at {cjson}: {e}")
            # 如果无法创建文件，尝试使用临时目�?
            import tempfile
            temp_dir = tempfile.gettempdir()
            cjson = os.path.join(temp_dir, "cjson.lua")
            with open(cjson, "wt") as fp:
                fp.write(cjson_lua)
            MideaLogger.warning(f"Using temporary file for cjson.lua: {cjson}")

    if not os.path.exists(bit):
        from .const import BIT_LUA
        bit_lua = base64.b64decode(BIT_LUA.encode("utf-8")).decode("utf-8")
        try:
            with open(bit, "wt") as fp:
                fp.write(bit_lua)
        except PermissionError as e:
            MideaLogger.error(f"Failed to create bit.lua at {bit}: {e}")
            # 如果无法创建文件，尝试使用临时目�?
            import tempfile
            temp_dir = tempfile.gettempdir()
            bit = os.path.join(temp_dir, "bit.lua")
            with open(bit, "wt") as fp:
                fp.write(bit_lua)
            MideaLogger.warning(f"Using temporary file for bit.lua: {bit}")

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_type = config_entry.data.get(CONF_TYPE)
    MideaLogger.debug(f"async_setup_entry type={device_type} data={config_entry.data}")
    if device_type == CONF_ACCOUNT:
        account = config_entry.data.get(CONF_ACCOUNT)
        password = config_entry.data.get(CONF_PASSWORD_KEY)
        server = config_entry.data.get(CONF_SERVER_KEY)
        cloud_name = CONF_SERVERS.get(server)
        cloud = get_midea_cloud(
            cloud_name=cloud_name,
            session=async_get_clientsession(hass),
            account=account,
            password=password,
        )
        if not cloud or not await cloud.login():
            MideaLogger.error("Midea cloud login failed")
            return False

        # 拉取家庭与设备列�?
        try:
            homes = await cloud.list_home()
            if homes and len(homes) > 0:
                hass.data.setdefault(DOMAIN, {})
                hass.data[DOMAIN].setdefault("accounts", {})
                bucket = {"device_list": {}, "coordinator_map": {}}
                
                # 获取用户选择的家庭ID列表
                selected_homes = config_entry.data.get(CONF_SELECTED_HOMES, [])
                MideaLogger.debug(f"Selected homes from config: {selected_homes}")
                MideaLogger.debug(f"Available homes keys: {list(homes.keys())}")
                if not selected_homes:
                    # 如果没有选择，默认使用所有家�?
                    home_ids = list(homes.keys())
                else:
                    # 只处理用户选择的家庭，确保类型匹配
                    home_ids = []
                    for selected_home in selected_homes:
                        # 尝试匹配字符串和数字类型的home_id
                        if selected_home in homes:
                            home_ids.append(selected_home)
                        elif str(selected_home) in homes:
                            home_ids.append(str(selected_home))
                        elif int(selected_home) in homes:
                            home_ids.append(int(selected_home))
                MideaLogger.debug(f"Final home_ids to process: {home_ids}")

                for home_id in home_ids:
                    appliances = await cloud.list_appliances(home_id)
                    if appliances is None:
                        continue

                    # 为每台设备构建占位设备与协调器（不连接本地）
                    for appliance_code, info in appliances.items():
                        MideaLogger.debug(f"info={info} ")

                        os.makedirs(hass.config.path(STORAGE_PATH), exist_ok=True)
                        path = hass.config.path(STORAGE_PATH)
                        file = await cloud.download_lua(
                            path=path,
                            device_type=info.get(CONF_TYPE),
                            sn=info.get(CONF_SN),
                            model_number=info.get(CONF_MODEL_NUMBER),
                            manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                        )
                        try:
                            os.makedirs(hass.config.path(STORAGE_PLUGIN_PATH), exist_ok=True)
                            plugin_path = hass.config.path(STORAGE_PLUGIN_PATH)
                            await cloud.download_plugin(
                                path=plugin_path,
                                appliance_code=appliance_code,
                                smart_product_id=info.get(CONF_SMART_PRODUCT_ID),
                                device_type=info.get(CONF_TYPE),
                                sn=info.get(CONF_SN),
                                sn8=info.get(CONF_SN8),
                                model_number=info.get(CONF_MODEL_NUMBER),
                                manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                            )
                        except Exception as e:
                            traceback.print_exc()

                        try:
                            device = MiedaDevice(
                                name=info.get(CONF_NAME),
                                device_id=appliance_code,
                                device_type=info.get(CONF_TYPE),
                                ip_address=None,
                                port=None,
                                token=None,
                                key=None,
                                connected=info.get("online"),
                                protocol=info.get(CONF_PROTOCOL) or 2,
                                model=info.get(CONF_MODEL),
                                subtype=info.get(CONF_MODEL_NUMBER),
                                manufacturer_code=info.get(CONF_MANUFACTURER_CODE),
                                sn=info.get(CONF_SN),
                                sn8=info.get(CONF_SN8),
                                lua_file=file,
                                cloud=cloud,
                            )
                            # 加载并应用设备映射（queries/centralized/calculate），并预�?attributes �?
                            try:
                                mapping = await load_device_config(
                                    hass,
                                    info.get(CONF_TYPE) or info.get("type"),
                                    info.get(CONF_SN8) or info.get("sn8"),
                                ) or {}
                            except Exception:
                                mapping = {}

                            try:
                                device.set_queries(mapping.get("queries", [{}]))
                            except Exception:
                                pass
                            try:
                                device.set_centralized(mapping.get("centralized", []))
                            except Exception:
                                pass
                            try:
                                device.set_calculate(mapping.get("calculate", {}))
                            except Exception:
                                pass

                            # 预置 attributes：包�?centralized 里声明的所有键、entities 中使用到的所有属性键
                            try:
                                preset_keys = set(mapping.get("centralized", []))
                                entities_cfg = (mapping.get("entities") or {})
                                # 收集实体配置中直接引用的属性键
                                for platform_cfg in entities_cfg.values():
                                    if not isinstance(platform_cfg, dict):
                                        continue
                                    for _, ecfg in platform_cfg.items():
                                        if not isinstance(ecfg, dict):
                                            continue
                                        # 常见直接属性字�?
                                        for k in [
                                            "power",
                                            "aux_heat",
                                            "current_temperature",
                                            "target_temperature",
                                            "oscillate",
                                            "min_temp",
                                            "max_temp",
                                        ]:
                                            v = ecfg.get(k)
                                            if isinstance(v, str):
                                                preset_keys.add(v)
                                            elif isinstance(v, list):
                                                for vv in v:
                                                    if isinstance(vv, str):
                                                        preset_keys.add(vv)
                                        # 模式映射里的条件字段
                                        for map_key in [
                                            "hvac_modes",
                                            "preset_modes",
                                            "swing_modes",
                                            "fan_modes",
                                            "operation_list",
                                            "options",
                                        ]:
                                            maps = ecfg.get(map_key) or {}
                                            if isinstance(maps, dict):
                                                for _, cond in maps.items():
                                                    if isinstance(cond, dict):
                                                        for attr_name in cond.keys():
                                                            preset_keys.add(attr_name)
                                # 传感�?开关等实体 key 本身也加入（�?key 即属性名�?
                                for platform_name, platform_cfg in entities_cfg.items():
                                    if not isinstance(platform_cfg, dict):
                                        continue
                                    platform_str = str(platform_name)
                                    if platform_str in [
                                        str(Platform.SENSOR),
                                        str(Platform.BINARY_SENSOR),
                                        str(Platform.SWITCH),
                                        str(Platform.FAN),
                                        str(Platform.SELECT),
                                    ]:
                                        for entity_key in platform_cfg.keys():
                                            preset_keys.add(entity_key)
                                # 写入默认空�?
                                for k in preset_keys:
                                    if k not in device.attributes:
                                        device.attributes[k] = None
                            except Exception:
                                pass

                            coordinator = MideaDataUpdateCoordinator(hass, config_entry, device, cloud=cloud)
                            # 后台刷新，避免初始化阻塞
                            hass.async_create_task(coordinator.async_config_entry_first_refresh())
                            bucket["device_list"][appliance_code] = info
                            bucket["coordinator_map"][appliance_code] = coordinator
                        except Exception as e:
                            MideaLogger.error(f"Init device failed: {appliance_code}, error: {e}")
                    # break
                hass.data[DOMAIN]["accounts"][config_entry.entry_id] = bucket

        except Exception as e:
            MideaLogger.error(f"Fetch appliances failed: {e}")
        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
        return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        # 卸载平台并清理账号桶
        unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)
        if unload_ok:
            try:
                hass.data.get(DOMAIN, {}).get("accounts", {}).pop(config_entry.entry_id, None)
            except Exception:
                pass
        return unload_ok
    if device_id is not None:
        device: MiedaDevice = hass.data[DOMAIN][DEVICES][device_id][CONF_DEVICE]
        if device is not None:
            if get_sn8_used(hass, device.sn8) == 1:
                remove_device_config(hass, device.sn8)
            # device.close()
        hass.data[DOMAIN][DEVICES].pop(device_id)
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
