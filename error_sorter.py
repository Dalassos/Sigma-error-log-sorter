# coding=utf-8
import os
from datetime import datetime
import builtins
import xml.etree.ElementTree as ET
import csv
import threading
import shutil
import tkinter as tk
from tkinter import filedialog

#____________________________________________



#functions
def login(text):
    global log
    log.writelines(str(text)+"\r")
    print(text)

def clean_date_to_folder(date):
    l = date.split("/")
    cleaned = l[2]+"-"+l[1]+"-"+l[0]
    return cleaned
    
def startNewLog(outdir, outCsv, newErrors, logNb, logLength):
    maxLength = 1048000
    #maxLength = 10
    login("----------------\nCheck if new log required")
    login("outdir, outCsv, newErrors, logNb, logLength :"+str(outdir)+", "+str(outCsv)+", "+str(newErrors)+", "+str(logNb)+", "+str(logLength))
    
    newLog = outCsv.replace(".csv",str(logNb)+".csv")
    login("newLog :"+newLog)

    if logLength > maxLength:
        if logNb > 0:
            newErrors.close()
        else:
            src = outCsv
            dst = newLog
            shutil.copyfile(src,dst)
        logNb += 1
        newLog = outCsv.replace(".csv",str(logNb)+".csv")    
        init_scan_rslt(outdir,newLog)
        newErrors = open(newLog,"a")
        logLength = 0
        login("New log started : #"+str(logNb))
       
    if isinstance(newErrors, str):
        login("newErrors is a string, initialising it as open file")
        
        newErrors = open(newLog,"a")
        login("Log reopened : #"+str(logNb))
    
    login("logNb, logLength, newErrors :"+str(logNb)+", "+str(logLength)+", "+str(newErrors))  
    return logNb, logLength, newErrors

def create_dir(dirName):
    login("---------------\nCreate output directory :"+str(dirName))
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        login("Directory " + dirName +  " Created ")
    else:    
        login("Directory " + dirName +  " already exists")
    login("--------------------------------\n")
    
def checkErrLog():
    login ("testing file chosen")
    test = False
    if 'errorFile' in globals(): 
        test = True
    login(test)
    return test
    
def out_dir(dirName):
    dirName = os.path.normpath(rootdir).split(os.path.sep)
    dirName = dirName[len(dirName)-1]
    login("dirName is "+dirName)
    create_dir(dirName)
    return dirName

def dict_to_csv(dictionnary,reportName,outdir):
        login("writing report from dictionnary "+str(dictionnary))
        report = open(os.path.join(outdir, reportName),"w")
        report.write("Value,Occurence\n") 
        for key, value in dictionnary.items():
            login("writing value")
            report.write("%s,%s\n" % (key, value)) 
        report.close()
        login("finished writing "+reportName)

def filter(outdir, log, value):
    login("starting filtering for :")
    
    name = str(value[0])
    login("filter name is :"+name)
    
    outdirFlt = os.path.join(outdir, name+"_filter")
    create_dir(outdirFlt) 
    login("outdirFlt is :"+outdirFlt)
    
    outFile = os.path.join(outdirFlt, name+"_AllErrors.csv")
    login("outFile is :"+outFile)   
    
    try:    
        open(os.path.join(outdir, log),"r").close()
        open(outFile,"w").close()
    except:
        err = "Could not open list files, make sure it exist and is not already in use by another program"
        login(err)
    else:
        almLog = open(os.path.join(outdir, log),"r")
        login("opened error logs: "+str(almLog))
        output = open(outFile,"w")
        list_heading = ("Date,Time,OS,Priority,Fault\r")
        output.write(list_heading)
        line = almLog.readline()
        login("reading line : "+line)
        line = almLog.readline()
        login("reading line : "+line)
        #errDate, errTime, errOS, errPriority, errFault = (" "," "," "," "," ")
          
        errTotal, logLength, logNb = 0, 0, 0
        humanReadLog = " "

        while (line):
            login("reading line : "+line)
            list = line.split(",")
            errFault = list[4]
            login("errFault is: "+errFault)
          
            for a in value:
                a = str(a)
                if (errFault.find(a) >= 0):
                    output.write(line)
                    errTotal += 1
                    
                    if logNb > 0:
                        humanReadLog.writelines(line)
                    logLength +=1
                    logNb, logLength, humanReadLog = startNewLog(outdirFlt, outFile, humanReadLog, logNb, logLength)  
                    
            
            login("finished loop, reading new line")   
            line = almLog.readline()
            
        if logNb > 0:
            humanReadLog.close()
            
        output.close() 
        
        errTotFile = os.path.join(outdirFlt,name+"_error_total.txt")
        try:
            open(errTotFile,"w").close()
        except:
            err = "Could not open list files, make sure it is not already in use by another program"
            login(err)
        else:
            with open(errTotFile, 'w') as a:
                a.write("Found a total of "+str(errTotal)+" fault alarms")
                a.close()
                
        login('Filter complete')
                
