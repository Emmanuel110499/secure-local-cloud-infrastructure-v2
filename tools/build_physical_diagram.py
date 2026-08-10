from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "diagrams" / "infrastructure-physical-base.png"
OUTPUT = ROOT / "docs" / "diagrams" / "infrastructure-physical-annotated.png"
FONT_ROOT = Path(r"C:\Windows\Fonts")


def main():
    image = Image.open(SOURCE).convert("RGBA")
    canvas = Image.new("RGBA", (image.width, image.height + 420), (244, 248, 252, 255))
    canvas.paste(image, (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")
    bold = ImageFont.truetype(str(FONT_ROOT / "arialbd.ttf"), 30)
    text = ImageFont.truetype(str(FONT_ROOT / "arial.ttf"), 21)
    white = (255, 255, 255, 242)
    navy = (11, 31, 58, 255)
    blue = (37, 99, 235, 255)
    green = (5, 150, 105, 255)
    amber = (217, 119, 6, 255)

    def panel(x, y, width, height, title, lines, color):
        draw.rounded_rectangle(
            (x, y, x + width, y + height), radius=18, fill=white, outline=color, width=4
        )
        draw.text((x + 18, y + 13), title, font=bold, fill=navy)
        cursor = y + 60
        for line in lines:
            draw.text((x + 20, cursor), "• " + line, font=text, fill=navy)
            cursor += 29

    panel(35, 35, 420, 135, "1  INTERNET / CLOUDFLARE", [
        "DNS public et certificat HTTPS", "Zero Trust et tunnel chiffré"
    ], blue)
    panel(1110, 38, 390, 145, "2  PASSERELLE RÉSEAU", [
        "Accès Internet des VM", "Flux privés et pare-feu"
    ], blue)
    panel(40, 980, 720, 315, "3  srv-web - serveur applicatif", [
        "cloudflared : tunnel sortant", "Nginx : reverse proxy",
        "Docker : secure-web-app-v2", "Gunicorn : serveur WSGI",
        "Flask : interface, routes et API", "Node Exporter + cAdvisor : métriques"
    ], blue)
    panel(790, 980, 735, 315, "4  srv-monitoring - observabilité", [
        "Prometheus : collecte et historique", "Grafana : tableaux avancés",
        "Alertmanager : alertes Telegram", "Node Exporter : métriques Linux",
        "Volumes : Prometheus / Grafana / Alertmanager"
    ], green)
    panel(40, 1315, 720, 250, "5  PC Windows - administration", [
        "Navigateur et SSH", "Windows Exporter : CPU, RAM, disque, réseau",
        "Collecteur batterie", "Tâche planifiée de réplication"
    ], amber)
    panel(790, 1315, 735, 250, "6  STOCKAGE DE SECOURS", [
        "Archives srv-web et srv-monitoring", "Empreintes SHA-256",
        "Copie hors VM sur le PC", "Restauration à tester régulièrement"
    ], amber)
    draw.rounded_rectangle((475, 185, 1060, 255), radius=18, fill=(11, 31, 58, 235))
    draw.text((500, 200), "Flux HTTPS et réseaux privés sécurisés", font=bold, fill="white")
    canvas.convert("RGB").save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
