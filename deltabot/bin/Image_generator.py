from PIL import Image, ImageDraw, ImageOps, ImageFont
import os
import config
import utils

path = config.base_dir
# path = 'deltabot'

def log(msg):
    utils.logger.info(msg)

def main(unit_img_path, relic_final, relic_init, alignment, stars_init, stars_final, zeta_count_init, zeta_count_latest, omicron_count_init ,omicron_count_latest):
    img_height = 160
    img_width = 160
    gear_height = 130
    star_active = Image.open(f"{path}/source/star-active.png").convert('RGBA')
    arrow_img = Image.open(f"{path}/source/bland-arrow.png").convert('RGBA')
    arrow_img = arrow_img.resize(size=(185, 180))
    base_image = Image.new('RGBA', (160 * 3, 160+ int(star_active.height//1.5)), (0, 0, 0, 0))
    init_img = gen_img(unit_img_path, relic_init, alignment, stars_init, img_height, img_width, zeta_count_init, omicron_count_init)
    final_img = gen_img(unit_img_path, relic_final, alignment, stars_final, img_height, img_width, zeta_count_latest, omicron_count_latest)
    add_stars(relic_height=160, base_image=base_image, stars=stars_init, offset=0)
    add_stars(relic_height=160, base_image=base_image, stars=stars_final, offset=160*2)
    base_image.alpha_composite(init_img, dest=(0, 0))
    base_image.alpha_composite(arrow_img, dest=(150, -10))
    base_image.alpha_composite(final_img, dest=(160*2, 0))
    base_image.save(f"{path}/tmp/unit_change.png")
    return f"{path}/tmp/unit_change.png"

def gen_img(unit_img_path, relic_final, alignment, stars, img_height, img_width, zeta_cnt, omicron_cnt):
    gear_height = 130
    alignment = {1:2, 2:0, 3:1}[alignment]
    base_image = Image.new('RGBA', (img_height, img_width), (0, 0, 0, 0))

    if relic_final != '':
        if relic_final[0] == 'R' or relic_final == 'G13':
            base_image = Image.new('RGBA', (img_height, img_width), (0, 0, 0, 0))
            relic_final = int(relic_final[1:]) if relic_final != 'G13' else 0

            add_relic_char_image(relic_width=img_width, base_image=base_image, unit_img_path=unit_img_path)
            add_relic_image(relic_width=img_width, base_image=base_image, relic_final=relic_final, alignment=alignment)

        elif relic_final[0] == 'G':
            gear_offset = 30 // 2
            base_image = Image.new('RGBA', (img_height, img_width - gear_offset), (0, 0, 0, 0))
            relic_final = int(relic_final[1:])

            add_gear_char_image(gear_width=img_width, gear_height=gear_height, base_image=base_image, unit_img_path=unit_img_path, gear_offset=gear_offset)
            add_gear_image(relic_width=img_width, base_image=base_image, relic_height=gear_height, gear_final=relic_final, gear_offset=gear_offset)
            # add_stars(relic_width=img_width, base_image=base_image, stars=stars)

    else:
        base_image = Image.new('RGBA', (img_height, img_width), (0, 0, 0, 0))
        add_relic_char_image(relic_width=img_width, base_image=base_image, unit_img_path=unit_img_path)
        
    if zeta_cnt > 0:
        base_image = add_zeta(relic_width=img_width, base_image=base_image, zeta_cnt=str(zeta_cnt))
    if omicron_cnt > 0:
        base_image = add_omicron(relic_width=img_width, base_image=base_image, omicron_cnt=str(omicron_cnt))

    return base_image;

def add_gear_char_image(gear_width, gear_height, base_image, unit_img_path, gear_offset):
    char_img = mask_char(unit_img_path=unit_img_path)
    char_width = gear_width - 40
    char_size = (char_width, char_width)
    char_img = char_img.resize(char_size)
    char_offset = ((gear_width - char_img.width) // 2, (gear_height - char_img.width) // 2 + gear_offset)
    base_image.alpha_composite(char_img, dest=(char_offset))
    
def add_relic_char_image(relic_width, base_image, unit_img_path):
    char_img = mask_char(unit_img_path=unit_img_path)
    char_width = relic_width - 60 
    char_size = (char_width, char_width)
    char_img = char_img.resize(char_size)
    char_offset = ((relic_width - char_img.width) // 2, (relic_width - char_img.width) // 2)
    base_image.alpha_composite(char_img, dest=(char_offset))

def add_gear_image(relic_width, base_image, relic_height, gear_final, gear_offset):
    gear_img = Image.open(f"{path}/source/character-gear-frame-atlas.png").convert('RGBA')
    gear_size = (relic_width, relic_height*12)
    gear_img = gear_img.resize(gear_size)
    if gear_final > 0:
        base_image.alpha_composite(gear_img, dest=(0, gear_offset), source=(0, gear_img.height/12 * (gear_final - 1)))
 
def add_relic_image(relic_width, base_image, relic_final, alignment):
    relic_img = Image.open(f"{path}/source/character-frame-relic-atlas.png").convert('RGBA')
    relic_size = (relic_width, relic_width*3)
    relic_img = relic_img.resize(relic_size)
    base_image.alpha_composite(relic_img, dest=(0, 0), source=(0, relic_img.height//3 * alignment))
    if relic_final > 0:
        add_relic_badge(relic_width=relic_width, base_image=base_image, relic_final=relic_final, alignment=alignment)

def add_relic_badge(relic_width, base_image, relic_final, alignment):
    relic_badge_img = get_relic_badge(alignment=alignment)
    relic_badge_offset = ((relic_width -  relic_badge_img.width) // 2,  relic_width - 55)
    base_image.alpha_composite(relic_badge_img, dest=(relic_badge_offset))
    font = ImageFont.truetype(f"{path}/source/Titillium-Regular.otf", 20)
    draw2 = ImageDraw.Draw(base_image)
    draw2.text(((base_image.width - 12) // 2, base_image.width - 37), str(relic_final), font=font, align="center", stroke_fill="black", stroke_width=3)

def add_stars(relic_height, base_image, stars, offset):

    i = 1
    star_active = Image.open(f"{path}/source/star-active.png").convert('RGBA')
    star_inactive = Image.open(f"{path}/source/star-inactive.png").convert('RGBA')
    
    while i <= 7:
        if i <= stars:
            relic_badge_offset = ((i-1) * star_inactive.width + 2 + offset, relic_height - star_inactive.height//2)
            base_image.alpha_composite(star_active, dest=(relic_badge_offset))

        else:
            relic_badge_offset = ((i-1) * star_inactive.width + 2 + offset, relic_height - star_inactive.height//2)
            base_image.alpha_composite(star_inactive, dest=(relic_badge_offset))

        i += 1

def add_zeta(relic_width, base_image, zeta_cnt):
    zeta_img = Image.open(f"{path}/source/tex.skill_zeta_glow.png").convert('RGBA')
    zeta_size = (45, 45)
    zeta_img = zeta_img.resize(zeta_size)
    zeta_offset = ((relic_width - zeta_img.width) // 2 - 40, (relic_width - zeta_img.width) // 2 + 30)
    base_image.alpha_composite(zeta_img, dest=(zeta_offset))
    font2 = ImageFont.truetype(f"{path}/source/Titillium-Regular.otf", 20)
    draw2 = ImageDraw.Draw(base_image)
    draw2.text(((base_image.width - 90) // 2, base_image.width - 62), zeta_cnt, font=font2, align="center", stroke_fill="black", stroke_width=1)
    return base_image

def add_omicron(relic_width, base_image, omicron_cnt):
    omega_img = Image.open(f"{path}/source/omicron-badge.png").convert('RGBA')
    omega_size = (50, 50)
    omega_img = omega_img.resize(omega_size)
    omega_offset = ((relic_width - omega_img.width) // 2 + 40, (relic_width - omega_img.width) // 2 + 30)
    base_image.alpha_composite(omega_img, dest=(omega_offset))
    font2 = ImageFont.truetype(f"{path}/source/Titillium-Regular.otf", 23)
    draw2 = ImageDraw.Draw(base_image)
    draw2.text(((base_image.width + 68) // 2, base_image.width - 63), omicron_cnt, font=font2, align="center", stroke_fill="black", stroke_width=3)
    return base_image

def get_relic_badge(alignment):
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

def mask_char(unit_img_path):
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
