import RPi.GPIO as GPIO
import spidev
import time
import numpy as np
import threading
import argparse
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

from util import fire_camera
from util import fire_digit4
from util import fire_gas
from util import fire_led
from util import fire_speaker

print("import 완료")

# GPIO 설정
GPIO.setmode(GPIO.BCM)

# GPIO 핀 정의
SEGMENTS = [17, 27, 22, 5, 6, 13, 19, 26]  # A, B, C, D, E, F, G, DP
DIGITS = [23, 24, 25, 16]  # D1, D2, D3, D4

# 숫자 세그먼트 매핑 (공통 양극 기준)
NUMBERS = [
    [1, 1, 1, 1, 1, 1, 0, 0],  # 0
    [0, 1, 1, 0, 0, 0, 0, 0],  # 1
    [1, 1, 0, 1, 1, 0, 1, 0],  # 2
    [1, 1, 1, 1, 0, 0, 1, 0],  # 3
    [0, 1, 1, 0, 0, 1, 1, 0],  # 4
    [1, 0, 1, 1, 0, 1, 1, 0],  # 5
    [1, 0, 1, 1, 1, 1, 1, 0],  # 6
    [1, 1, 1, 0, 0, 0, 0, 0],  # 7
    [1, 1, 1, 1, 1, 1, 1, 0],  # 8
    [1, 1, 1, 1, 0, 1, 1, 0],  # 9
]

# NONE 정보 세그먼트 매핑 (공통 양극 기준)
NONE_INFO = [0, 0, 0, 0, 0, 0, 1, 0]  # -

# LED 핀 정의
LED_PINS = {
    'Red': 14,
    'Green': 15
}

# 가스센서 통신 설정
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI0, CS0 사용
spi.max_speed_hz = 1350000

# 가스센서 채널 설정
channel = 0

# 4-Digit 7-Segment 및 LED 핀 설정
for pin in SEGMENTS:
    GPIO.setup(pin, GPIO.OUT)
for pin in DIGITS:
    GPIO.setup(pin, GPIO.OUT)
for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)  # LED 핀 출력 모드

# 버튼 핀 설정 (풀다운 저항)
BUTTON_RED_PIN = 2   # Red 버튼
GPIO.setup(BUTTON_RED_PIN, GPIO.IN)

# 스피커 핀 정의
SPEAKER_PIN = 12
GPIO.setup(SPEAKER_PIN, GPIO.OUT)  # 스피커 핀 출력 모드

print("GPIO SET 완료")

# Picamera2 인스턴스 생성
picam2 = Picamera2()

# 카메라 설정 및 시작
preview_config = picam2.create_preview_configuration(main={"size": (640, 640)})
picam2.configure(preview_config)
picam2.start()

print("Camera SET 완료")

# YOLO 모델 로드
model = YOLO("./yolo11n.pt")  # YOLO 모델 파일 경로
print("AI Load 완료")

# 탐지 결과를 공유할 변수
detected_people = None
stop_threads = False  # 쓰레드 종료 플래그
print("쓰레드 설정 완료")

"""
사용 함수들
fire_camera.check_human(picam2, model, show_img=False): # 사람 확인 함수

fire_digit4.display_digit4(display_number, SEGMENTS, DIGITS, NUMBERS): # 숫자 표시 함수
fire_digit4.display_none(SEGMENTS, DIGITS, NONE_INFO): # NONE 표시 함수
fire_digit4.test_digit4(SEGMENTS, DIGITS, NUMBERS): # 숫자 테스트 함수

fire_gas.read_adc(spi, channel=0): # 가스 체크 함수
fire_gas.check_init_gas(spi, channel=0): # 가스 센서 초기값 설정 함수
fire_gas.test_gas(spi, channel=0): # 가스 센서 테스트 함수

fire_led.test_all_LED(LED_PINS): # LED 깜빡임 테스트 함수

fire_speaker.test_speaker(SPEAKER_PIN): # 스피커 테스트 함수
fire_speaker.warning_speaker(pwm): # 스피커 출력 함수
"""

def test_sensor():
    """
    센서 테스트 함수
    """
    print("모든 센서를 테스트 하고 있습니다...")

    # 카메라 테스트
    count, _ = fire_camera.check_human(picam2, model)
    if count is None:
        print("객체 탐지 이상!")
        return False
    print("객체 탐지 정상!")
    time.sleep(0.5)

    # 7-Segment 디지털 출력 테스트
    check = fire_digit4.test_digit4(SEGMENTS, DIGITS, NUMBERS, NONE_INFO)
    if not check:  # check가 False일 경우
        print("숫자 출력 이상!")
        return False
    print("숫자 출력 정상!")
    time.sleep(0.5)

    # 가스 센서 테스트
    check = fire_gas.test_gas(spi, channel)
    if not check:  # check가 False일 경우
        print("가스 센서 이상!")
        return False
    print("가스 센서 정상!")
    time.sleep(0.5)

    # LED 테스트
    check = fire_led.test_all_LED(LED_PINS)
    if not check:  # check가 False일 경우
        print("LED 출력 이상!")
        return False
    print("LED 출력 정상!")
    time.sleep(0.5)

    # 스피커 테스트
    check = fire_speaker.test_speaker(SPEAKER_PIN)
    if not check:  # check가 False일 경우
        print("스피커 출력 이상!")
        return False
    print("스피커 출력 정상!")
    time.sleep(0.5)

    print("모든 센서가 정상입니다")
    return True

