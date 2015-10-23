import cv2
import numpy as np
import sys
import pyperclip
import os
import os.path
import ConfigParser
import fumen

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

if not os.path.isfile('fumenizer.ini'):
	threshold = 20
	showPreviewWindow = True
	tgm1 = False
	f = open("fumenizer.ini", "w")
	f.write("[settings]\n")
	f.write("#for TGM a threshold around 20 is recommended\n")
	f.write("threshold=20\n")
	f.write("show_preview_window=1\n")
	f.write("tgm1=0\n")
	f.close()

config = ConfigParser.SafeConfigParser()
config.read('fumenizer.ini')
threshold = config.getint('settings', 'threshold')
showPreviewWindow = config.getboolean('settings', 'show_preview_window')
tgm1 = config.getboolean('settings', 'tgm1')

if len(sys.argv) == 1:
	print "Please enter an image file as an argument."
	sys.exit()
#image needs to be the exact playfield without the border
#todo: recognize playfield automagically by looking for squares
field = cv2.imread(sys.argv[1])
hsv = cv2.cvtColor(field, cv2.COLOR_BGR2HSV)
height, width = field.shape[:2]
#for i in range(height):
#	for j in range(width):
#		hue = hsv[i][j][0]
#		saturation = hsv[i][j][1]
#		value = hsv[i][j][2]
#		hsv[i, j] = [hue, saturation, 100]
lower = np.array([0,150,85])
upper = np.array([180,255,255])
mask = cv2.inRange(hsv, lower, upper)
if(tgm1):
	field = cv2.bitwise_and(field, field, mask = mask)

#uncomment for preview for the tgm1 code
#cv2.imshow('f', field)
#cv2.waitKey()

block_height = height / 20.
block_width = width / 10.

end = False
# matrix is a nested list that represents the playfield
# holes are 0's, blocks are 1's
# todo: recognize color
matrix = []
for row in range(20):
	line = []
	for col in range(10):
		y1 = round(height - (row + 1) * block_height)
		y2 = round(height - row * block_height)
		x1 = round(col * block_width)
		x2 = round((col + 1) * block_width)
		part = field[y1:y2, x1:x2]

		thresh = cv2.cvtColor(part, cv2.COLOR_BGR2GRAY)
		ret, thresh = cv2.threshold(thresh, threshold, 255, cv2.THRESH_BINARY)
		#sometimes a little tinkering with the 2nd parameter (aka the threshold value) 
		#of threshold is required (e.g. going higher than 20)
		temp_height, temp_width = thresh.shape[:2]
		#blocks will now be predominantly white squares, so we're counting 
		#black and white pixels
		black = 0
		white = 0
		for i in range(temp_height):
			for j in range(temp_width):
				if thresh[i, j] == 0:
					black += 1
				else:
					white += 1
		#tgm1 mode is still kind of hacky and needs improvement
		if tgm1:
			if white > 60:
				line.append(1)
			else:
				line.append(0)
		else:
			if white > black:
				line.append(1)
			else:
				line.append(0)

		#uncomment this part to go through the coordinates one by one 
		#cv2.imshow('b', part)
		#cv2.imshow('c', thresh)
		#ch = 0xFF & cv2.waitKey()
		#if ch == 27:
		#	end = True
		#	break
	matrix.append(line)
	if end:
		break

#prepare result image
blank = np.zeros((200, 100, 3), np.uint8)
frame = fumen.Frame()
cell = 10

for row in range(20):
	for col in range(10):
		if matrix[row][col]:
			#draw gray rectangles where blocks are
			cv2.rectangle(blank, (col * 10 + 2, 190 - row * 10), 
				(col * 10 + 5 + 2, 190 - row * 10 + 5), (105, 105, 105), cv2.FILLED)
		if matrix[19 - row][col]:
			frame.field[cell] = 8
		else:
			frame.field[cell] = 0
		cell += 1

fumen_url = fumen.make([frame], 0)
pyperclip.copy(fumen_url)

if showPreviewWindow:
	#show result image
	cv2.imshow('d', blank)
	cv2.waitKey()
	cv2.destroyAllWindows()
