import cv2

# 사람 확인 함수
def check_human(picam2, model, show_img=False):
    try:
        # 프레임 캡처
        frame = picam2.capture_array()

        # OpenCV에서 사용하는 BGR 포맷을 RGB로 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # YOLO 모델에 입력 (RGB 포맷을 사용)
        results = model.predict(rgb_frame, conf=0.5)  # confidence threshold를 0.5로 설정

        # 사람 클래스 (COCO 데이터셋 기준으로 0번이 사람 클래스)
        person_count = 0

        # 프레임에 바운딩 박스와 텍스트 그리기
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # 바운딩 박스 좌표
            cls = int(box.cls[0])  # 클래스 ID

            if cls == 0:  # 클래스가 "사람"인 경우
                person_count += 1
                if show_img: # 확인용도
                    # 바운딩 박스 그리기
                    cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 초록색 박스
                    # 라벨 추가
                    cv2.putText(rgb_frame, f"Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 감지된 인원 수 리턴
        if show_img:
            return person_count, rgb_frame
        else:
            return person_count, None

    except Exception as e:
        print(f"오류 발생: {e}")
        return None, None

