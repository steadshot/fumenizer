import cv2
import numpy as np
import sys
import pyperclip

if len(sys.argv) == 1:
	print "Please enter an image file as an argument."
	exit()
#image needs to be the exact playfield without the border
#todo: recognize playfield automagically by looking for squares
field = cv2.imread(sys.argv[1])
height, width = field.shape[:2]
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
		ret, thresh = cv2.threshold(thresh, 20, 255, cv2.THRESH_BINARY)
		#sometimes a little tinkering with the 2nd parameter (aka the threshold value) 
		#of threshold is required (e.g. going higher than 20)
		#todo: make threshold an argument
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

#silly js hax to quickly generate a fumen frame out of the result
js_commands = 'avascript:x=document.getElementById("clt");if(x.checked)x.click();'
js_commands += 'arr=['
for row in range(20):
	for col in range(10):
		if matrix[row][col]:
			js_commands += str(22 - row) + str(col) + ','
			#draw gray rectangles where blocks are
			cv2.rectangle(blank, (col * 10 + 2, 190 - row * 10), 
				(col * 10 + 5 + 2, 190 - row * 10 + 5), (105, 105, 105), cv2.FILLED)

js_commands += '];'
js_commands += 'arr.forEach(function(val){evbutton1();drawfield(val, 1);evbutton0()});'

#copy js hax into clipboard
#since you can't paste javascript commands into some browsers' URL bar
#you have to prepend the 'j' yourself
pyperclip.copy(js_commands)

#show result image
cv2.imshow('d', blank)
cv2.waitKey()
cv2.destroyAllWindows()
