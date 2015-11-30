all:
	swig -c++ -python -o bct30_wrap.cpp bct30.i
	g++ -c bct30.cpp bct30_wrap.cpp fslide.cpp indicom.c mcapi_standin.c -I/usr/include/python2.7 -fPIC
	g++ -shared bct30.o bct30_wrap.o fslide.o indicom.o mcapi_standin.o -o _bct30.so

clean:
	rm *.o
	rm *.so
	rm *.py
	rm bct30_wrap.cpp
