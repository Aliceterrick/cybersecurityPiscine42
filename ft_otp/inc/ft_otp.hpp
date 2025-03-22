#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>
#include <openssl/err.h> 
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <ctime>
#include <vector>
#include <stdexcept>

using namespace std;

const string KEY_FILE = "secret.key";
const int SALT_LEN = 16;
const int IV_LEN = 16;
const int KEY_LEN = 32; // AES-256
const int ITERATIONS = 100000;
const int DIGITS = 6;
const int TIME_STEP = 30;

void generateKey();
void generateOTP();
vector<unsigned char> deriveKey(const string& password, const vector<unsigned char>& salt);
string bytesToHex(const vector<unsigned char>& bytes);
vector<unsigned char> hexToBytes(const string& hex);
int hotp(const vector<unsigned char>& key, uint64_t counter);
void handleOpenSSLError();