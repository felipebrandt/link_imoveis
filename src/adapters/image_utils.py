

def base64_to_png(property_id, base64_img):
    with open(f"..\\src\\static\\img\\{property_id}.png", "wb") as fh:
        fh.write(base64_img)