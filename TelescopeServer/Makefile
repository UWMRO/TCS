all:
	g++ -std=c++11 -c -o TelescopeServer.o TelescopeServer.cpp #-std=c++11 is for thread
	g++ -c -o bct30.o bct30.cpp
	g++ -o TelescopeServer TelescopeServer.o bct30.o -I/home/mro/mcapi/mcapi-4.4.1/src/drivers/linux/mcapi.o -lmcapi
clean:
	rm *.o
	rm *.so
	rm *.py
	rm bct30_wrap.cpp
