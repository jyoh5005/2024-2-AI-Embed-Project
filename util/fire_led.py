import RPi.GPIO as GPIO
import time

# LED 깜빡임 테스트 함수
def test_all_LED(LED_PINS):
    try:
        for _ in range(3):  # 3번 깜빡임
            for pin in LED_PINS.values():
                GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.8)
            for pin in LED_PINS.values():
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.2)
    except:
        return False
        
    return True
    