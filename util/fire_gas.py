import time

# 가스 체크 함수
def read_adc(spi, channel=0):
    if channel < 0 or channel > 7:
        raise ValueError("채널은 0에서 7 사이여야 합니다.")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# 가스 센서 초기값 설정 함수
def check_init_gas(spi, channel=0):
    init_gas_value = float('inf')
    for i in range(10):
        gas_value = read_adc(spi, channel)  # 초기 가스 값 읽기
        if init_gas_value > gas_value:
            init_gas_value = gas_value
        time.sleep(1)

    return init_gas_value   # 가장 작은 값 리턴

# 가스 센서 테스트 함수
def test_gas(spi, channel=0):
    try:
        read_adc(spi, channel)
    except:
        return False
        
    return True

