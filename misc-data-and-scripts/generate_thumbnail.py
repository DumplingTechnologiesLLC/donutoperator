import cv2
import urllib.request
import os


def run_example():
    """Extract frames from the video and creates thumbnails for one of each"""
    # Extract frames from video
    print("Extract frames from video")
    frames = video_to_frames("https://www.youtube.com/embed/u72a2guLNZc")
    print(frames)
    # Generate and save thumbs
    print("Generate and save thumbs")
    for i in range(len(frames)):
        thumb = image_to_thumbs(frames[i])
        os.makedirs('frames/%d' % i)
        for k, v in thumb.items():
            cv2.imwrite('frames/%d/%s.png' % (i, k), v)


def video_to_frames(url_link):
    """Extract frames from video"""
    rsp = urllib.request.urlopen(url_link)
    print(rsp)
    cap = cv2.VideoCapture(str(rsp.read()))
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print(video_length)
    frames = []
    if cap.isOpened() and video_length > 0:
        frame_ids = [0]
        if video_length >= 4:
            frame_ids = [0,
                         round(video_length * 0.25),
                         round(video_length * 0.5),
                         round(video_length * 0.75),
                         video_length - 1]
        count = 0
        success, image = cap.read()
        while success:
            if count in frame_ids:
                frames.append(image)
            success, image = cap.read()
            count += 1
    return frames


def image_to_thumbs(img):
    """Create thumbs from image"""
    height, width, channels = img.shape
    thumbs = {"original": img}
    sizes = [640, 320, 160]
    for size in sizes:
        if (width >= size):
            r = (size + 0.0) / width
            max_size = (size, int(height * r))
            thumbs[str(size)] = cv2.resize(img, max_size, interpolation=cv2.INTER_AREA)
    return thumbs


if __name__ == '__main__':
    run_example()
