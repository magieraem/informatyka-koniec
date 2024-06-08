import psychopy
from psychopy import visual, core, event, gui, sound
import pandas as pd
import csv
import random  # Import random module to shuffle DataFrame rows

# pobiera slowa z pliku zewnetrzmego 
df = pd.read_csv("stimulislowa.csv", sep=";")

# zbiera dane osob badanych i zapisuje jako slownik dialog
info = {"ID": "", "Wiek": "", "Płeć": ["Kobieta", "Mężczyzna", "Inna"]}
dialog = gui.DlgFromDict(dictionary=info, title="Dane osoby badanej")

#wyjdzie jesli puste
if not dialog.OK:
    core.quit()

# Tworzy albo otwiera istniejacy plik CSV oraz zapisuje dane osob badanych
#Nazwa pliku będzie zależała od identyfikatora uczestnika, który wprowadzany jest w oknie dialogowym na początku, oraz będzie zawierała prefiks "participant_" przed tym identyfikatorem. Dla przykładu, jeśli identyfikator uczestnika to "123", nazwa pliku będzie wyglądać tak: "participant_123.csv"
output_file = f"participant_{info['ID']}.csv"
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Trial", "Word1", "Word2", "Response", "Correct", "ReactionTime"])

# mozliwosc wyjscia z procedury badawczej
def check_exit(key="Q"):
    stop = event.getKeys(keyList=[key])
    if len(stop) > 0:
        exit(1)

# otwiera okno procedury
win = visual.Window([1280, 720], color="#F5F5F5", monitor="testMonitor", units="norm", fullscr=False)

# ustawia FPS na 60 zeby nie bylo bedu z tym
win.refreshThreshold = 1 / 60.0  # Set the refresh threshold to match 60 FPS

# wyswietla instrukcje badania
instrukcje = [
    "W tym zadaniu, które zaraz zobaczysz na ekranie pojawią się jednocześnie dwa słowa. Twoim zadaniem jest ocenić, czy słowa są słowami prawdziwymi czy bezsensownymi. Jeśli oba słowa są prawdziwymi polskimi słowami, naciśnij na klawiaturze „m”. Jeśli jeden lub oba słowa są słowami bezsensownymi, naciśnij na klawiaturze „z”.",
    "Przykłady poprawnych zestawów słów (takich, przy których należy kliknąć „m”): WIOSNA - WIATR. Przykłady niepoprawnych zestawów słów (takich, przy których należy kliknąć „z”): WIOSNA - UZYLE lub AGWITK - HATOPS. W niektórych częściach badania będziesz słuchał/a muzyki. Prosimy o nie zmienianie jej głośności - to część eksperymentu.",
    "Przed rozpoczęciem sesji eksperymentalnej, będziesz poddany krótkiej sesji treningowej, która pomoże Ci zrozumieć zadanie. W trakcie tej sesji treningowej otrzymasz informację po każdej udzielonej odpowiedzi, czy była poprawna. Postaraj się odpowiadać poprawnie i szybko, ponieważ czas Twojej reakcji będzie mierzony."
]
bottom_text = "[Naciśnij spację, aby przejść dalej]"

# odczytuje pliki dzwiekowe
muz_bez_slow = sound.Sound("bezslow.wav")
muz_slowa = sound.Sound("zeslowami.wav")

# funkcja dla latwiejszego wyswietlania tekstu na przyszlosc
def display_text(win, main_text, bottom_text=None):
    instruction_text = visual.TextStim(win, text=main_text, color="black", wrapWidth=1.2, pos=(0, 0.2))
    instruction_text.draw()
    if bottom_text:
        bottom_text_stim = visual.TextStim(win, text=bottom_text, color="black", pos=(0, -0.8))
        bottom_text_stim.draw()
    win.flip()
    event.waitKeys(keyList=["space"])

# instruckje wyswietla
for instrukcja in instrukcje:
    display_text(win, instrukcja, bottom_text)

