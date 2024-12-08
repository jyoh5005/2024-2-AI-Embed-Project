import RPi.GPIO as GPIO
import time

# 스피커 테스트 함수
def test_speaker(SPEAKER_PIN):
    try:
        pwm = GPIO.PWM(SPEAKER_PIN, 1) # 초기 주파수 1Hz
        pwm.start(50)  # 듀티 사이클 50%
        tones = [261.63, 329.63, 392.00, 523.25]  # 도, 미, 솔, 도 (C4, E4, G4, C5)
        for tone in tones:
            pwm.ChangeFrequency(tone)
            time.sleep(0.8)

        pwm.stop()
        pwm = None  # 정리 후 None으로 설정

    except:
        pwm.stop()
        pwm = None  # 정리 후 None으로 설정
        return False

    return True


# 스피커 출력 함수
def warning_speaker(pwm):
    try:
        pwm.ChangeFrequency(329.63)  # 주파수 329.63Hz (E4)
        time.sleep(0.3)
        pwm.ChangeFrequency(523.25)  # 주파수 523.25Hz (C5)
        time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n스피커 종료 중...")
    except Exception as e:
        print(f"소리 재생 중 오류 발생: {e}")