def monitor_gas():
    """
    가스 센서를 모니터링하고, 특정 조건에서 LED와 스피커 동작 수행
    """
    print("잠시만 기다리십시오...")
    # 가스 센서 초기화
    init_gas_value = fire_gas.check_init_gas(spi, channel)

    # Green LED 켬
    GPIO.output(LED_PINS['Green'], GPIO.HIGH)
    print(f"초기 가스 값: {init_gas_value}")
    print("가스 모니터링을 시작합니다")

    monitor_count = 999
    while True:
        # 현재 가스 값 확인
        current_gas_value = fire_gas.read_adc(spi, channel)

        # 가스 값이 초기 값보다 300 이상 높거나 버튼이 눌리면 화재 발생 처리
        if current_gas_value > init_gas_value + 500:
            print(f"화재 발생! 현재 가스 값: {current_gas_value}")
            return True

        monitor_count += 1
        if monitor_count >= 1000:
            monitor_count = 0
            print("가스 측정중...")

        time.sleep(0.01)  # 10ms 간격으로 체크
    
def detect_humans(show_img=False):
    """
    사람 탐지 쓰레드 함수
    Args:
        show_img (bool): True일 경우 탐지된 이미지를 화면에 표시
    """
    global detected_people, stop_threads
    while not stop_threads:
        count, frame = fire_camera.check_human(picam2, model, show_img)
        detected_people = count  # 탐지 결과 업데이트
        print(f"감지된 사람 수: {count}")
        if show_img:
            import cv2
            cv2.imshow("Detected Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q'를 누르면 종료
                stop_threads = True
                break
    cv2.destroyAllWindows()

def sound_warning():
    """
    스피커 경고 쓰레드 함수
    """
    global stop_threads
    pwm = GPIO.PWM(SPEAKER_PIN, 1)  # 초기 주파수 1Hz 설정
    pwm.start(50)  # 듀티 사이클 50%

    try:
        while not stop_threads:
            fire_speaker.warning_speaker(pwm)  # 경고음 함수 호출
            time.sleep(0.001)  # 경고음 사이 간격을 두기 위해 대기
    except Exception as e:
        print(f"경고 쓰레드에서 오류 발생: {e}")
    finally:
        pwm.stop()  # PWM 정지
        pwm = None  # PWM 객체 해제
        print("스피커 정리 완료")

def display_people():
    """
    4-Digit 디스플레이 쓰레드 함수
    """
    global detected_people, stop_threads
    while not stop_threads:
        if detected_people is not None:
            fire_digit4.display_digit4(detected_people, SEGMENTS, DIGITS, NUMBERS)
        else:
            # 기본적으로 NONE 표시
            fire_digit4.display_none(SEGMENTS, DIGITS, NONE_INFO)
        time.sleep(0.1)  # 디스플레이 갱신 주기


# 메인 함수
def main():
    parser = argparse.ArgumentParser(description="Fire detection script")
    parser.add_argument(
        "--show-img",
        action="store_true",
        help="Detect frame and show it on the screen.",
    )
    args = parser.parse_args()

    threads = []
    if test_sensor():
        print("시작하기...")
        threads.append(threading.Thread(target=display_people))
        threads.append(threading.Thread(target=sound_warning))
        threads.append(threading.Thread(target=detect_humans, args=(args.show_img,)))
    else:
        # 종료하기
        picam2.stop()
        cv2.destroyAllWindows()
        GPIO.cleanup()
        return


    try:
        threads[0].start()
        if monitor_gas():
            # 초록 LED 끔
            GPIO.output(LED_PINS['Green'], GPIO.LOW)
            GPIO.output(LED_PINS['Red'], GPIO.HIGH)

            # 탐지, 스피커 쓰레드 실행
            for thread in threads[1:]:
                thread.start()

            for thread in threads:
                thread.join()  # 모든 쓰레드가 종료될 때까지 대기

    except KeyboardInterrupt:
        print("\n프로그램 종료 중...")
    finally:
        global stop_threads
        stop_threads = True
        for thread in threads:
            if thread.is_alive():
                thread.join()  # 모든 쓰레드가 종료될 때까지 대기

        picam2.stop()
        if args.show_img:
            cv2.destroyAllWindows()
        GPIO.cleanup()
        print("정리 완료. 프로그램 종료.")


if __name__ == "__main__":
    main()


