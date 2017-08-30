import numpy as np


def spectrinput(filename):
    infile = open(filename, 'r')
    
    filelist = infile.read().replace("\n", " ").split(" ")
    
    numfreq = int(filelist[6])
    filelist.pop(6)
    
    freqfluxlist = []
  
    for item in filelist:
        try:
            item = np.float64(eval(item))
            if (item < 0): item = 0
            freqfluxlist.append(item)
        except:
            if (item != ''): print(item, type(item))
            continue
    
    print(numfreq)
    print(freqfluxlist[numfreq])
    print(len(freqfluxlist)/2)


    xfreq = np.array(freqfluxlist[0:numfreq])
    yint = np.array(freqfluxlist[numfreq:])
    
    xfreq = (3e3)/xfreq
    yint = (yint)/(3.33e4*xfreq*xfreq)



    swag = np.transpose([xfreq, yint])

    return np.array([item for item in swag if 3800 < item[0] < 7000])

