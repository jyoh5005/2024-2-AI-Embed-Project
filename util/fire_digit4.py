import RPi.GPIO as GPIO
import time

# 숫자 표시 함수
def display_digit4(display_number, SEGMENTS, DIGITS, NUMBERS):
    digits = list(str(display_number).zfill(4))  # 4자리로 맞춤
    for i, digit in enumerate(digits):
        GPIO.output(DIGITS[i], GPIO.HIGH)  # 현재 자리 선택 (공통 양극)
        for j, segment in enumerate(SEGMENTS):
            GPIO.output(segment, not NUMBERS[int(digit)][j])  # 세그먼트 출력 반전
        time.sleep(0.005)  # 멀티플렉싱 딜레이
        GPIO.output(DIGITS[i], GPIO.LOW)  # 현재 자리 비활성화

# NONE 표시 함수
def display_none(SEGMENTS, DIGITS, NONE_INFO):
    for i in range(len(DIGITS)):
        GPIO.output(DIGITS[i], GPIO.HIGH)  # 현재 자리 선택 (공통 양극)
        for j, segment in enumerate(SEGMENTS):
            GPIO.output(segment, not NONE_INFO[j])  # 세그먼트 출력 반전
        time.sleep(0.005)  # 멀티플렉싱 딜레이
        GPIO.output(DIGITS[i], GPIO.LOW)  # 현재 자리 비활성화


# 숫자 테스트 함수
def test_digit4(SEGMENTS, DIGITS, NUMBERS, NONE_INFO):
    try:
        for num in [8888, 1234, 5678, 9000]:
            print(f"4digit = {num}")
            display_digit4(num, SEGMENTS, DIGITS, NUMBERS)
            time.sleep(1.0)

        print("None   = ----")
        display_none(SEGMENTS, DIGITS, NONE_INFO)
        time.sleep(1.0)
    except:
        return False

    return True