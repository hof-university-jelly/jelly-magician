Python 3 sollte installiert sein.

```bash
# Repository klonen
git clone https://github.com/hof-university-jelly/jelly-obj-detection
cd jelly-obj-detection

# Dependencies am besten über ein virtual environment verwalten
python3 -m venv venv

# Virtuelles Env laden. Das passende activate-Script sourcen,
# je nachdem was für eine Shell ihr verwendet
source venv/bin/activate.fish

# Kurz testen ob das venv geladen wurde
# Die Ausgabe sollte im Pfad von venv enthalten sein
which python3
which pip3

# Das installiert eure dependencies im venv
pip3 install -r requirements.txt

# Programm starten
python3 main.py

```
