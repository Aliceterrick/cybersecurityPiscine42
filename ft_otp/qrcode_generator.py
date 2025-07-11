import qrcode
from PIL import Image

def qr_gen(otp):
    if not otp:
        print("No seed. Stop.")
        return
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
    )
    qr.add_data(otp)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    logo = Image.open('.qr/.logo.png')
    logo.thumbnail((60, 60))
    logo_pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
    img.paste(logo, logo_pos)
    img.save('.qr/.qr.png')
    img = Image.open('.qr/.qr.png')
    img.show()
