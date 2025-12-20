from ..core.device_map import MideaDeviceProperties, MideaDeviceProperty, MideaDeviceEntityConfig

# 重新定义0x09类型设备的属性映射（智能门锁）
DEVICE_MAPPING_0x09 = MideaDeviceProperties(
    name="Smart Door Lock",
    entity_configs=[
        # 开锁方式
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="unlock_mode",
                desc="Unlock Mode",
                readable=True,
                writable=True,
                visible=True,
                value_range=[0, 1, 2, 3, 4, 5]
            ),
            platform="select",
            entity_key="unlock_mode"
        ),
        
        # 当前状态
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="current_status",
                desc="Current Status",
                readable=True,
                writable=False,
                visible=True,
                value_range=None
            ),
            platform="sensor",
            entity_key="current_status"
        ),
        
        # 目标开锁方式
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="target_unlock_method",
                desc="Target Unlock Method",
                readable=True,
                writable=True,
                visible=True,
                value_range=[1, 10]
            ),
            platform="number",
            entity_key="target_unlock_method"
        ),
        
        # 门锁状态
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="lock_state",
                desc="Lock State",
                readable=True,
                writable=False,
                visible=True,
                value_range=None
            ),
            platform="binary_sensor",
            entity_key="lock_state"
        ),
        
        # 开锁记录
        
        # 电池状态
        
        # 设备在线状态
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="device_online",
                desc="Device Online",
                readable=True,
                writable=False,
                visible=True,
                value_range=None
            ),
            platform="binary_sensor",
            entity_key="device_online"
        ),
        
        # 错误代码
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="error_code",
                desc="Error Code",
                readable=True,
                writable=False,
                visible=True,
                value_range=None
            ),
            platform="sensor",
            entity_key="error_code"
        ),
        
        # 自动锁定功能开关
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="auto_lock",
                desc="Auto Lock",
                readable=True,
                writable=True,
                visible=True,
                value_range=[0, 1]
            ),
            platform="switch",
            entity_key="auto_lock"
        ),
        
        # 防撬报警状态
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="tamper_alarm",
                desc="Tamper Alarm",
                readable=True,
                writable=False,
                visible=True,
                value_range=None
            ),
            platform="binary_sensor",
            entity_key="tamper_alarm"
        ),
        
        # 临时密码设定
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="temp_password_setting",
                desc="Temporary Password Setting",
                readable=True,
                writable=True,
                visible=True,
                value_range=[1000, 999999]
            ),
            platform="number",
            entity_key="temp_password_setting"
        ),
        
        # 指纹识别灵敏度
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="fingerprint_sensitivity",
                desc="Fingerprint Sensitivity",
                readable=True,
                writable=True,
                visible=True,
                value_range=[1, 10]
            ),
            platform="number",
            entity_key="fingerprint_sensitivity"
        ),
        
        # 剩余电量百分比
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="battery_level",
                desc="Battery Level",
                readable=True,
                writable=False,
                visible=True,
                value_range=[0, 100]
            ),
            platform="sensor",
            entity_key="battery_level",
            device_class="battery",
            unit_of_measurement="%"
        ),
        
        # 儿童锁状态
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="child_lock",
                desc="Child Lock",
                readable=True,
                writable=True,
                visible=True,
                value_range=[0, 1]
            ),
            platform="switch",
            entity_key="child_lock"
        ),
        
        # 多重验证设置
        MideaDeviceEntityConfig(
            property=MideaDeviceProperty(
                name="multi_auth",
                desc="Multi-factor Authentication",
                readable=True,
                writable=True,
                visible=True,
                value_range=[0, 1]
            ),
            platform="switch",
            entity_key="multi_auth"
        )
    ]
)
