import os
import pygame

pygame.mixer.init()

BASE_DIR = os.path.dirname(__file__)

tracks = [
    os.path.join(BASE_DIR, "music", "track1.mp3"),
    os.path.join(BASE_DIR, "music", "track2.mp3"),
]

index = 0
is_playing = False


def play():
    global is_playing

    pygame.mixer.music.load(tracks[index])
    pygame.mixer.music.play()
    is_playing = True


def stop():
    global is_playing

    pygame.mixer.music.stop()
    is_playing = False


def next_track():
    global index, is_playing

    index = (index + 1) % len(tracks)
    pygame.mixer.music.load(tracks[index])
    pygame.mixer.music.play()
    is_playing = True


def previous_track():
    global index, is_playing

    index = (index - 1) % len(tracks)
    pygame.mixer.music.load(tracks[index])
    pygame.mixer.music.play()
    is_playing = True


def current_track():
    return os.path.basename(tracks[index])