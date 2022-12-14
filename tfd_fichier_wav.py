import numpy as np
import soundfile as sf
import sounddevice as sd
import scipy.signal
from matplotlib import pyplot as plt
import wx

def on_click_module(event, freq, mod_f, type, graphe):
    if event.key == 'shift':
        x, y = event.xdata, event.ydata
        idx = np.argmin(np.abs(freq-x))
        n_min = max(idx - 1000, 0)
        n_max = min(idx + 1000, freq.shape[0])
        idx = np.argmin(np.abs(y - mod_f[n_min : n_max])) + n_min
        if event.inaxes:
            ax = event.inaxes  # the axes instance
            print('Fréquence retenue ', format(freq[idx],'.5e'), "Hz")
            if type == 0:
                print('Module ', format(mod_f[idx], '.4e')," u.a.")
            if type == 1:
                print('Phase ', format(mod_f[idx], '.4e')," u.a.")
    if event.key == 'control' and type == 0:
        x, y = event.xdata, event.ydata
        idx = np.argmin(np.abs(freq-x))
        n_min = max(idx - 1000, 0)
        n_max = min(idx + 1000, freq.shape[0])
        idx = np.argmin(np.abs(y - mod_f[n_min : n_max])) + n_min
        if event.inaxes:
            ax = event.inaxes  # the axes instance
            print('Fréquence retenue ', format(freq[idx],'.5e'), "Hz")
            pos_peak, _ = scipy.signal.find_peaks(mod_f, height=mod_f[idx]/2)
            nb_peak = 0
            for p in pos_peak:                   
                if freq[p] > 0:
                    print('F ', format(freq[p],'.5e'), "Hz",
                          'M ', format(mod_f[p], '.4e')," u.a.")
                    nb_peak = nb_peak + 1
                    if nb_peak>10:
                        print("Number of peaks is greater than 10")
                        print("Stop iterating")
                        break
            if nb_peak <= 10:
                pos = freq[pos_peak] > 0
                graphe[0].plot(freq[pos_peak[pos]], mod_f[pos_peak[pos]], "x")
                graphe[1].canvas.draw()
                

my_app = wx.App()
nom_fichier_son = wx.FileSelector("Fichier son",wildcard="*.wav")
son , Fe = sf.read(nom_fichier_son)
del my_app
N = son.shape[0]
print("Nombre d'échantillons : ", N)
print("Fréquence d'échantillonnage : ", Fe)
S = np.fft.fft(son, axis=0)
if len(son.shape) == 1:
    nb_courbe = 1
else:
    print("Son stéréophonique")
    print("Voulez vous conserver la voie 0, 1 ou garder les deux?")
    l_choix = ["0", "1", "2"]
    while choix not in l_choix:
        choix = input("Votre choix 0, 1 ou 2")
    match choix:
        case "0":
            print("Extraction de la voie 0 pour analyse")
            son = son[:,0]
        case "1":
            print("Extraction de la voie 1 pour analyse")
            son = son[:,1]
        case _:
            print("Analyse des deux voies")
print("Nombre de voies : ", nb_courbe)
# Tracer du signal temporel
fig1, ax1 = plt.subplots(nrows=1, ncols=nb_courbe)
fig2, ax2 = plt.subplots(nrows=1, ncols=nb_courbe)
fig3, ax3 = plt.subplots(nrows=1, ncols=nb_courbe)
te = np.arange(0,N)/Fe
freq = np.fft.fftfreq(N)*Fe
for idx_voie in range(0,nb_courbe):
    if nb_courbe == 1:
        graphe1 = ax1
        graphe2 = ax2
        graphe3 = ax3
        y = son
        Y = S
    else:
        graphe1 = ax1[idx_voie]
        graphe2 = ax2[idx_voie]
        graphe3 = ax3[idx_voie]
        y = son[:, idx_voie]
        Y = S[:, idx_voie]
    graphe1.plot(te,y,label='Voie ' + str(idx_voie))
    if idx_voie == 0:
        graphe1.set(title=nom_fichier_son)
    graphe1.grid(True)
    graphe1.set(xlabel='Time (s)', ylabel=' y (u.a.)')
    graphe1.legend()
    plt.pause(0.1)
# Tracer du module du spectre de la TFD du signal temporel
    plt.figure(2)
    val_freq = np.fft.fftshift(freq)
    val_mod = np.fft.fftshift(np.abs(Y).real/Fe)
    graphe2.plot(val_freq,
                 val_mod,
                 marker='.',
                 label='Voie ' + str(idx_voie))
    if idx_voie == 0:
        graphe2.set(title='Module de la T.F.D.')
    graphe2.legend()
    graphe2.grid(True)
    graphe2.set(xlabel='Fréquence (Hz)',ylabel='Amplitude (u.a.)')
# Tracer de la phase du spectre de la TFD du signal temporel
    plt.figure(3)
    val_angle = np.fft.fftshift(np.angle(Y))
    graphe3.plot(val_freq,
                 val_angle,
                 marker='.',
                 label='Voie ' + str(idx_voie))
    if idx_voie == 0:
        graphe3.set(title='Phase de la T.F.D.')
    graphe3.legend()
    graphe3.grid(True)
    graphe3.set(xlabel='Fréquence (Hz)',ylabel='Phase (rd)')
    module_mouse =  lambda event: on_click_module(event, val_freq, val_mod,0, (graphe2, fig2))
    fig2.canvas.mpl_connect('button_press_event', module_mouse)
    phase_mouse =  lambda event: on_click_module(event, val_freq, val_angle,1, (graphe3,fig3))
    fig3.canvas.mpl_connect('button_press_event', phase_mouse)

plt.show()
