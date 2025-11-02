import qrcode


def generate_donatable_qr(name, quantity, expiry_date):

    data = f"Name: {name}\nQuantity: {quantity}\nExpiry: {expiry_date}\nDonatable: Yes"

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    filename = f"{name}_donatable_qr.png"
    img.save(filename)
    print(f"✅ QR code generated: {filename}\n")
