#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2022 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# we need to import python modules from the $SUMO_HOME/tools directory
# ORTAM DEĞİŞKENLERİNDEN SUMO KONTROL EDİLİYOR VE İÇE AKTARILIYOR
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

 #Rota dosyası oluşturma 
def generate_routefile():
    # RANDOM FONKSİYONUNU BELİRLİ BİR DEĞERE SABİTLEDİK . Random üreticiden hep aynı değerleri alabilmek için 
    #random.seed(1)  # make tests reproducible  
    # 3600 sn için ROU DOSYASI OLUŞTURULACAK
    N = 3600  # number of time steps  
    
    # demand per second from different directions
    # YOLLAR İÇİN ÜRETİLECEK ARAÇ YOĞUNLUĞUNU BELİRLEME
    pWE = 1. / 10  # 0.1
    pEW = 1. / 11  # 0.09
    pNS = 1. / 30  # pNS = 0.03  Her zaman diliminde north yolu için üretilecek olan random sayı pNS değerinden küçükse bu yol için araç üretilir. 
    
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />""", file=routes)
        vehNr = 0
        vehNr_pWE = 0
        vehNr_pEW = 0
        vehNr_pNS = 0
# her zaman dilimi için her yola random sayı üreterek yolun yoğunluk değerlerine göre araç üretme gerçekleştirilir
# random üretici yukarda sabitlediğimizden dolayı uniform dan hep aynı değerleri alırız.        
        for i in range(N): 
            if random.uniform(0, 1) < pWE:  
                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                vehNr_pWE +=1
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
                vehNr_pEW +=1
            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
                vehNr_pNS += 1
                
        print("</routes>", file=routes)
        print("\n--------> Toplam üretilen araç sayısı:",vehNr)
        print("pwe : ",vehNr_pWE)
        print("pew : ",vehNr_pEW)
        print("pns : ",vehNr_pNS)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="31" state="GrGr"/>  # 0.faz 
#        <phase duration="6"  state="yryr"/>  # 1.faz
#        <phase duration="31" state="rGrG"/>  # 2.faz
#        <phase duration="6"  state="ryry"/>  # 3.faz
#    </tlLogic>

def run():
    """execute the TraCI control loop"""
    step = 0
    # we start with phase 2 where EW has green
    traci.trafficlight.setPhase("0", 2) # 0. id ye sahip trafik ışığında 2. faz ile başlatılır.
    while traci.simulation.getMinExpectedNumber() > 0: # aktif ve üretilcek araç sayısı var olduğu sürece simülasyon çalışmaya devam eder.
        traci.simulationStep(step=0)  
        if traci.trafficlight.getPhase("0") == 2: 
            # we are not already switching
            # 0.id li dedöktör tetiklendiğinde faz 3 olarak değiştirilir.
            if traci.inductionloop.getLastStepVehicleNumber("0") > 0: 
                # there is a vehicle from the north, switch
                # Eğer kuzeyden araç gelirse faz 3 çalıştırılır.Faz 3 ün süresi bitince faz 0 çalışır ve yeşil yanar kuzey yolunda 
                traci.trafficlight.setPhase("0", 3)
            else:
                # kuzeyden araç gelmediği süre boyunca faz 2 de tutulur.
                # otherwise try to keep green for EW
                traci.trafficlight.setPhase("0", 2)
                
        step += 1
    
    traci.close() 
    sys.stdout.flush() #arabellete bulunan bilgiler temizlenir.


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options



if __name__ == "__main__":
    options = get_options()

    # SUMO yu SUNUCU OLARAK BAŞLATIYORUZ
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    
    else:
        sumoBinary = checkBinary('sumo-gui')


    # first, generate the route file for this simulation
    generate_routefile()
   
    # İSTEMCİ TRACI Yİ BAŞLATIYORUZ
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    
    run()
