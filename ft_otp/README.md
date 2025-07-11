This project implements a Time-based One-Time Password (TOTP) generator.
A TOTP uses a symmetric algorithm shared between two parties: the prover/client and the verifier/server. It is a more robust extension of HMAC-based One-Time Password (HOTP).

In HOTP, a secret S and a counter C are used:
HOTP = HMAC(S, C).
In TOTP, the counter is based on the number of time intervals (usually of 30 seconds) between a fixed point in time (usually the epoch) and the current time. 

TOTP is a more secure alternative to traditional passwords in some ways. If the shared secret remains secure, a TOTP can only be compromised for the duration of a single time interval. However, the security of the secret, which must be known to both parties, is critical.

_____

This program can be run three different ways:

python3 ft_otp.py -g <filename>: Saves the key contained in <filename> into an encrypted file named ft_otp.key.
⚠️ The key must be a hexadecimal string of at least 64 characters.

python3 ft_otp.py -k <ft_otp.key>: Generates a TOTP based on the key stored in ft_otp.key.

python3 ft_otp.py -q <ft_otp.key>: Generates both a TOTP and a QR code using the key from ft_otp.key, with the TOTP as the seed.

Remember to install the requirements specified in requirements.txt

You can test this program and compare its output to that of oathtool:

python3 ft_otp.py -k ft_otp.key ; oathtool --totp -b $(echo -n "$(cat key.txt)" | xxd -r -p | base32)