def create_sorted_reports(outdir,outName,valueName):
    login("----------------------------------------\nsorting reports started")
    dateReportName = valueName+"_date_Report.csv"
    OSReportName = valueName+"_OS_Report.csv"
    try:
        mainpath = os.path.join(outdir, outName)
        login("mainpath is :"+mainpath)
        open(mainpath,"r").close()
        login("filtered alarm file ok")
        open(os.path.join(outdir, dateReportName),"w").close()   
        open(os.path.join(outdir, OSReportName),"w").close() 
        login("raw files ok")
        
    except:
        err = "Could not open list files, make sure it exist and is not already in use by another program"
        login(err)
    else:
        allErrors = open(os.path.join(outdir, outName),"r")
        login("opened error logs: "+str(allErrors))
        
        dictOS = {}
        dictDate = {}
        
        line = allErrors.readline()
        login("reading line : "+line)
        line = allErrors.readline()
        login("reading line : "+line)
        #errDate, errTime, errOS, errPriority, errFault = (" "," "," "," "," ")

        while (line):
            login("reading line : "+line)
            list = line.split(",")
            errDate = list[0]
            errOS = list[2]
            errFault = list[4]
            login("errDate is: "+errDate+" and errOS is: "+errOS)
            login("errFault is: "+errFault)
            
            if errDate in dictDate:
                dictDate[errDate] = (dictDate[errDate]+1)
                login("errDate present, counting "+str(dictDate[errDate]))
            else:
                #create_dir(os.path.join(outdir,clean_date_to_folder(errDate)))
                dictDate[errDate] = 1
                login("errDate not present, added")
                
            if errOS in dictOS:
                dictOS[errOS] = (dictOS[errOS]+1)
                login("errOS present, counting "+str(dictOS[errOS]))
            else:
                dictOS[errOS] = 1
                login("errOS not present, added")
            
            login("finished loop, reading new line")   
            line = allErrors.readline()

        allErrors.close() 

        
        login('Sort complete')
        login("----------------------------------------------------------\rDictDate is:"+str(dictDate)+"----------------------------------------------------------\r")
        login("DictOS is:"+str(dictOS)+"----------------------------------------------------------\n")
        
        dict_to_csv(dictDate,dateReportName,outdir)
        dict_to_csv(dictOS,OSReportName,outdir)
        login("reports created----------------------------------------------------------\n")

def init_scan_rslt(outdir, outCsv):
    login("---------------------------------\nInitialising csv output file")
    create_dir(outdir)
    try:
        open(outCsv,"w").close()                  
    except:
        err = "Could not open list files, make sure it is not already in use by another program"
        login(err)
    else:
        allErrors = open(outCsv,"w")
        list_heading = ("Date,Time,OS,Priority,Fault\r")
        allErrors.write(list_heading)
        allErrors.close()
    login("Scan results csv initialised\n----------------------------------------------------------------")
 
