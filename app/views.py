from django.shortcuts import render
from django.http import JsonResponse
from .models import Video


from skimage.measure import structural_similarity as ssim
import matplotlib.pyplot as plt
import cv2
import math
import numpy as np
import pytesseract
from PIL import Image
import glob
src_path = '/home/arjun/Desktop/majorProjectDjango/ContentBasedVideoExtraction/app/frames/'

dictOfWords = {}

def addToDict(string):
    words = string.split()
    # print("Words List:", words)

    for word in words:
        if word in dictOfWords:
            dictOfWords[word] += 1
        else:
            dictOfWords[word] = 1


def get_string(img_path):
    img = cv2.imread(img_path)
    # print("image = ", img)
    # Convert to gray
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    cv2.imwrite(src_path + "removed_noise.png", img)

    # Apply threshold to get image with only black and white
    img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite(src_path + "thresh.png", img)
    result = pytesseract.image_to_string(Image.open(src_path + "thresh.png"))

    addToDict(result)


def VidProc(videoPath):

    vidcap = cv2.VideoCapture(videoPath)
    # frameRate = vidcap.get(5) #frame rate
    # print ("frameRate", frameRate)

    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    # Print frames per second
    if int(major_ver) < 3:
        fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        print ("Frames per second: {0}".format(fps))
    else:
        fps = vidcap.get(cv2.CAP_PROP_FPS)
        print ("Frames per second : {0}".format(fps))

    length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('Total number of frames:', length)
    success, image = vidcap.read()
    count = 0
    while success:
        # if(count == 300):
        #     break
        success, image = vidcap.read()
        frameId = vidcap.get(1)  # current frame number

        if (frameId % math.floor(3 * fps) == 0):

            # Display the resulting frame
            # cv2.imshow('frame',image)

            # Write frame in frames folder
            cv2.imwrite(src_path+ "frame%d.jpg" % count, image)     # save frame as JPEG file
            if(count>0):
                img1 = cv2.imread(src_path + "frame" + str(count - 1) + ".jpg", 0)
                img2 = cv2.imread(src_path + "frame" + str(count) + ".jpg", 0)
                SSIM = ssim(img1, img2)
                print("ssim: ",count, " ", SSIM )
                if(SSIM > .90 ):
                    print("inside here")
                    continue
            # Convert Frame Into Text
            # print ("\n\nImage Into String :", get_string("/home/arjun/Desktop/majorProject/frames/frame{0}.jpg".format(count)))
            get_string(src_path + "frame{0}.jpg".format(count))

            if cv2.waitKey(10) == 27:  # exit if Escape is hit
                break
            count += 1

    vidcap.release()
    cv2.destroyAllWindows()


def index(request):
    return render(request, "index.html", {
    })

def searchView(request):
    toSearch = request.GET.get("toSearch")
    toSearch = toSearch.lower()
    print ("Searched Item:", toSearch)
    videos = Video.objects.all()
    targetVideos = []
    for video in videos:
        print("\nVideo Title ->", video.title)
        f=0
        count=0
        for key, value in (video.data).items():
            key = key.lower()
            if toSearch in key:
                print("\tKey:", key, "\tCount: ", value)
                count += value
                f=1
        if f==1:
            targetVideos.append({"video": video, "count": count})
        print("\n")
    # Sort videos according to the count of the searched item
    targetVideos.sort(key=lambda x: x["count"], reverse=True)
    
    return render(request, "list.html", {
        "toSearch": toSearch,
        "videos": targetVideos,
    })


def videoProc(request):
    print("here in videoProc")
    videos = Video.objects.all()
    videosProcessed = 0
    for video in videos:
        if(video.data != None):
            continue
        print("Video Title", video.title)
        VidProc("/home/arjun/Desktop/majorProjectDjango/ContentBasedVideoExtraction/media-files/" + str(video.videoFile))
        # print("/home/arjun/Desktop/majorProjectDjango/ContentBasedVideoExtraction/media-files/" + str(video.videoFile))
        print("\n\ndictOfWords:\n")
        for k, v in dictOfWords.items():
            print (k, " => ", v)
        video.data = dictOfWords
        video.save()
        dictOfWords.clear()
        videosProcessed += 1
    return JsonResponse({"videosProcessed": videosProcessed})
