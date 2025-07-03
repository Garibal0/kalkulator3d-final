from firebase_utils import load_filaments, save_filaments, load_historia, save_historia
from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)




@app.route("/")
def index():
    filamenty = load_filaments()
    return render_template("index.html", filamenty=filamenty)


@app.route("/dodaj", methods=["GET", "POST"])
def dodaj():
    filamenty = load_filaments()
    if request.method == "POST":
        nowy = {
            "nazwa": request.form["nazwa"],
            "kolor": request.form["kolor"],
            "cena_za_kg": float(request.form["cena"]),
            "pozostalo_gramow": float(request.form["ilosc"])
        }
        filamenty.append(nowy)
        save_filaments(filamenty)
        return redirect(url_for("index"))
    return render_template("dodaj.html")


@app.route("/edytuj/<int:index>", methods=["GET", "POST"])
def edytuj(index):
    filamenty = load_filaments()

    if request.method == "POST":
        filamenty[index] = {
            "nazwa": request.form["nazwa"],
            "kolor": request.form["kolor"],
            "cena_za_kg": float(request.form["cena"]),
            "pozostalo_gramow": float(request.form["ilosc"])
        }
        save_filaments(filamenty)
        return redirect(url_for("index"))

    # tryb GET: pokaż formularz z danymi
    f = filamenty[index]
    return render_template("dodaj.html", tryb_edytuj=True, index=index, f=f)



@app.route("/usun/<int:index>")
def usun(index):
    filamenty = load_filaments()
    if 0 <= index < len(filamenty):
        filamenty.pop(index)
        save_filaments(filamenty)
    return redirect(url_for("index"))

@app.route("/oblicz", methods=["GET", "POST"])
def oblicz():
    filamenty = load_filaments()
    wynik = None

    if request.method == "POST":
        projekt = request.form["projekt"]
        czas = float(request.form["czas"])
        moc = float(request.form.get("moc", 120))
        wpis_filamenty = []
        koszt_total = 0
        ilosc_total = 0

        for i in range(1, 5):
            idx = request.form.get(f"filament{i}")
            ilosc = request.form.get(f"ilosc{i}")
            if idx and ilosc:
                f = filamenty[int(idx)]
                ilosc = float(ilosc)
                koszt = round((f["cena_za_kg"] / 1000) * ilosc, 2)
                f["pozostalo_gramow"] = max(0, f["pozostalo_gramow"] - ilosc)
                ilosc_total += ilosc
                wpis_filamenty.append({
                    "nazwa": f["nazwa"],
                    "kolor": f["kolor"],
                    "ilosc": ilosc,
                    "koszt": koszt
                })
                koszt_total += koszt

        # energia
        czas_h = czas / 60
        kwh = round((moc * czas_h) / 1000, 3)
        koszt_energii = round(kwh * 1.20, 2)
        koszt_total += koszt_energii

        save_filaments(filamenty)

        historia = load_historia()
        historia.append({
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nazwa_projektu": projekt,
            "filamenty": wpis_filamenty,
            "czas_min": czas,
            "koszt_energii": koszt_energii,
            "koszt_laczny": round(koszt_total, 2)
        })
        save_historia(historia)

        wynik = {
            "filamenty": wpis_filamenty,
            "kwh": kwh,
            "koszt_energii": koszt_energii,
            "koszt_laczny": round(koszt_total, 2),
            "ilosc_total": round(ilosc_total, 1)
        }

    return render_template("oblicz.html", filamenty=filamenty, wynik=wynik)


@app.route("/historia")
def historia():
    dane = load_historia()
    return render_template("historia.html", historia=dane)


@app.route("/historia/<int:id>")
def szczegoly(id):
    dane = load_historia()
    if 0 <= id < len(dane):
        wpis = dane[id]
        # Oblicz kWh jeśli nie było zapisane
        czas = wpis.get("czas_min", 0)
        moc = 120  # stała wartość jak w formularzu
        wpis["kwh"] = round((moc * (czas / 60)) / 1000, 3)
        return render_template("szczegoly.html", wpis=wpis)
    return redirect(url_for("historia"))

@app.route("/historia/usun/<int:id>")
def usun_historia(id):
    historia = load_historia()
    filamenty = load_filaments()

    if 0 <= id < len(historia):
        wpis = historia[id]
        for zuzyty in wpis["filamenty"]:
            for f in filamenty:
                if f["nazwa"] == zuzyty["nazwa"] and f["kolor"] == zuzyty["kolor"]:
                    f["pozostalo_gramow"] += zuzyty["ilosc"]
                    break

        save_filaments(filamenty)
        historia.pop(id)
        save_historia(historia)

    return redirect(url_for("historia"))

# Wersja dla Render – nie uruchamiamy nic lokalnie
# Render uruchomi aplikację przez gunicorn