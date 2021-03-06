import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
from scipy.signal import chirp
import librosa
import librosa.display
import sounddevice as sd
import time
from scipy.fftpack import fft, ifft
from scipy.signal import fftconvolve, convolve, kaiser

class audio_interface():
    def __init__(self):
        self.fs=96000
    def playrecord(self,signal,fs=96000,channels=1):
        signal=np.concatenate((signal, [0]*int(fs*0.8)), axis=None)
        signal=np.concatenate(([0]*int(fs*0.8),signal), axis=None)
        rec=sd.playrec(signal,fs,channels,blocking=True)
        #time.sleep(3)
        return rec.reshape((signal.shape[0]))




class signal_generator():
    def __init__(self,sr):
        self.sr=sr
        self.signal=[]
    def linsweep(self,w1,w2,T):
        return self._linsweep(self,w1,w2,T)
    def logsweep(self,w1,w2,T):
        return self._logsweep(self,w1,w2,T)
    def sine(self,w,T):
        return self._sine(self,w,T)
    
    
    def plot_signal(self,signal,title,sr=None):
        if sr is None: 
            sr=self.sr
        plt.figure(figsize=(20,5))
        plt.plot(np.array(range(len(signal)))/sr,signal,)
        plt.title(title)
        plt.xlabel('Zeit in s')
        plt.ylabel('Signalstärke')
        plt.show()
    
    
    def plot_spectrum(self,signal,title): 
        def Spectrum(s):
            Ftest=scipy.fftpack.fft(s)
            n=round(s.shape[0]/2)
            xf=np.linspace(0.0,self.sr/2,n)
            return xf,20*np.log10(np.abs(Ftest[0:n]))
        plt.figure(figsize=(20,5))
        plt.plot(*Spectrum(signal))
        plt.title(title)
        plt.xlabel('Frequenz [Hz]')
        plt.ylabel('Amplitude [dB]')
        plt.xscale("log")
        plt.show()
        
    def plot_spectrogram(self,signal,title):
        plt.figure(figsize=(20,5))
        D=np.abs(librosa.stft(signal))
        DB=librosa.amplitude_to_db(D,ref=np.max)
        librosa.display.specshow(DB,sr=self.sr,x_axis="time",y_axis="linear")
        plt.colorbar(format="%+2.0f dB")
        plt.show()
        
    def plot_spec(self,signal,title):
        #plt.figure(figsize=(20,5))
        fig, axs = plt.subplots(1,2,figsize=(20,5))
        
        D=np.abs(librosa.stft(signal))
        DB=librosa.amplitude_to_db(D,ref=np.max)
        librosa.display.specshow(DB,sr=self.sr,x_axis="time",y_axis="linear",ax=axs[0])
        #fig.colorbar(DB,format="%+2.0f dB",ax=axs[0])
        
        def Spectrum(s):
            Ftest=scipy.fftpack.fft(s)
            n=round(s.shape[0]/2)
            xf=np.linspace(0.0,self.sr/2,n)
            return xf,20*np.log10(np.abs(Ftest[0:n]))
        axs[1].plot(*Spectrum(signal))
        plt.title(title)
        axs[1].set_xlabel('Frequenz [Hz]')
        axs[1].set_ylabel('Amplitude [dB]')
        axs[1].set_xscale("log")
        
        plt.show()
        
        
        
    class _linsweep():
        def __init__(self,self_generator,w1,w2,T):
            self.self_generator=self_generator
            T=T*self_generator.sr
            self.w1=w1/self_generator.sr
            self.w2=w2/self_generator.sr
            
            self.signal=np.sin(2*np.pi*(self.w1*np.arange(T)+(((self.w2-self.w1)/T)*np.arange(T)*np.arange(T)/2)))
            #self.signal=chirp(np.arange(T),f0=self.w1,f1=self.w2,t1=T)
            
        def plot_signal(self):
            self.self_generator.plot_signal(self.signal,"lin sine sweep")
        def plot_spectrum(self):
            self.self_generator.plot_spectrum(self.signal,"lin sine sweep - spectrum")
        def plot_spectrogram(self):
            self.self_generator.plot_spectrogram(self.signal,"lin sine sweep - spectrogram")
        def plot_spec(self):
            self.self_generator.plot_spec(self.signal,"lin sine sweep")
            
            
    class _logsweep():
        def __init__(self,self_generator,w1,w2,T):
            self.self_generator=self_generator
            self.T=T*self_generator.sr
            self.w1=w1/self_generator.sr
            self.w2=w2/self_generator.sr
            
            self.signal=np.sin(2*np.pi*self.w1*self.T/np.log(self.w2/self.w1)*(np.exp(np.arange(self.T)/(self.T/np.log(self.w2/self.w1)))-1.0))
        def inverse(self):
            # This is what the value of K will be at the end (in dB):
            kend = 10**((-6*np.log2(self.w2/self.w1))/20)  
            # dB to rational number.
            k = np.log(kend)/self.T

            # Making reverse probe impulse so that convolution will just
            # calculate dot product. Weighting it with exponent to acheive 
            # 6 dB per octave amplitude decrease.
            self.reverse_signal = self.signal[-1::-1] * np.array(list(map(lambda t: np.exp(t*k), np.arange(self.T))))
            Frp =  fft(fftconvolve(self.reverse_signal, self.signal))
            self.reverse_signal /= np.abs(Frp[round(Frp.shape[0]/4)])
            return self.reverse_signal
            
        def plot_signal(self):
            self.self_generator.plot_signal(self.signal,"log sine sweep")
        def plot_spectrum(self):
            self.self_generator.plot_spectrum(self.signal,"log sine sweep - spectrum")
        def plot_spectrogram(self):
            self.self_generator.plot_spectrogram(self.signal,"log sine sweep - spectrogram")
        def plot_spec(self):
            self.self_generator.plot_spec(self.signal,"log sine sweep")
            
    class _sine():
        def __init__(self,self_generator,w,T):
            self.self_generator=self_generator
            T=T*self_generator.sr
            self.w=w/self_generator.sr
            self.signal=np.sin(2*np.pi*np.arange(T)*self.w)
            
        def plot_signal(self):
            self.self_generator.plot_signal(self.signal,"log sine sweep")
        def plot_spectrum(self):
            self.self_generator.plot_spectrum(self.signal,"log sine sweep - spectrum")
        def plot_spectrogram(self):
            self.self_generator.plot_spectrogram(self.signal,"log sine sweep - spectrogram")
        def plot_spec(self):
            self.self_generator.plot_spec(self.signal,"log sine sweep")
 


#https://github.com/baranovmv/RoomResponse/blob/master/measure.py
    