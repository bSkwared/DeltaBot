from PIL import Image, ImageDraw, ImageOps, ImageFont
import os
import config


def main(unit_img_path, relic_final):
    relic_width = 160
    relic_height = 160
    gear_width = 160
    gear_height = 130
    if relic_final[0] == 'R' or relic_final == 'G13':
        new_image = Image.new('RGBA', (relic_width, relic_height), (0, 0, 0, 0))
        addRelicCharImage(relic_width=relic_width, new_image=new_image, unit_img_path=unit_img_path)
        addRelicImage(relic_width=relic_width, new_image=new_image, relic_final=relic_final)

    elif relic_final[0] == 'G':
        new_image = Image.new('RGBA', (gear_width, gear_height), (0, 0, 0, 0))
        addGearCharImage(gear_width=gear_width, gear_height=gear_height, new_image=new_image, unit_img_path=unit_img_path)
        addGearImage(relic_width=gear_width, new_image=new_image, relic_height=gear_height, gear_final=relic_final)

    # addZeta(relic_width=relic_width, new_image=new_image)
    # addOmicron(relic_width=relic_width, new_image=new_image)
    new_image.save(f"{config.base_dir}/tmp/combined_image.png")
    return f"{config.base_dir}/tmp/combined_image.png"

def addGearCharImage(gear_width, gear_height, new_image, unit_img_path):
    char_img = maskChar(unit_img_path=unit_img_path)
    char_width = gear_width - 40
    char_size = (char_width, char_width)
    char_img = char_img.resize(char_size)
    char_offset = ((gear_width - char_img.width) // 2, (gear_height - char_img.width) // 2)
    new_image.alpha_composite(char_img, dest=(char_offset))
    
def addRelicCharImage(relic_width, new_image, unit_img_path):
    char_img = maskChar(unit_img_path=unit_img_path)
    char_width = relic_width - 60 
    char_size = (char_width, char_width)
    char_img = char_img.resize(char_size)
    char_offset = ((relic_width - char_img.width) // 2, (relic_width - char_img.width) // 2)
    new_image.alpha_composite(char_img, dest=(char_offset))

def addGearImage(relic_width, new_image, relic_height, gear_final):
    gear_img = Image.open(f"{config.base_dir}/source/character-gear-frame-atlas.png").convert('RGBA')
    gear_size = (relic_width, relic_height*12)
    gear_img = gear_img.resize(gear_size)

    new_image.alpha_composite(gear_img, dest=(0, 0), source=(0, gear_img.height/12 * gear_final - 2))
 
def addRelicImage(relic_width, new_image, relic_final):
    relic_img = Image.open(f"{config.base_dir}/source/character-frame-relic-atlas.png").convert('RGBA')
    relic_size = (relic_width, relic_width*3)
    relic_img = relic_img.resize(relic_size)
    new_image.alpha_composite(relic_img, dest=(0, 0), source=(0, relic_img.height//3 * 1))
    addRelicBadge(relic_width=relic_width, new_image=new_image, relic_final=relic_final)

def addRelicBadge(relic_width, new_image, relic_final):
    relic_badge_img = getRelicBadge()
    relic_badge_offset = ((relic_width -  relic_badge_img.width) // 2,  relic_width - 55)
    new_image.alpha_composite(relic_badge_img, dest=(relic_badge_offset))
    font = ImageFont.truetype(f"{config.base_dir}/source/Titillium-Regular.otf", 20)
    draw2 = ImageDraw.Draw(new_image)
    draw2.text(((new_image.width - 12) // 2, new_image.width - 37), relic_final, font=font, align="center", stroke_fill="black", stroke_width=3)
    
def addZeta(relic_width, new_image):
    zeta_img = Image.open(f"{config.base_dir}/source/tex.skill_zeta_glow.png").convert('RGBA')
    zeta_size = (relic_width // 4, relic_width // 4)
    zeta_img = zeta_img.resize(zeta_size)
    zeta_offset = ((relic_width - zeta_img.width) // 2 - 40, (relic_width - zeta_img.width) // 2 + 30)
    new_image.alpha_composite(zeta_img, dest=(zeta_offset))
    font2 = ImageFont.truetype(f"{config.base_dir}/source/Titillium-Regular.otf", 12)
    draw2 = ImageDraw.Draw(new_image)
    draw2.text(((new_image.width - 88) // 2, new_image.width - 55), "1", font=font2, align="center", stroke_fill="black", stroke_width=3)

def addOmicron(relic_width, new_image):
    omega_img = Image.open(f"{config.base_dir}/source/omicron-badge.png").convert('RGBA')
    omega_size = (relic_width // 4, relic_width // 4)
    omega_img = omega_img.resize(omega_size)
    omega_offset = ((relic_width - omega_img.width) // 2 + 40, (relic_width - omega_img.width) // 2 + 30)
    new_image.alpha_composite(omega_img, dest=(omega_offset))
    font2 = ImageFont.truetype(f"{config.base_dir}/source/Titillium-Regular.otf", 12)
    draw2 = ImageDraw.Draw(new_image)
    draw2.text(((new_image.width + 72) // 2, new_image.width - 56), "1", font=font2, align="center", stroke_fill="black", stroke_width=3)

def getRelicBadge():
    relic_badge_img = Image.open(f"{config.base_dir}/source/relic-badge-atlas.png").convert('RGBA')
    mask = Image.new("L", (relic_badge_img.width, relic_badge_img.width), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (relic_badge_img.width, relic_badge_img.width), fill=255)
    # light side: (0.5, 0), dark side: (0.5, .33), GL: (0.5, .67), neutral: (0.5, 1) 
    masked_img = ImageOps.fit(relic_badge_img, mask.size, centering=(0.5, .33))
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
    main()