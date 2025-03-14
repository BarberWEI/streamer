import pygame

# 初始化pygame
pygame.init()

# 加载音乐文件
pygame.mixer.music.load("../outputs/response.mp3")

# 播放音乐
pygame.mixer.music.play()

# 保持程序运行直到音乐播放结束
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

# from playsound import playsound
#
# playsound(r'C:\Users\xiaoen\Downloads\audio (4).mp3')