all:
	swig -python -c++ -o bct30_wrap.cpp bct30.i
	g++ -O2 -fPIC -c bct30.cpp bct30_wrap.cpp -I/usr/include/python2.7 -I/home/mro/TCC/bct
	g++ -fPIC -Wall -Wextra -shared bct30.o bct30_wrap.o -o _bct30.so -L.  -I/usr/include/python2.7/ -lpython2.7

clean:
	rm *.o
	rm *.so
	rm *.py
	rm bct30_wrap.cpp
