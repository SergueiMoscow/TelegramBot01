from PIL import Image, ImageDraw, ImageFont


def draw_price(ticker: str, name: str, price: str, open: str, change_string: str):
    """Draws a picture with the latest price, open price and daily change."""
    im_width = 200
    im_height = 100
    color = '#333333'
    f_price = float(price)
    f_open = float(open)
    # font_name = 'fonts/arial/arial.ttf'
    font_name = 'fonts/MSSansSerif/microsoftsansserif.ttf'
    price_color = "green" if f_price > f_open else "red"
    im = Image.new('RGB', (im_width, im_height), (219, 219, 219))
    draw = ImageDraw.Draw(im)
    # Price
    font = ImageFont.truetype(font_name, 28)
    _, _, w, h = draw.textbbox((0, 0), price, font=font)
    draw.text((im_width - w, im_height / 2 - h / 2), price, fill=price_color, font=font)
    bottom_price = im_height / 2 - h / 2 + h
    # Ticker
    font = ImageFont.truetype(font_name, 14)
    _, _, w, h = draw.textbbox((0, 0), price, font=font)
    draw.text((w / len(ticker), h / 2), ticker, fill=color, font=font)
    # Name
    draw.text((w / len(ticker), h * 2), name, fill=color, font=font)
    # Open
    draw.text((w / len(ticker), im_height - h * 1.5), f'Open {open}', fill=color, font=font)
    # Change
    change_string = change_string  # get_change_string(open, price)
    _, _, w, h = draw.textbbox((0, 0), change_string, font=font)
    draw.text((im_width - w, bottom_price + h / 2), change_string, fill=price_color, font=font)
    return im
    #im.show()