def scan(errLog, outdir, outCsv, errTotal, logLength, logNb):

    try:
        open(outCsv,"a").close() 
        #open(errLog,"r").close()         
    except:
        err = "Could not open list files, make sure it is not already in use by another program"
        login(err)
    else:
        login("test ok")
        allErrors = open(outCsv,"a")
        humanReadLog = ""
            
        line = errLog.readline()
        errDate, errTime, errOS, errPriority, errFault = (" "," "," "," "," ")
        errorStarted = False
        errorLogStep = False
        while (line):
            login("reading line : "+line)
            if line.startswith("****************************************************************************"):
                errorLogStep = True
                errorStarted = False
                login("error reading complete")
            elif line.startswith("****"):
                errorStarted = True
                login("error Logs started")

            if errorStarted:
                login("extracting of error")
                if (line.find("Priority") >= 0):
                    login("priority found : "+str(line.find("Priority")))
                    try:
                        line = line.split("Priority ")[1]
                    except:
                        err = "Could not read error"
                        login(err)
                    else:
                        list = line.split("****")
                        errPriority = list[0].replace("\n","")
                        login("errPriority is "+errPriority)
                    
                        try:
                            line = list[1].split("on ")[1]
                        except:
                            err = "Could not read error"
                            login(err)
                        else:
                            list = line.split(" at ")
                            errDate = list[0].replace("\n","")
                            login("errDate is "+errDate)
                            try:
                                errTime = list[1].replace("\n","")
                            except:
                                err = "Could not read error"
                                login(err)
                            else:
                                login("errTime is "+errTime)
                else:
                    errFault = line.replace(",","")
                    login("errFault is "+errFault)
                    if (line.find("Default System Message")>= 0):
                        login("Default System Message")
                        errOS = "Default"
                    elif (line.find("Node")>= 0):
                        list = line.split("Node")
                        login("Node found, "+str(list))
                        errOS = list[1].strip().split(" ")[0].replace("\n","")
                    elif (line.find(":")>= 0):
                        list = line.split(":")
                        login(": found, "+str(list))
                        errOS = list[0].strip().split(" ")[-1].replace("\n","")
                    elif (line.find(",")>= 0):
                        list = line.split(",")
                        login(", found, "+str(list))
                        errOS = list[0].strip().split(" ")[-1].replace("\n","")
                    elif (line.find("Controller")>= 0):
                        list = line.split("Controller")
                        login("Controller found, "+str(list))
                        errOS = list[1].strip().split(" ")[0].replace("\n","")
                    elif (line.find("controller")>= 0):
                        list = line.split("controller")
                        login("Controller found, "+str(list))
                        errOS = list[1].strip().split(" ")[0].replace("\n","")
                    else:
                        login("No OS found")
                        errOS = "n/a"
                    login("errOS is "+errOS)                       
                    
            if errorLogStep:
                logStr = (errDate+","+errTime+","+errOS+","+errPriority+","+errFault)
                allErrors.writelines(logStr)
                login("error fully logged, logStr is "+logStr)
                errTotal += 1                    
                login("errTotal, logLength :"+str(errTotal)+", "+str(logLength))
                logNb, logLength, humanReadLog = startNewLog(outdir, outCsv, humanReadLog, logNb, logLength) 
                login("errTotal, logLength, humanReadLog :"+str(errTotal)+", "+str(logLength)+", "+str(humanReadLog))                     
                
                if logNb > 0:
                    humanReadLog.writelines(logStr)
                logLength +=1
    
                errorLogStep = False   
                
            login("finished loop, reading new line")   
            line = errLog.readline()

        allErrors.close() 
        if logNb > 0:
            humanReadLog.close()
                
        login("Scan complete, found "+str(errTotal)+" errors, Log number: "+str(logNb)+", "+str(logLength)+" errors in this log file")
        return errTotal, logLength, logNb
      
