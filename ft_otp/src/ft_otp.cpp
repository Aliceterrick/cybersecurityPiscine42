#include "../inc/ft_otp.hpp"

void generateKey() {
	vector<unsigned char> secret(32);
	if (!RAND_bytes(secret.data(), secret.size()))
		throw runtime_error("Key generation failed");

	string hexSecret = bytesToHex(secret);

	cout << "Entrez un mot de passe de chiffrement: ";
	string password;
	getline(cin, password);

	vector<unsigned char> salt(SALT_LEN);
	if (!RAND_bytes(salt.data(), salt.size()))
		throw runtime_error("Salt generation failed");

	vector<unsigned char> key = deriveKey(password, salt);

	vector<unsigned char> iv(IV_LEN);
	if (!RAND_bytes(iv.data(), iv.size()))
		throw runtime_error("IV generation failed");

	EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
	if (!ctx) throw runtime_error("Context creation failed");

	if (!EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key.data(), iv.data()))
		handleOpenSSLError();

	vector<unsigned char> ciphertext(hexSecret.size() + EVP_CIPHER_block_size(EVP_aes_256_cbc()));
	int len, ciphertext_len = 0;

	if (!EVP_EncryptUpdate(ctx, ciphertext.data(), &len, 
		reinterpret_cast<const unsigned char*>(hexSecret.data()), hexSecret.size()))
		handleOpenSSLError();
	ciphertext_len = len;

	if (!EVP_EncryptFinal_ex(ctx, ciphertext.data() + len, &len))
		handleOpenSSLError();
	ciphertext_len += len;

	EVP_CIPHER_CTX_free(ctx);
	ciphertext.resize(ciphertext_len);

	ofstream file(KEY_FILE, ios::binary);
	file.write(reinterpret_cast<char*>(salt.data()), salt.size());
	file.write(reinterpret_cast<char*>(iv.data()), iv.size());
	file.write(reinterpret_cast<char*>(ciphertext.data()), ciphertext.size());
}

void generateOTP() {
	ifstream file(KEY_FILE, ios::binary);
	if (!file) throw runtime_error("Key file not found");

	vector<unsigned char> salt(SALT_LEN);
	vector<unsigned char> iv(IV_LEN);
	vector<unsigned char> ciphertext;

	file.read(reinterpret_cast<char*>(salt.data()), salt.size());
	file.read(reinterpret_cast<char*>(iv.data()), iv.size());
	ciphertext.assign(istreambuf_iterator<char>(file), {});

	cout << "Entrez le mot de passe: ";
	string password;
	getline(cin, password);

	vector<unsigned char> key = deriveKey(password, salt);

	EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
	if (!ctx) throw runtime_error("Context creation failed");

	if (!EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key.data(), iv.data()))
		handleOpenSSLError();

	vector<unsigned char> plaintext(ciphertext.size() + EVP_CIPHER_block_size(EVP_aes_256_cbc()));
	int len, plaintext_len = 0;

	if (!EVP_DecryptUpdate(ctx, plaintext.data(), &len, ciphertext.data(), ciphertext.size()))
		handleOpenSSLError();
	plaintext_len = len;

	if (!EVP_DecryptFinal_ex(ctx, plaintext.data() + len, &len))
		throw runtime_error("Decryption failed - wrong password?");
	plaintext_len += len;

	EVP_CIPHER_CTX_free(ctx);
	plaintext.resize(plaintext_len);

	string hexSecret(plaintext.begin(), plaintext.end());
	if (hexSecret.length() != 64)
		throw runtime_error("Invalid key length");

	vector<unsigned char> secret = hexToBytes(hexSecret);

	uint64_t counter = time(nullptr) / TIME_STEP;
	int code = hotp(secret, counter);
	cout << "Code OTP: " << setw(6) << setfill('0') << code << "\n";
}

vector<unsigned char> deriveKey(const string& password, const vector<unsigned char>& salt) {
	vector<unsigned char> key(KEY_LEN);
	if (PKCS5_PBKDF2_HMAC(
		password.c_str(), password.size(),
		salt.data(), salt.size(),
		ITERATIONS, EVP_sha256(),
		KEY_LEN, key.data()) != 1)
		throw runtime_error("Key derivation failed");
	return key;
}

string bytesToHex(const vector<unsigned char>& bytes) {
	stringstream ss;
	ss << hex << setfill('0');
	for (const auto& byte : bytes)
		ss << setw(2) << static_cast<int>(byte);
	return ss.str();
}

vector<unsigned char> hexToBytes(const string& hex) {
	if (hex.length() % 2 != 0)
		throw runtime_error("Invalid hex string");

	vector<unsigned char> bytes;
	for (size_t i = 0; i < hex.length(); i += 2) {
		string byteString = hex.substr(i, 2);
		try {
			bytes.push_back(stoi(byteString, nullptr, 16));
		} catch (...) {
			throw runtime_error("Invalid hex character");
		}
	}
	return bytes;
}

int hotp(const vector<unsigned char>& key, uint64_t counter) {
	vector<unsigned char> counter_bytes;
	for (int i = 7; i >= 0; --i)
		counter_bytes.push_back((counter >> (i * 8)) & 0xFF);

	unsigned char hmac[EVP_MAX_MD_SIZE];
	unsigned int hmac_len;
	
	if (!HMAC(EVP_sha1(), 
			 key.data(), key.size(),
			 counter_bytes.data(), counter_bytes.size(),
			 hmac, &hmac_len))
		handleOpenSSLError();

	int offset = hmac[hmac_len - 1] & 0x0F;
	int binary = ((hmac[offset] & 0x7F) << 24) |
				 (hmac[offset + 1] << 16) |
				 (hmac[offset + 2] << 8) |
				 hmac[offset + 3];

	return binary % 1000000;
}

void handleOpenSSLError() {
	char buffer[120];
	ERR_error_string(ERR_get_error(), buffer);
	throw runtime_error(buffer);
}


int main(int argc, char* argv[]) {
	if (argc != 2) {
		cerr << "Usage: " << argv[0] << " -g [key] | -k [key]\n";
		return 1;
	}

	string option = argv[1];
	if (option == "-g") generateKey();
	else if (option == "-k") generateOTP();
	else {
		cerr << "Error: Invalid option\n";
		return 1;
	}
	return 0;
}