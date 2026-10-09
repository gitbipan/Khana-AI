
# Helper script to generate visual sample food photos for testing PoshanAI.
# Generates realistic labeled plate graphics for Dal Bhat, Momo, Dhindo, Kwati, and Sel Roti.

//libraries
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "static" / "sample_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_image(
    bg_color: tuple,
    filename: str,
    plate_color: tuple,
    title: str,
    subtitle: str,
    components: list[tuple[str, tuple, tuple]],  # (name, color, bbox)
):
    size = (600, 600)
    img = Image.new("RGB", size, bg_color)
    draw = ImageDraw.Draw(img)

    draw.rectangle([10, 10, 590, 590], outline=(100, 90, 80), width=4)

    plate_box = [60, 60, 540, 540]
    draw.ellipse(plate_box, fill=plate_color, outline=(70, 60, 45), width=6)
    draw.ellipse([80, 80, 520, 520], outline=(160, 140, 90), width=2)

    for name, color, bbox in components:
        draw.ellipse(bbox, fill=color, outline=(40, 30, 20), width=2)

        # Center text indicator wala
        cx = (bbox[0] + bbox[2]) // 2
        cy = (bbox[1] + bbox[3]) // 2
        draw.text((cx - 30, cy - 8), name, fill=(255, 255, 255))

    # Banner header
    draw.rectangle([40, 20, 560, 75], fill=(30, 30, 30, 219), outline=(210, 170, 70), width=2)
    draw.text((60, 28), title, fill=(255, 230, 150))
    draw.text((60, 50), subtitle, fill=(220, 220, 220))

    dest = OUTPUT_DIR / filename
    img.save(dest, format="JPEG", quality=90)
    print(f"Generated sample food image: {dest}")


def generate_all_samples():
    # nepali food like dal bhat tarkari, momo, kodo, dhindo etc generated here
    # 1. Dal Bhat Tarkari Thali (दाल भात तरकारी)
    create_sample_image(
        filename="dal_bhat_tarkari.jpg",
        bg_color=(235, 225, 210),
        plate_color=(218, 178, 92),  # Brass Thali (काँसको थाली)
        title="Nepali Thali - Dal Bhat Tarkari (दाल भात तरकारी)",
        subtitle="Staple: Steamed White Rice (भात), Dal (दाल), Saag (साग), Tarkari",
        components=[
            ("Rice (भात)", (245, 245, 240), [190, 190, 410, 410]),     # Center rice mountain
            ("Dal (दाल)", (210, 150, 40), [100, 110, 230, 230]),       # Top-left Dal bowl
            ("Tarkari", (190, 100, 40), [370, 110, 500, 230]),          # Top-right Curry bowl
            ("Saag (साग)", (45, 110, 45), [110, 370, 230, 490]),        # Bottom-left greens
            ("Achar", (180, 50, 35), [380, 380, 480, 480]),             # Bottom-right tomato achar
        ]
    )

    # 2. Momo Plate (म:म:)
    create_sample_image(
        filename="momo_plate.jpg",
        bg_color=(240, 235, 230),
        plate_color=(245, 245, 245),  # White ceramic plate
        title="Steamed Momo Platter (कुखुराको म:म:)",
        subtitle="10 pcs Steamed Dumplings with Tomato Sesame Achar",
        components=[
            ("Achar", (200, 90, 30), [240, 240, 360, 360]),           # Center achar bowl
            ("Momo 1", (235, 230, 215), [150, 120, 230, 200]),
            ("Momo 2", (235, 230, 215), [260, 100, 340, 180]),
            ("Momo 3", (235, 230, 215), [370, 120, 450, 200]),
            ("Momo 4", (235, 230, 215), [420, 230, 500, 310]),
            ("Momo 5", (235, 230, 215), [390, 340, 470, 420]),
            ("Momo 6", (235, 230, 215), [310, 420, 390, 500]),
            ("Momo 7", (235, 230, 215), [210, 420, 290, 500]),
            ("Momo 8", (235, 230, 215), [130, 340, 210, 420]),
            ("Momo 9", (235, 230, 215), [100, 230, 180, 310]),
        ]
    )

    # 3. Kodo Dhindo with Gundruk & Bhatmas (कोदोको ढिँडो र गुन्द्रुक)
    create_sample_image(
        filename="dhindo_gundruk.jpg",
        bg_color=(230, 220, 210),
        plate_color=(190, 150, 80),  # Traditional brass platter
        title="Millet Dhindo with Gundruk (कोदोको ढिँडो र गुन्द्रुक)",
        subtitle="Indigenous superfood rich in Calcium, Fiber & Iron",
        components=[
            ("Dhindo", (95, 75, 65), [180, 180, 420, 420]),             # Dark purple/brown millet dhindo mound
            ("Gundruk", (80, 95, 50), [100, 120, 230, 240]),           # Gundruk soup bowl
            ("Ghyu", (245, 220, 100), [370, 120, 470, 220]),           # Pure ghee cup
            ("Bhatmas", (170, 110, 60), [110, 360, 230, 480]),         # Roasted soybeans
            ("Mula Achar", (220, 80, 60), [370, 360, 490, 480]),       # Fermented radish pickle
        ]
    )

    # 4. Kwati Soup (क्वाँटी)
    create_sample_image(
        filename="kwati_soup.jpg",
        bg_color=(238, 230, 220),
        plate_color=(220, 210, 195),
        title="Sprouted 9-Bean Kwati Soup (क्वाँटी)",
        subtitle="High-protein pulse soup with Ajwain (Jwano) tempering",
        components=[
            ("Kwati Bowl", (160, 95, 45), [120, 120, 480, 480]),
            ("Beans", (110, 60, 30), [200, 200, 400, 400]),
        ]
    )

    # 5. Sel Roti & Aloo Achar (सेल रोटी र आलुको अचार)
    create_sample_image(
        filename="sel_roti.jpg",
        bg_color=(240, 230, 218),
        plate_color=(230, 225, 213),
        title="Festive Sel Roti Platter (सेल रोटी)",
        subtitle="Traditional ring bread with spiced potato pickle",
        components=[
            ("Sel Roti 1", (195, 120, 40), [130, 130, 350, 350]),
            ("Sel Roti 2", (185, 110, 35), [250, 250, 470, 470]),
            ("Aloo Achar", (210, 140, 50), [360, 120, 480, 240]),
        ]
    )

    print("All sample food images successfully generated.")


if __name__ == "__main__":
    generate_all_samples() 
    # as soon as programs starts, samples are generated 
