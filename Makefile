# Makefile
all: clean zip
zip:
	zip -r application.zip * .eb*
clean:
	rm -vf application.zip *.*~ *~ *.pyc
	rm -vf templates/*.*~ 


