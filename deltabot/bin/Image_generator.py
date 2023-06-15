from PIL import Image, ImageDraw, ImageOps, ImageFont
import os
import config
import utils

path = config.base_dir
# path = 'deltabot'

def log(msg):
    utils.logger.info(msg)

def main(unit_img_path, relic_final, relic_init, alignment, stars_init, stars_final):
    img_height = 160
    img_width = 160
    gear_height = 130
    star_active = Image.open(f"{path}/source/star-active.png").convert('RGBA')
    arrow_img = Image.open(f"{path}/source/bland-arrow.png").convert('RGBA')
    arrow_img = arrow_img.resize(size=(185, 180))
    new_image = Image.new('RGBA', (160 * 3, 160+ int(star_active.height//1.5)), (0, 0, 0, 0))
    init_img = genImg(unit_img_path, relic_init, alignment, stars_init, img_height, img_width)
    final_img = genImg(unit_img_path, relic_final, alignment, stars_final, img_height, img_width)
    addStars(relic_height=160, new_image=new_image, stars=stars_init, offset=0)
    addStars(relic_height=160, new_image=new_image, stars=stars_final, offset=160*2)
    new_image.alpha_composite(init_img, dest=(0, 0))
    new_image.alpha_composite(arrow_img, dest=(150, -10))
    new_image.alpha_composite(final_img, dest=(160*2, 0))
    new_image.save(f"{path}/tmp/unit_change.png")
    return f"{path}/tmp/unit_change.png"

def genImg(unit_img_path, relic_final, alignment, stars, img_height, img_width):
    gear_height = 130
    alignment = {1:2, 2:0, 3:1}[alignment]
    new_image = Image.new('RGBA', (img_height, img_width), (0, 0, 0, 0))

    if relic_final != '':
        if relic_final[0] == 'R' or relic_final == 'G13':
            new_image = Image.new('RGBA', (img_height, img_width), (0, 0, 0, 0))
            relic_final = int(relic_final[1:]) if relic_final != 'G13' else 0

            addRelicCharImage(relic_width=img_width, new_image=new_image, unit_img_path=unit_img_path)
            addRelicImage(relic_width=img_width, new_image=new_image, relic_final=relic_final, alignment=alignment)

        elif relic_final[0] == 'G':
            gear_offset = 30 // 2
            new_image = Image.new('RGBA', (img_height, img_width - gear_offset), (0, 0, 0, 0))
            relic_final = int(relic_final[1:])

            addGearCharImage(gear_width=img_width, gear_height=gear_height, new_image=new_image, unit_img_path=unit_img_path, gear_offset=gear_offset)
            addGearImage(relic_width=img_width, new_image=new_image, relic_height=gear_height, gear_final=relic_final, gear_offset=gear_offset)
            # addStars(relic_width=img_width, new_image=new_image, stars=stars)

    else:
        new_image = Image.new('RGBA', (img_height, img_width), (0, 0, 0, 0))
        addRelicCharImage(relic_width=img_width, new_image=new_image, unit_img_path=unit_img_path)
        # new_image = addZeta(relic_width=relic_width, new_image=new_image)
        # new_image = addOmicron(relic_width=relic_width, new_image=new_image)

    return new_image;

def addGearCharImage(gear_width, gear_height, new_image, unit_img_path, gear_offset):
    char_img = maskChar(unit_img_path=unit_img_path)
    char_width = gear_width - 40
    char_size = (char_width, char_width)
    char_img = char_img.resize(char_size)
    char_offset = ((gear_width - char_img.width) // 2, (gear_height - char_img.width) // 2 + gear_offset)
    new_image.alpha_composite(char_img, dest=(char_offset))
    
def addRelicCharImage(relic_width, new_image, unit_img_path):
    char_img = maskChar(unit_img_path=unit_img_path)
    char_width = relic_width - 60 
    char_size = (char_width, char_width)
    char_img = char_img.resize(char_size)
    char_offset = ((relic_width - char_img.width) // 2, (relic_width - char_img.width) // 2)
    new_image.alpha_composite(char_img, dest=(char_offset))

def addGearImage(relic_width, new_image, relic_height, gear_final, gear_offset):
    gear_img = Image.open(f"{path}/source/character-gear-frame-atlas.png").convert('RGBA')
    gear_size = (relic_width, relic_height*12)
    gear_img = gear_img.resize(gear_size)
    if gear_final > 0:
        new_image.alpha_composite(gear_img, dest=(0, gear_offset), source=(0, gear_img.height/12 * (gear_final - 1)))
 
def addRelicImage(relic_width, new_image, relic_final, alignment):
    relic_img = Image.open(f"{path}/source/character-frame-relic-atlas.png").convert('RGBA')
    relic_size = (relic_width, relic_width*3)
    relic_img = relic_img.resize(relic_size)
    new_image.alpha_composite(relic_img, dest=(0, 0), source=(0, relic_img.height//3 * alignment))
    if relic_final > 0:
        addRelicBadge(relic_width=relic_width, new_image=new_image, relic_final=relic_final, alignment=alignment)

def addRelicBadge(relic_width, new_image, relic_final, alignment):
    relic_badge_img = getRelicBadge(alignment=alignment)
    relic_badge_offset = ((relic_width -  relic_badge_img.width) // 2,  relic_width - 55)
    new_image.alpha_composite(relic_badge_img, dest=(relic_badge_offset))
    font = ImageFont.truetype(f"{path}/source/Titillium-Regular.otf", 20)
    draw2 = ImageDraw.Draw(new_image)
    draw2.text(((new_image.width - 12) // 2, new_image.width - 37), str(relic_final), font=font, align="center", stroke_fill="black", stroke_width=3)

def addStars(relic_height, new_image, stars, offset):

    i = 1
    star_active = Image.open(f"{path}/source/star-active.png").convert('RGBA')
    star_inactive = Image.open(f"{path}/source/star-inactive.png").convert('RGBA')
    
    while i <= 7:
        if i <= stars:
            relic_badge_offset = ((i-1) * star_inactive.width + 2 + offset, relic_height - star_inactive.height//4)
            new_image.alpha_composite(star_active, dest=(relic_badge_offset))

        else:
            relic_badge_offset = ((i-1) * star_inactive.width + 2 + offset, relic_height - star_inactive.height//4)
            new_image.alpha_composite(star_inactive, dest=(relic_badge_offset))

        i += 1

def addZeta(relic_width, new_image):
    zeta_img = Image.open(f"{path}/source/tex.skill_zeta_glow.png").convert('RGBA')
    zeta_size = (45, 45)
    zeta_img = zeta_img.resize(zeta_size)
    zeta_offset = ((relic_width - zeta_img.width) // 2 - 40, (relic_width - zeta_img.width) // 2 + 30)
    new_image.alpha_composite(zeta_img, dest=(zeta_offset))
    font2 = ImageFont.truetype(f"{path}/source/Titillium-Regular.otf", 12)
    draw2 = ImageDraw.Draw(new_image)
    draw2.text(((new_image.width - 88) // 2, new_image.width - 55), "1", font=font2, align="center", stroke_fill="black", stroke_width=3)
    return new_image

def addOmicron(relic_width, new_image):
    omega_img = Image.open(f"{path}/source/omicron-badge.png").convert('RGBA')
    omega_size = (45, 45)
    omega_img = omega_img.resize(omega_size)
    omega_offset = ((relic_width - omega_img.width) // 2 + 40, (relic_width - omega_img.width) // 2 + 30)
    new_image.alpha_composite(omega_img, dest=(omega_offset))
    font2 = ImageFont.truetype(f"{path}/source/Titillium-Regular.otf", 12)
    draw2 = ImageDraw.Draw(new_image)
    draw2.text(((new_image.width + 72) // 2, new_image.width - 56), "1", font=font2, align="center", stroke_fill="black", stroke_width=3)
    return new_image

def getRelicBadge(alignment):
    if alignment == 2:
        alignment = 3
    relic_badge_img = Image.open(f"{path}/source/relic-badge-atlas.png").convert('RGBA')
    # relic_badge_img.resize(50, 50*4)
    mask = Image.new("L", (relic_badge_img.width, relic_badge_img.width), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (relic_badge_img.width, relic_badge_img.width), fill=255)
    # light side: (0.5, 0), dark side: (0.5, .33), GL: (0.5, .67), neutral: (0.5, 1) 
    masked_img = ImageOps.fit(relic_badge_img, mask.size, centering=(0.5, (alignment / 3.0)))
    result_img = Image.new("RGBA", masked_img.size, (0, 0, 0, 0)) 
    result_img.paste(masked_img, (0, 0), masked_img)

    return result_img

def maskChar(unit_img_path):
    char_img = Image.open(unit_img_path).convert('RGBA')
    # Create relic_width mask
    mask = Image.new("L", char_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + char_img.size, fill=255, width=25)

    # Apply the mask
    char_img = ImageOps.fit(char_img, mask.size, centering=(0.5, 0.5))
    char_img.putalpha(mask)

    return char_img

if __name__ == "__main__":
    unit_img_path = f"{path}/resources/Aayla_Secura.png"
    relic_final = 'R6'
    relic_init = 'G1'
    alignment = 2
    main(unit_img_path, relic_final, relic_init, alignment)