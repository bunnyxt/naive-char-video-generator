import cv2
import imageio
import subprocess
import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def getCharArray(precision):
    char_array = []
    if precision == 16:
        char_array = ['M', 'W', 'N', 'Ö', 'Ü', 'Ä', '8', '9', 'k', 'å', 'J', 'l', '?', '-', ':', ' ']
    return char_array

def getCharMatrix(image, width, height, precision, char_array):
    images_matrix = image.load()
    char_matrix = [[0 for i in range(height)] for j in range(width)]
    for i in range(width):
        for j in range(height):
            pixel = images_matrix[i, j]
            level = int(pixel / precision)
            char_matrix[i][j] = char_array[level]
    return char_matrix

if __name__ == "__main__":
    print("Welcome to Naive Char Video Generator")

    # 01 load video
    file_name = input("Please enter video file name: ")
    video = cv2.VideoCapture(file_name)
    if not video.isOpened() :
        print("Error! Cannot open file {0} as a video!".format(file_name))
        exit(0)
    shutil.rmtree("workspace")
    os.mkdir("workspace")

    # 02 separate video and audio
    print("Now pick audio...")
    os.mkdir("workspace/audio")
    audio_file_name = "workspace/audio/{0}.wav".format(file_name.split('.')[0])
    subprocess.call("ffmpeg -i {0} -f wav {1}".format(file_name, audio_file_name), shell=True)
    print("Audio picked to {0}!".format(audio_file_name))

    # 03 pick frame images
    print("Now pick frame images...")
    fps = video.get(cv2.CAP_PROP_FPS)  # 获取视频的帧率
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)  # 获取视频的宽度
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 获取视频的高度
    os.mkdir("workspace/image")
    frame_count = 0
    while True:
        if frame_count == 99999:
            break
        frame_count += 1
        (flag, frame) = video.read()  # 读取图片
        frame_file_name = "workspace/image/{0}.jpg".format(frame_count)
        if flag == True:
            cv2.imwrite(frame_file_name, frame, [cv2.IMWRITE_JPEG_QUALITY])  # 保存图片
            print(frame_file_name)
        else:
            break
    frame_count -= 1
    print("{0} images picked from video {1} in workspace/image!".format(frame_count, file_name))

    # 04 make char text file
    print("Now make char text files...")
    os.mkdir("workspace/chartext")
    resize_ratio = 0.1
    precision = 16
    char_array = getCharArray(precision)
    if len(char_array) != precision:
        print("Error! Not support precision {0}!".format(precision))
        exit(0)
    r_width = int(width * resize_ratio)
    r_height = int(height * resize_ratio)
    for i in range(1, frame_count + 1):
        frame = Image.open("workspace/image/{0}.jpg".format(i))
        frame = frame.convert("L")
        frame = frame.resize((r_width, r_height), Image.ANTIALIAS)
        char_matrix = getCharMatrix(frame, r_width, r_height, precision, char_array)
        char_text_file_name = 'workspace/chartext/{0}.txt'.format(i)
        with open(char_text_file_name, 'w') as f:
            for h in range(0, r_height):
                for w in range(0, r_width):
                    f.write(char_matrix[w][h])
                f.write("\n")
        print(char_text_file_name)
        frame.close()
    print("{0} char text files made in workspace/chartext!".format(frame_count))


    # 05 make char images
    print("Now make char images...")
    os.mkdir("workspace/charimage")
    font_size = 12
    c_width = font_size
    c_height = font_size
    font = ImageFont.truetype('Arial.ttf', font_size)
    for i in range(1, frame_count + 1):
        image = Image.new('RGB', (r_width * c_width, r_height * c_height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        x = 0
        y = 0
        char_text_file_name = 'workspace/chartext/{0}.txt'.format(i)
        with open(char_text_file_name, 'r') as f:
            for line in f:
                x = 0
                for ch in line:
                    draw.text((x, y), ch, font=font, fill=(0, 0, 0))
                    x += c_width
                y += c_height
        char_image_file_name = "workspace/charimage/{0}.jpg".format(i)
        image.save(char_image_file_name, 'jpeg')
        print(char_image_file_name)
    print("{0} char images made in workspace/charimage!".format(frame_count))

    # 06 make char video
    print("Now make char video...")
    output_file_name = "{0}_output.{1}".format(file_name.split('.')[0],file_name.split('.')[1])
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    videoWriter = cv2.VideoWriter(output_file_name, fourcc, fps, (r_width * c_width, r_height * c_height))
    for i in range(1, frame_count + 1):
        frame = cv2.imread("workspace/charimage/{0}.jpg".format(i))
        videoWriter.write(frame)
    videoWriter.release()
    final_output_file_name = "{0}_output_final.{1}".format(file_name.split('.')[0],file_name.split('.')[1])
    subprocess.call('ffmpeg -i ' + output_file_name + ' -i ' + audio_file_name + ' -strict -2 -f mp4 ' + final_output_file_name, shell=True)
    print("Finish make char video {0}!".format(final_output_file_name))