def sort(outdir, outName, outSuffix, value):
    login("----------------------------------------------------------\r\rStarting to sort")
    create_sorted_reports(outdir,outName,"")
                
    #sort filtered
    for a in value:
        valueName = str(a[0])
        login("filtering for :"+valueName)
        
        outdirFlt = os.path.join(outdir, valueName+"_filter")
        create_dir(outdirFlt) 
        login("outdirFlt is :"+outdirFlt)
        filteredLog = valueName+outSuffix
        login("Filtered log path is :"+filteredLog)

        create_sorted_reports(outdirFlt,filteredLog,valueName)  
     
   
#____________________________________________
#GUI functions

def cancel():
    log.close()
    quit()

def execute():
    
    startTime = datetime.now()
    login("Started on :"+str(startTime))

    outPath = "_ScanResults"
    outSuffix = "_AllErrors.csv"
    outName = "scan"+outSuffix
    #outFolder = os.path.basename(errLog.name).split(".")[0]+outPath
    outFolder = str(startTime).replace(":","").replace(" ","").replace("-","").replace(".","")+outPath
    login(outFolder)
    outdir = os.path.join(out_dir(rootdir),outFolder)
    login(outdir)
    
    humanReadLog = ""
    
    if checkErrLog() is True:
        outCsv = os.path.join(outdir, outName)
        init_scan_rslt(outdir, outCsv)
        errTotal, logLength, logNb = 0, 0, 0
        login("errTotal, logLength, logNb = "+str(errTotal)+" "+str(logLength)+" "+str(logNb))
        for a in errorFile:
            errLog = a
            errTotal, logLength, logNb = scan(errLog,outdir,outCsv, errTotal, logLength, logNb)
            a.close()
                    
        filters = ["reset","Reset","RESET"]
        filter(outdir, outName, filters)
        sort(outdir, outName, outSuffix, [filters])
        
        endTime = datetime.now()
        duration = endTime - startTime
        login("Finished on :"+str(endTime)+", duration was :"+str(duration))
        
        errTotFile = os.path.join(outdir,"error_total.txt")
        try:
            open(errTotFile,"w").close()
        except:
            err = "Could not open list files, make sure it is not already in use by another program"
            login(err)
        else:
            with open(errTotFile, 'w') as a:
                a.write("Found a total of "+str(errTotal)+" fault alarms")
                a.close()
            
    else:
        login("No error log selected")
         
def init_gui():
    #Tkinter GUI
    root = tk.Tk()
    root.title("Sigma error log analyser")
    root.minsize(400,100)
    root.geometry("480x100")
    
    # create the main sections of the layout, 
    # and lay them out
    top = tk.Frame(root)
    bottom = tk.Frame(root)
    top.pack(side=tk.TOP)
    bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # create the widgets for the top part of the GUI,
    # and lay them out
    s = tk.Button(root, text="Select", width=10, height=2, command=select)
    c = tk.Button(root, text="Leave", width=10, height=2, command=cancel)
    e = tk.Button(root, text="Scan & Sort", wraplength=60, width=10, height=2, command=execute)
    s.pack(in_=top, side=tk.LEFT)
    e.pack(in_=top, side=tk.LEFT)
    c.pack(in_=top, side=tk.LEFT)

    # create the widgets for the bottom part of the GUI,
    # and lay them out
    global path
    path = tk.Label(root, text = "...", width=35, height=15)
    path.pack(in_=bottom, side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    w = tk.Label(root, text="Please choose error log file")
    w.pack()

    return root
    
def select():
    global errorFile
    print ("Please choose error file")
    almLog =  filedialog.askopenfiles(mode='r')
    #root.filename = filedialog.askopenfile(mode='r')
    errorFile = almLog
    login("errorFile is :"+str(errorFile))
    
#____________________________________________________________
#main code
global outdir
rootdir = ""    
log = open("log.txt","w")
    
root = init_gui()
root.mainloop()

