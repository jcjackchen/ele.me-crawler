import folium
import random
import csv

# file_name = "data/2018-04-19 18:30:40 Data.txt"
file_name1 = "Beijing/split1.txt"
file_name2 = "Shanghai/Shanghai_1.csv"
resume_file = "Beijing/2018-05-29 09:57:31 Log"
split_file = "Beijing/split"


def collect_location(file=file_name1):
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

def collect_ids(file=file_name1,resume=False,city="Beijing"):

    position = 1

    if city == "Beijing":
        file = file_name1
        position = 1
    if city == "Shanghai":
        file = file_name2
        position = 2


    print("City: "+city)

    f = open(file,"r")
    L = {}
    failed = 0
    for line in f:
        str_buffer = line.split(",")
        try:
            name = str_buffer[position].rstrip()
            if city == "Shanghai":
                name = str_buffer[position].rstrip().decode(encoding="gbk").encode(encoding="utf-8")

            L[int(str_buffer[0])] = name
        except Exception as e:
            failed += 1
            continue

    done = []
    if resume:
        f = open(resume_file,"r")
        for line in f:
            if "id=" in line:
                i = line.index("=") + 1
                done.append(int(line[i:]))
                
    count = 0
    for d in done:
        if d in L:
            L.pop(d)
            count += 1

    assert(count == len(done))
    print("Data failed to convert: " + str(failed))
    print("Current restaurant to operate: " + str(len(L)))
    return L


def data_divide(save_file=split_file,number=4):
    L = collect_ids();
    count = 0.25 * len(L)
    split = 0
    f = open(save_file+str(split)+ ".txt","w")
    number_count = 0

    for l in L:
        if count <= 0:
            split += 1
            count = 0.25 * len(L)
            f = open(save_file+str(split)+ ".txt","w")

        string = str(l) + "," + L[l] + "\n" 
        f.write(string)
        f.flush
        count -= 1
        number_count += 1

    assert(number_count == len(L))

if __name__ == "__main__":
    collect_ids(city="Shanghai")
    # mapping()
    # data_divide()