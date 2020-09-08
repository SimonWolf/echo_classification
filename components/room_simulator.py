import pyroomacoustics as pra
import random
import numpy as np
from signal_generator import signal_generator,audio_interface 
from scipy.io import wavfile
from scipy import interpolate
import os

class room_simulator():
    
    room_specs=[
        {
            "roomtype": "toilet",
            "max_room_dim": [2,1.5,3],
            "min_room_dim":[ 1,1,2],
            "wall_materials": [["wooden_door","ceramic_tiles","hard_surface","hard_surface"],
                               ["wooden_door","hard_surface","hard_surface","hard_surface"],
                               ["wooden_door","glass_window","carpet_thin","ceramic_tiles"],
                               ["wooden_door","carpet_thin","ceramic_tiles","hard_surface"],
                               ["wooden_door","glass_window","hard_surface","hard_surface"],
                               ["hard_surface","hard_surface","hard_surface","hard_surface"],],
            "floor_material": ["ceramic_tiles","hard_surface"],
            "ceiling_material": ["hard_surface","smooth_brickwork_flush_pointing"]
        },
        {
            "roomtype": "livingroom",
            "max_room_dim": [7,6,3],
            "min_room_dim":[ 3,2,2],
            "wall_materials": [["curtains_cotton_0.5","blinds_half_open","glass_window","hard_surface"],
                               ["curtains_cotton_0.5","curtains_cotton_0.5","glass_window","wood_1.6cm"],
                               ["wooden_door","glass_window","curtains_cotton_0.5","hard_surface"],],
            "floor_material": ["carpet_thin","carpet_hairy","carpet_tufted_9.5mm","carpet_cotton","chairs_heavy_upholstered"],
            "ceiling_material": ["hard_surface","smooth_brickwork_flush_pointing"]
        },
        {
            "roomtype": "bathroom",
            "max_room_dim": [4,4,3],
            "min_room_dim":[ 3,2,2],
            "wall_materials": [["wooden_door","ceramic_tiles","hard_surface","hard_surface"],
                               ["wooden_door","hard_surface","hard_surface","hard_surface"],
                               ["ceramic_tiles","glass_window","ceramic_tiles","ceramic_tiles"],
                               ["wooden_door","glass_window","ceramic_tiles","hard_surface"],
                               ["wooden_door","glass_window","ceramic_tiles","hard_surface"],
                               ["hard_surface","hard_surface","hard_surface","hard_surface"],],
            "floor_material": ["ceramic_tiles","hard_surface"],
            "ceiling_material": ["hard_surface","smooth_brickwork_flush_pointing"]
        },
        {
            "roomtype": "office",
            "max_room_dim": [4,4,3],
            "min_room_dim":[ 2,2,2],
            "wall_materials": [["curtains_cotton_0.5","blinds_half_open","glass_window","hard_surface"],
                               ["curtains_cotton_0.5","hard_surface","glass_window","wood_1.6cm"],
                               ["wooden_door","glass_window","curtains_cotton_0.5","hard_surface"],],
            "floor_material": ["carpet_thin","hard_surface"],
            "ceiling_material": ["hard_surface","smooth_brickwork_flush_pointing"]
        },
        
        
    ]
    rooms=[]
    
    def __init__(self,N_mutations_per_roomtype=1,sr=96000,roomtype="toilet"):
        roomtypedict={
            "toilet":0,
            "livingroom":1,
            "bathroom":2,
            "office":3
        }
       # print("INIT room simulator:")
        self.rooms=[]
        self.sr=sr
        self.create_rooms(N_mutations_per_roomtype,roomtypedict[roomtype])
        
    def create_rooms(self,N_mutations_per_roomtype,roomtype=0):
        roomtype=self.room_specs[roomtype]
        
        number_rooms=0
            
        for i in range(N_mutations_per_roomtype):
            ################################################################################################
            #random room dimensions
            room_x=(random.randint(roomtype["min_room_dim"][0]*100,roomtype["max_room_dim"][0]*100)/100)
            room_y=(random.randint(roomtype["min_room_dim"][1]*100,roomtype["max_room_dim"][1]*100)/100)
            room_z=(random.randint(roomtype["min_room_dim"][2]*100,roomtype["max_room_dim"][2]*100)/100)
            room_dim=[room_x,room_y,room_z]
            ################################################################################################
            #random materials
            wall_materials=random.choice(roomtype["wall_materials"])
            random.shuffle(wall_materials)
            floor_material=random.choice(roomtype["floor_material"])
            ceiling_material=random.choice(roomtype["ceiling_material"])
            m = pra.make_materials(
                ceiling=ceiling_material,
                floor=floor_material,
                east=wall_materials[0],
                west=wall_materials[1],
                north=wall_materials[2],
                south=wall_materials[3],)
            ################################################################################################
            # create room
            rt60 = 0.5  # seconds
            e_absorption, max_order = pra.inverse_sabine(rt60, room_dim)
            room = pra.ShoeBox(room_dim, fs=self.sr, materials=m, max_order=max_order , air_absorption=True,ray_tracing=False)
            ################################################################################################
            # random mic_positions
            mic_x=(random.randint(0,int(room_x*100))/100)
            mic_y=(random.randint(0,int(room_y*100))/100)
            mic_z=(random.randint(0,int(room_z*100))/100)
            mic_pos=[mic_x,mic_y,mic_z]
            room.add_microphone_array(np.array([mic_pos]).T)
            ################################################################################################
            # add sweep source
            sg=signal_generator(sr=self.sr)
            logsweep=sg.logsweep(w1=100,w2=30000,T=0.3)
            sweep_sourcepos=mic_pos
            if room.is_inside([mic_pos[0],mic_pos[1]+0.1,mic_pos[2]]):
                sweep_sourcepos=[mic_pos[0],mic_pos[1]+0.1,mic_pos[2]]
            else:
                sweep_sourcepos=[mic_pos[0],mic_pos[1]-0.1,mic_pos[2]]
            scaled = np.int16(logsweep.signal/np.max(np.abs(logsweep.signal)) * 32767*0.5)
            room.add_source(sweep_sourcepos, signal=scaled, delay=0.02)
            ################################################################################################
            # add noise source
            fs, audio = wavfile.read("../../data/audio/"+random.choice(os.listdir("../../data/audio/")))
            #fs, audio = wavfile.read("../../data/audio/DevNode1_ex46_154.wav")
            noise_x=(random.randint(0,int(room_x*100))/100)
            noise_y=(random.randint(0,int(room_y*100))/100)
            noise_z=(random.randint(0,int(room_z*100))/100)
            noise_pos=[noise_x,noise_y,noise_z]
            ## Interpolate to higher fps
            duration = audio.shape[0] / fs
            time_old  = np.linspace(0, duration, audio.shape[0])
            time_new  = np.linspace(0, duration, int(audio.shape[0] * 96000 / fs))
            interpolator = interpolate.interp1d(time_old, audio.T)
            audio = interpolator(time_new).T.astype('int16') 
            
            room.add_source(noise_pos, signal=audio.T[0], delay=0.0)
            #room.add_source(noise_pos, signal=np.sin(audio.T[1])*0.01, delay=0.0)
            #room.add_source(noise_pos, signal=np.sin(audio.T[2])*0.01, delay=0.0)
            #room.add_source(noise_pos, signal=np.sin(audio.T[3])*0.01, delay=0.0)
        ################################################################################################
            # store room
            self.rooms.append(room)
            #print("Room "+str(number_rooms)+" created: "+str(room_dim)+" , "+str(wall_materials)+" , "+str(floor_material)+" , "+str(ceiling_material))
            number_rooms+=1