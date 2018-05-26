import folium
import random
file_name = "data/2018-04-19 18:30:40 Data.txt"


def collect_location(file=file_name):
    f = open(file,"r")
    L = []
    failed = 0
    for line in f:
        str_buffer = line.split(",")
        try:
            L.append((float(str_buffer[3]),float(str_buffer[4])))
        except Exception as e:
            failed += 1
            continue
        
    print(failed)
    return L

def mapping():
    L = collect_location()
    L = random.sample(L,int(0.125*len(L)))
    mapit = folium.Map(location=[39.90469, 116.407173], zoom_start=15 )
    for coord in L:
        folium.Marker( location=[ coord[0], coord[1] ]).add_to(mapit)

    mapit.save('map.html')

def collect_ids(file=file_name):
    f = open(file,"r")
    L = {}
    failed = 0
    for line in f:
        str_buffer = line.split(",")
        try:
            L[str_buffer[0]] = str_buffer[2]
        except Exception as e:
            failed += 1
            continue
        
    print(failed)
    return L
        

if __name__ == "__main__":
    mapping()