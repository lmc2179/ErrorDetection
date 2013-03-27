install:
	virtualenv -p /usr/bin/python2.7 --system-site-packages env 
	ln -s env/bin/activate activate
    . env/bin/activate && pip install -r requirements.txt
clean:
		rm -rf env
.PHONY: install clean

