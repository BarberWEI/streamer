import cv2
import time


class PlayVid:
    def __init__(self):
        self.speed = 0  # Initialize the speed variable properly

    def playVideo(self, video):
        cap = cv2.VideoCapture(video)

        # Check if the video file was successfully opened
        if not cap.isOpened():
            print("Error: Could not open video.")
            return

        cv2.namedWindow("Video Player", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Player", 1920, 1080)

        start_time = time.time()  # Record the start time

        while cap.isOpened():
            success, frame = cap.read()
            if success:
                cv2.imshow('Video Player', frame)
            else:
                break

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            if elapsed_time > 30:  # Check if 150 seconds have passed
                break

            quitButton = cv2.waitKey(25) & 0xFF == ord('q')
            closeButton = cv2.getWindowProperty('Video Player', cv2.WND_PROP_VISIBLE) < 1

            if quitButton or closeButton:
                break

        cap.release()
        cv2.destroyAllWindows()


