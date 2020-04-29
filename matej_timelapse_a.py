#!/usr/bin/env python
#
# run in console
# sudo python /your/file/location/raspiLapseCam.py (add &) if you wish to run as a
# background task. A process ID will be shown which can be ended with

# sudo kill XXXX (XXXX = process number)

# to schedule run at system startup run console nano crontab -e (set time interval within the code)
# @reboot /usr/bin/python /home/pi/matej_timelapse.py

# Import some frameworks
import os
import time
import RPi.GPIO as GPIO
import logging
import datetime
import subprocess
import os.path
import re


# Grab the current datetime which will be used to generate dynamic folder names
from os import path
d = datetime.datetime.now()
initYear = "%04d" % (d.year) 
initMonth = "%02d" % (d.month)
initDate = "%02d" % (d.day)
initHour = "%02d" % (d.hour)
initMins = "%02d" % (d.minute)

#config
dateToday = datetime.date.today()
dateIsYesterday = datetime.date.today()
createMovie = 0
uploadToYoutube = 0
compression = 0
logExport = 0
logStart = ""
logEnd = ""
wCounter = 1
imgWidth = 3280 # Max = 3280 
imgHeight = 2464 # Max = 2464
imgParameters = "-sh 100 -q 100 -v -ev -3 -vf -hf -awb off -awbg 1.6,1.7 -mm average -n"

# Define the location where you wish to save files. 
# If you run a local web server on Apache you could set this to /var/www/ to make them 
# accessible via web browser.

folderToSave = "/home/pi/camera/" + str(initYear) + str(initMonth) + str(initDate) +"_"+ str(initHour) + str(initMins)
if path.isdir("/home/pi/camera/") is False :
    os.mkdir("/home/pi/camera/")
if path.isdir(folderToSave) is False :
    os.mkdir(folderToSave)

# Set up a log file to store activities for any checks.
logging.basicConfig(filename=str(folderToSave) + ".log",level=logging.DEBUG)
logging.debug(" Ultimate RaspiLapse -- Started Log for " + str(folderToSave))
logging.debug(" Logging session started at: "+ str(d))
logStart = str(d)

# Run a WHILE Loop of infinitely
while True:
    
    d = datetime.datetime.now()
#    
    dateToday = datetime.date.today()
    if dateToday == dateIsYesterday:
# change if you want program to end on certain hour h-format 
# (without leading zeroes) if you want indefinite loop type if d.hour < 99 
# or to if d.hour >= 7 and d.hour < 9 if you want to run it between time range
    
        if d.minute >= 0 and d.minute < 50 : 
            
            # Capture the CURRENT time (not start time as set above) to insert into each capture image filename
            hour = "%02d" % (d.hour)
            mins = "%02d" % (d.minute)
            second = "%02d" % (d.second)
            fileName = str(initYear) + "-" + str(initMonth) + "-" + str(initDate) + "_" + str(hour) + "-" + str(mins) + "-" + str(second)


            print (" ====================================== Saving file at " + hour + ":" + mins + ":" + second)
            
            # Capture the image using raspistill. Set to capture with added sharpening, auto white balance and average metering mode witout preview on screen
            if wCounter <=9 :
                os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(folderToSave) + "/" + str(fileName) + ".jpg " + str(imgParameters))
                
            # Write out to log file
                logging.debug(' Full-res image saved: ' + str(folderToSave) + "/" + str(fileName) )
                wCounter += 1
                print("wCounter: "+str(wCounter))
            else :
                #
                os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(folderToSave) + "/" + str(fileName) + ".jpg " + str(imgParameters))
                logging.debug(' Full-res image saved: ' + str(folderToSave) + "/" + str(fileName) )
                # create webpage image_shot every 10th image (webpage 5min refresh image)
                if path.isdir("/home/pi/camera/www/") is False :
                    os.mkdir("/home/pi/camera/www/")
                    logging.debug(' Folder created: /home/pi/camera/www/')

                os.system("ffmpeg -i "+str(folderToSave) + "/" + str(fileName)+".jpg -vf scale="+str(imgWidth)+":"+ str(imgHeight) +" /home/pi/camera/www/latest_image.jpg -y")
                logging.debug(' Compressed image saved to www: /home/pi/camera/www/latest_image.jpg (UPDATED)' )
                #
                if path.isdir(str(folderToSave)+"/www_alltime/") is False :
                    os.mkdir(str(folderToSave)+"/www_alltime/")
                    logging.debug(' Folder created: ' + str(folderToSave)+"/www_alltime/")
                os.system("ffmpeg -i "+str(folderToSave) + "/" + str(fileName)+".jpg -vf scale="+str(imgWidth)+":"+ str(imgHeight) +" "+str(folderToSave)+"/www_alltime/"+ str(fileName) +".jpg -y")
                logging.debug(' Compressed image saved: ' + str(folderToSave) + "/" + str(fileName))
                wCounter = 1

            
        # Wait x+5 seconds before next capture (+5sec goes because raspistill workflow for focusing, taking and saving a shot takes 5-5.5sec)
            time.sleep(2)
            createMovie = 1
        else:
            # create timelapse
            if createMovie == 1 :
                print (" ====================================== Sleeping (10)")
                time.sleep(2) #change to 10
                print (" ====================================== Exporting .JPGs to timelapse")
                if path.isdir(str(folderToSave) + "/export") is False :
                    os.mkdir(str(folderToSave) + "/export")
                    logging.debug(' Folder created: ' + str(folderToSave) + "/export")
                os.system("ffmpeg -framerate 30 -pattern_type glob -i '"+ str(folderToSave) +"/*.jpg' " + str(folderToSave) + "/export/"+ str(fileName) +".mp4")
                logging.debug(' Timelapse created: ' + str(folderToSave) + "/export/" + str(fileName) )
                createMovie = 0
                uploadToYoutube = 1
                compression = 1 #delete line
            #upload to youtube
