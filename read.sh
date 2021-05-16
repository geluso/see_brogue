convert $1 -type Grayscale input.tif                                                             
tesseract -l eng input.tif $1
cat $1.txt
