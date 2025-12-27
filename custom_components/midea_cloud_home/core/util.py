def bytes_to_dec_string(data: bytearray) -> bytearray:
    """
    �?bytearray 转换为逗号分隔的十进制字符串格式，然后返回 bytearray
    对应 Java �?bytesToDecString 方法
    """
    # 处理有符号字节（模拟 Java �?byte 类型 -128 �?127�?
    result = []
    for b in data:
        # 将无符号字节转换为有符号字节
        signed_byte = b if b < 128 else b - 256
        result.append(str(signed_byte))

    decimal_string = ','.join(result)
    return bytearray(decimal_string, 'utf-8')


def dec_string_to_bytes(dec_string: str) -> bytearray:
    """
    将逗号分隔的十进制字符串转换为字节数组
    对应 Java �?decStringToBytes 方法
    
    Args:
        dec_string: 逗号分隔的十进制字符串，�?"1,2,-3,127"
    
    Returns:
        bytearray: 转换后的字节数组
    """
    if dec_string is None:
        return bytearray()
    
    # 按逗号分割字符�?
    split_values = dec_string.split(',')
    result = bytearray(len(split_values))
    
    for i, value_str in enumerate(split_values):
        try:
            # 解析十进制字符串为整数，然后转换为字�?
            int_value = int(value_str.strip())
            # 确保值在字节范围�?(-128 �?127)
            if int_value < -128:
                int_value = -128
            elif int_value > 127:
                int_value = 127
            result[i] = int_value & 0xFF  # 转换为无符号字节
        except (ValueError, IndexError) as e:
            # 如果解析失败，记录错误并跳过该�?
            print(f"dec_string_to_bytes() error: {e}")
            result[i] = 0  # 默认�?
    
    return result