#             if uploadToYoutube == 1 :
#                 print (" ====================================== Sleeping (10)")
#                 time.sleep(10)
#                 print (" ====================================== Uploading video to Youtube.com")
#                 os.system("youtube-upload --title='" + str(fileName) + "' --client-secrets=cs.json --playlist='timelapse' --embeddable=True "+ str(folderToSave) + "/export/" + str(fileName) +".mp4")
#                 logging.debug(' Video auto uploaded to youtube: ' + str(folderToSave) + "/export/" + str(fileName) )
#                 uploadToYoutube = 0
#                 compression = 1
             #resizing
            
            if compression == 1:
              def get_size(start_path = str(folderToSave)):
                 total_size = 0
                 for dirpath, dirnames, filenames in os.walk(start_path):
                     for f in filenames:
                         fp = os.path.join(dirpath, f)
                         # skip if it is symbolic link
                         if not os.path.islink(fp):
                             total_size += os.path.getsize(fp)

                 return total_size
              #
              path, dirs, files = next(os.walk(str(folderToSave)))
              fileCount = len(files)
              print(str(fileCount))
              logging.debug(' '+str(fileCount)+' photos recorded during the session. ')
              folderSizeGB = round(get_size()/1024/1024/1024,3)
              folderSizeMB = round(get_size()/1024/1024,1)
              print(str(folderSizeGB)+" GB / "+str(folderSizeMB)+" MB")
              logging.debug(' Total size before compression: ' +  str(folderSizeGB) + " GB / "+  str(folderSizeMB) + " MB")
              photos = os.listdir(str(folderToSave))
              for photo in photos:
                  os.system('ffmpeg -i '+str(folderToSave)+'/'+photo+' -vf scale=3280:2464 '+str(folderToSave)+'/'+photo+' -y')
              #
              path, dirs, files = next(os.walk(str(folderToSave)))
              fileCount = len(files)
              print(str(fileCount))
              logging.debug(' '+str(fileCount)+' photos after compression.  ')
              
              folderSizeGB = round(get_size()/1024/1024/1024,3)
              folderSizeMB = round(get_size()/1024/1024,1)
              print(str(folderSizeGB)+" GB / "+str(folderSizeMB)+" MB")
              logging.debug(' Total size after compression: ' +  str(folderSizeGB) + " GB / "+  str(folderSizeMB) + " MB")
              compression = 0
              logging.debug(' Logging session ended at: '+ str(d))
              logEnd = str(d)
              logExport = 1

            

            if logExport == 1 :
                # logging - config
                log_file_path = str(folderToSave) + ".log"
                from os import path #reset path (changed for counting files)
                if path.isdir("/home/pi/camera/www/logs/") is False :
                    os.mkdir("/home/pi/camera/www/logs/")
                export_file_path = "/home/pi/camera/www/logs/"
                file = str(logStart)+"-"+str(logEnd)+"_export.txt"
                export_file = export_file_path + file
                regex = logStart
                # read from log
                with open(log_file_path, "r") as file:
                    match_list = []
                    signal1 = 0
                    for line in file:
                        if signal1 == 0 :
                            for match in re.finditer(regex, line, re.S):
                                match_text = match.group()
                                if match_text == match.group():
                                    signal1 =1
                        else :
                            match_list.append(line)    
                            
                    file.close()
                    print("Logs cached.")
                    #write
                    with open(export_file, "w+") as file:
                        file.write("EXPORTED DATA: "+str(logStart)+"-"+str(logEnd)+"\n")
                       
                        for item in range(0, len(match_list)):
                            file.write(str(match_list[item]))
                    file.close()
                    print("Logs exported.")
                    logExport = 0
            
    else:
# this part is used when script is run overnight (date change) and enforce saving images to different folder every day        
# reinit day        
        d = datetime.datetime.now()
        initYear = "%04d" % (d.year) 
        initMonth = "%02d" % (d.month)
        initDate = "%02d" % (d.day)
        initHour = "%02d" % (d.hour)
        initMins = "%02d" % (d.minute)
# config
        from os import path
        dateToday = datetime.date.today()
        dateIsYesterday = datetime.date.today()
        createMovie = 0
        uploadToYoutube = 0
        compression = 0
        logExport = 0
        logStart = ""
        logEnd = ""
        wCounter = 1
        imgWidth = 3280 # Max = 3280 
        imgHeight = 2464 # Max = 2464
        imgParameters = "-sh 100 -q 100 -v -ev -3 -vf -hf -awb off -awbg 1.6,1.7 -mm average -n"


# reinit folder
        folderToSave = "/home/pi/camera/" + str(initYear) + str(initMonth) + str(initDate) + str(initHour) + str(initMins)
        if path.isdir("/home/pi/camera/") is False :
            os.mkdir("/home/pi/camera/")
        if path.isdir(folderToSave) is False :
            os.mkdir(folderToSave)

# reinit logging (same file)
        logging.basicConfig(filename=str(folderToSave) + ".log",level=logging.DEBUG)
        logging.debug(" Ultimate RaspiLapse -- Started Log for " + str(folderToSave))
        logging.debug(" Logging session started at: "+ str(d))
        logStart = str(d)

