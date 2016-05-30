all:
	g++ -c -o parser.o parser.cpp 
	g++ -c -o bct30.o bct30.cpp
	g++ -o test parser.o bct30.o -I/home/mro/mcapi/mcapi-4.4.1/src/drivers/linux/mcapi.o -lmcapi
clean:
	rm *.o
	rm *.so
	rm *.py
	rm bct30_wrap.cpp