# sesja treningowa
def trening(df, num_trials=15, min_pop=8):
    df = df.sample(n=num_trials)
    pop_odp_count = 0

    for liczba_prob, row in df.iterrows():
        para = f"{row['Slowo1']} \n {row['Slowo2']}"
        fix = visual.TextStim(win, text='+', color=(-1, -1, -1))
        fix.draw()
        win.flip()
        core.wait(0.8)

        word_stim = visual.TextStim(win, text=para, color=(-1, -1, -1), pos=(0.0, 0.0))
        word_stim.draw()
        win.flip()
        
        timer = core.Clock()  # Start the clock
        odp = event.waitKeys(maxWait=3, keyList=['m', 'z'], timeStamped=timer)
        
        if odp:
            key, rt = odp[0]
        else:
            key, rt = None, None

        pop_odp = 'm' if row['Relacja'] == 1 else 'z'

        if key:
            if key == pop_odp:
                pop_odp_count += 1
                feedback = "poprawnie"
                correct = True
            else:
                feedback = "odpowiedź niepoprawna"
                correct = False
        else:
            feedback = "odpowiedź niepoprawna lub udzielona za wolno"
            correct = False
        
        # Log data to file
        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([liczba_prob, row['Slowo1'], row['Slowo2'], key, correct, rt])

        feedback_stim = visual.TextStim(win, text=feedback, color=(-1, -1, -1))
        feedback_stim.draw()
        win.flip()
        core.wait(2)
        win.flip()
        core.wait(0.8)

    if pop_odp_count < min_pop:
        dodatkowa_instrukcja = (
            "Wydaje się, że miałeś/aś problem z instrukcją. "
            "Jeśli oba słowa są prawdziwymi polskimi słowami, naciśnij na klawiaturze „m”. "
            "Jeśli jeden lub oba słowa są słowami bezsensownymi, naciśnij na klawiaturze „z”."
            "\n\nNaciśnij spację, aby ponownie przeczytać instrukcje."
        )
        display_text(win, dodatkowa_instrukcja)
        for instrukcja in instrukcje:
            display_text(win, instrukcja, bottom_text)

# wlacza sesje treningowa
trening(df, 15, 8)

# eksperymentalna sesja
# eksperymentalna sesja
def eksperymentalna(df, num_trials, music, part):
    if part == 1:
        music.play()
        
    for trial_num, row in df.iterrows():
        if trial_num == num_trials:
            break

        fix = visual.TextStim(win, text='+', color=(-1, -1, -1))
        fix.draw()
        win.flip()
        core.wait(0.8)

        para = f"{row['Slowo1']} \n {row['Slowo2']}"
        word_stim = visual.TextStim(win, text=para, color=(-1, -1, -1), pos=(0.0, 0.0))
        word_stim.draw()
        win.flip()
        
        timer = core.Clock()  # Start the clock
        response = event.waitKeys(maxWait=3, keyList=['m', 'z'], timeStamped=timer)
        
        if response:
            key, rt = response[0]
        else:
            key, rt = None, None

        correct = (key == 'm' and row['Relacja'] == 1) or (key == 'z' and row['Relacja'] == 0)
        print(correct)  # Dodatkowe wyświetlenie wartości correct
        # Log data to file
        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([trial_num, row['Slowo1'], row['Slowo2'], key, correct, rt])

        win.flip()
        core.wait(0.8)

    if part == 2:
        music.stop()

    return None


# wlacz eksperymentalna
display_text(win, "Zaraz rozpocznie się sesja eksperymentalna. Pamiętaj, oceniasz czy zestawy słów są prawdziwe i dla takich klikasz klawisz „m” a dla bezsensowych klikasz klawisz „z”. Odpowiadaj poprawnie i staraj się robić to jak najszybciej.", "Naciśnij spację, aby rozpocząć.")

# czesci sesji eksperymentalnej
display_text(win, "Sesja eksperymentalna - Część 1", "Naciśnij spację, aby rozpocząć")
part1_correct = eksperymentalna(df, 90, muz_bez_slow, part=1)
display_text(win, "Ta część dobiegła końca, to chwila na moment odpoczynku.\nGdy będziesz gotowy/a kliknij spację, by kontynuować")

display_text(win, "Sesja eksperymentalna - Część 2", "Naciśnij spację, aby rozpocząć")
part2_correct = eksperymentalna(df, 90, muz_bez_slow, part=2)
display_text(win, "Ta część dobiegła końca, to chwila na moment odpoczynku.\nGdy będziesz gotowy/a kliknij spację, by kontynuować")

display_text(win, "Sesja eksperymentalna - Część 3", "Naciśnij spację, aby rozpocząć")
part3_correct = eksperymentalna(df, 90, muz_bez_slow, part=2)
display_text(win, "To koniec eksperymentu. Bardzo dziękujemy za wzięcie udziału w naszym badaniu!", "[Naciśnij spację, by wyjść z procedury eksperymentalnej]")

import glob
csv_files = glob.glob('*.{}'.format('csv'))
df_conact = pd.concat([pd.read_csv(f) for f in csv_files ], ignore_index=True)
df_conact

# zamykanie
win.close()
core.quit()