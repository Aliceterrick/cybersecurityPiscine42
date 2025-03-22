NAME = ft_otp

CC = c++

CCFLAGS = -std=c++11 -Wall -I/usr/include/openssl
LDFLAGS = -L/usr/lib/x86_64-linux-gnu -lcrypto -lssl

SRC = src/ft_otp.cpp

all:
	$(CC) $(CCFLAGS) $(SRC) $(LDFLAGS) -o $(NAME)

clean:
	rm -f $(NAME)