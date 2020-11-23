from timecode import Timecode
#from typing import List
import re
from tkinter import filedialog
from tkinter import *
import csv
import pandas as pd
import xml.etree.ElementTree as ET
import configparser
from collections import defaultdict
from collections import OrderedDict
from operator import itemgetter
from itertools import product
import os
fps = 23.976

ui = fu.UIManager
disp = bmd.UIDispatcher(ui)
from python_get_resolve import GetResolve
resolve = GetResolve()
project = resolve.GetProjectManager().GetCurrentProject()
mediapool = project.GetMediaPool()
bin = mediapool.GetCurrentFolder()
Clips = bin.GetClipList()
if not project:
    print("No project is loaded")
    sys.exit()

status_text = ""
Frames_toggle = True
Folder_Name = ""
MetadataList = []
object_List = []
ScriptEMetadataList = []


###About Dialog Window
def AboutWindow():
    width, height = 500, 250
    win = disp.AddWindow(
        {"ID": "AboutWin", "WindowTitle": 'About Dialog', "WindowFlags": "{Window = true, WindowStaysOnTopHint = true}",
         "Geometry": "{200, 200, width, height}"},
        [
            ui.VGroup({"ID": 'root'},
                      ## Add your GUI elements here:
                      [
                          ui.TextEdit({"ID": 'AboutText', "ReadOnly": "true",
                                       "Alignment": "{AlignHCenter = true,AlignTop = true}", "HTML": 'test'}),
                          ui.VGroup({"Weight": "0"},
                                    ui.Label({"ID": "URL", "Text": "test1",
                                              "Alignment": "{AlignHCenter = true,AlignTop = true}", "WordWrap": "true",
                                              "OpenExternalLinks": "true"}),
                                    ui.Label({"ID": "EMAIL", "Text": "test",
                                              "Alignment": "{AlignHCenter = true, AlignTop = true}", "WordWrap": "true",
                                              "OpenExternalLinks": "true"})
                                    ),
                      ]),
        ])


    itm = win.GetItems()


def _func(ev):
    disp.ExitLoop()


    win.On.AboutWin.Close = _func

dlg = disp.AddWindow({"WindowTitle": "MetadataImporter", "ID": "MyWin", "Geometry": [100, 100, 400, 200], },
                     [
                         ui.VGroup({"Spacing": .5, },
                                   [
                                       # Add your GUI elements here:
                                       ui.TextEdit(
                                           {"ID": "ClipList", "Text": "ClipList", "PlaceholderText": "ClipList",
                                            "Weight": 0.5,"Height": "200","ReadOnly":True,}),
                                       ui.Button({"ID": "PrintButton", "Text": "Select Lens CSV's", "Weight": 0.5}),
                                       ui.HGap(0, .5),
                                       ui.Button({"ID": "ScriptEButton", "Text": "Select ScriptE xml", "Weight": 0.5}),
                                       ui.HGap(0, .5),                                       
                                       ui.ComboBox({"ID": 'FPS', "Text": 'Combo Menu'}),
                                       ui.HGap(0, .5),
                                       ui.VGap({"0", "2.0"}),
                                       ui.Button({"Weight": "0.25", "ID": 'AboutDialogButton',
                                                  "Text": 'Show the About Dialog'}),
                                       ui.Label({"ID": "Status","Text": "Waiting for input", "Weight": 0.5})
                                   ]),
                     ])

itm = dlg.GetItems()


# The window was closed
def _func(ev):
    disp.ExitLoop()


dlg.On.MyWin.Close = _func

# Add your GUI element based event functions here:

## Add the items to the ComboBox menus
itm["FPS"].AddItem('23.98')
itm["FPS"].AddItem('24')
itm["FPS"].AddItem('29.97')
itm["FPS"].AddItem('30')
itm["FPS"].AddItem('59.94')
itm["FPS"].AddItem('60')
#
# itm["Operation"].AddItem('Add')
# itm["Operation"].AddItem('Subtract')
# itm["Operation"].AddItem('Multiply')
# itm["Operation"].AddItem('Divide')


def Select_CSVFolder():
    global Folder_Name
    global Clips
    global MetadataList
    newfields = []
    newrows = []
    MetadataList = []
    root = Tk()
    
    root.filename = filedialog.askopenfilenames(initialdir="/", title="Select file",
                                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    root.withdraw()
    print(root.filename)
    file_list = list(root.filename)
    print("file list: " + str(file_list))
    # for each csv condense down to a new row
    
    for x in file_list:
        #print(x)
        tcList = []
        # reading csv file
        df = pd.read_csv(x,index_col=0,sep=r"\t",engine='python')
        if(df.empty):
            print ('CSV file is empty')
        else:
            print ('CSV file is not empty')
            df['Master TC'] = df['Master TC'].astype(str)
            tc_list = df["Master TC"]
            tcStart = Timecode(fps,df["Master TC"].min())
            tcEnd = Timecode(fps,df["Master TC"].max())
            #print(tcEnd,tcStart)
            MetadataList.append([df['Camera Index'][0],tcStart,tcEnd,df['Lens Focal Length'][0],df['Lens Iris'][0],df['Lens Focus Distance'][0],df['Lens'][0]])
            #print(MetadataList)
            #print(MetadataList[0][0])
    return MetadataList
    print(MetadataList)

clip_list = []
def Get_ClipList():
    global clip_list
    global object_List
    clip_list = []
    object_List = []
    for x in Clips:
        #print(x.GetName())
        print(x.GetClipProperty())
        type_var = list(x.GetClipProperty("Type").values())[0]
        #print(type_var)
        #for y in list(x.GetClipProperty("Type").values():
            #type_var = y
        if type_var == "Video":
            clip_list.append(x.GetName())
            object_List.append(x)
        else:
            print(str(x.GetName()) + " was not included")
    itm['ClipList']({"ReadOnly" : False})
    itm['ClipList']({"Text" : clip_list})



#def Apply_Metadata(Bin, csv):
 #   global



def Add_Metadata():
    #print(object_List)
    clipNames = []
    #for obj in object_List:
        #print(str(obj.GetClipProperty("File Name"))[:1])
    print(MetadataList)
        
    for x in MetadataList:   
        for y in object_List:
        
        
            #print(y.GetClipProperty())
            #list(x.GetClipProperty("Type").values())[0]
            objectStartTC = Timecode(fps,list(y.GetClipProperty("Start TC").values())[0])
            objectEndTC = Timecode(fps,list(y.GetClipProperty("End TC").values())[0])
            object_Cam = str(list(y.GetClipProperty("File Name").values())[0])[:1]
            #print(object_Cam)
            #object_Cam = object_Cam[:0]
            #print(object_Cam)
            #print(object_Cam,objectStartTC,objectEndTC)
            #print(x[1],x[2],x[0], objectStartTC, objectEndTC, object_Cam)
            #if x[1] <= objectStartTC:
            #    print("objectStart tc match")
            #elif x[2] >= objectEndTC:
            #    print("object End tc match")
            #if x[0] == object_Cam:
             #   print("cam match")
            #    y.SetMetadata('Camera #', str(x[0]))
            #else:
            #   print("no matches")
            if (max(x[1],objectStartTC) <= min(x[2],objectEndTC)) == True and (x[0] == object_Cam) == True:
                print("Found a match for " + str(list(y.GetClipProperty("File Name").values())[0]))
                y.SetMetadata('Lens Number', str(x[3]))
                y.SetMetadata('Camera Aperture', str(x[4]))
                y.SetMetadata('Distance', str(x[5])+ " Feet")
                y.SetMetadata('Lens Type', str(x[6]))

                
def Add_ScriptE_Metadata():
    clipNames = []
    for x in ScriptEMetadataList:   
        for y in object_List:
            print()

def Convert_toFrames(TC, FPS):
    global status_text
    if str(TC) == str(neg_error) or TC == "":
        print()
    else:
        tc1 = Timecode(FPS, TC)
        tc3 = tc1.frame_number
        itm['Result']({"Text": tc3})
        status_text = str(tc3)


def Convert_toTC(TC, FPS):
    global status_text

    if str(TC) == str(neg_error) or TC == "":
        print()
    else:
        tc3 = Timecode(FPS, start_timecode=None, frames=int(TC)) + Timecode(FPS, "00:00:00:00")
        # tc3 = tc1.frame_number
        itm['Result']({"Text": tc3})
        status_text = str(tc3)

def ScriptE_XML_read(file_path):
    global Clips
    global ScriptEMetadataList
    tree = ET.parse(file_path)
    #print(tree)
    root = tree.getroot()
    shotList = []
    df_cols = ["Start Date", "Start Time", "End Time", "Camera Roll", "Production Name", "Shoot Day","Camera","Description", "Comment", "Slate"]
    rows = []
    #[StartD, StartT, EndT, roll, prodName, shootDay, scriptE, cam, descript, comment, slate]
    prodName, shootDay, cam, slate, take, roll, clipNum, soundroll, Lens, circle, selType, complete, Comment, techComm, caption = "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
    for shots in root.iter("ShotProperties"):
        prodName, shootDay, cam, slate, take, roll, clipNum, soundroll, Lens, circle, selType, complete, Comment, techComm, caption, descript = "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
        for x in shots:
            #print(x.tag)
            #get all items
            #print((str(x.tag) + ": " + str(str(x.text))

            if str(x.tag) == 'OriginalRoll':
                roll = str(x.text.strip())
                roll = roll[0] + "00" + roll[1]
                #print(roll)
            if str(x.tag) == 'Slate':
                slate = str(x.text)
            if str(x.tag) == 'ShootDay':
                shootDay = str(x.text)
            if str(x.tag) == 'SoundRoll':
                soundroll = str(x.text)
            if str(x.tag) == 'CircleStatus':
                circle = str(x.text)
            if str(x.tag) == 'ClipNumber':
                if x.text == None:
                    print(str(x.text))
                else:
                    clipNum = str(x.text.strip())
            if str(x.tag) == 'SelectType':
                selType = str(x.text)
            if str(x.tag) == 'Comment':
                Comment = str(x.text)
            if str(x.tag) == 'TechnicalComment':
                techComm = str(x.text)
            if str(x.tag) == 'ProductionName':
                prodName = str(x.text)
            if str(x.tag) == 'Lenstype':
                Lens = str(x.text)
            if str(x.tag) == 'ShotCaption':
                caption = str(x.text)
            if str(x.tag) == 'ShotDescription':
                descript = str(x.text)
            if str(x.tag) == 'Camera':
                cam = str(x.text)
            if str(x.tag) == 'Take':
                take = str(x.text)
            if str(x.tag) == 'CompleteShot':
                complete = str(x.text)
            if str(x.tag) == 'StartDateTime':
                StartDT = str(x.text)
                StartD, StartT = StartDT.split(" ")
                StartT = StartT + ":00"
                #print(StartD, StartT)
            if str(x.tag) == 'EndDateTime':
                EndDT = str(x.text)    
                EndD, EndT = EndDT.split(" ")
                EndT = EndT + ":00"
                #print(EndT)
            if str(x.tag) == 'TimeCodeIn':
                TCIn = str(x.text)
            if str(x.tag) == 'TimeCodeOut':
                TCOut = str(x.text)

                

                
            ###logic to infer clip number
            #may want to add logic to add leading zeroes to roll and clip number.
            #roll = roll.zfill(3)
            #clipNum = roll.zfill(3)
            #clipNum = ET.tostring(clipNum)
            #print (roll, clipNum)
            roll.strip()
            clipNum.strip()
            reelname = roll + clipNum
            #print(reelname)
            #if circle == "Circle":
                #circle = "Y"
            #if selType == "DIR FAV":
                #selType = "DIR FAV"
            #if selType == "NG":
                #selType = "Pink"
            #if selType == "OK":
                #selType = "Navy"
            #if selType == "PIECES":
                #selType = "Orange"
            #scriptE = circle + " " + slate + take + " " + reelname + " " + descript + " " + Comment + " " + caption + " " + selType + " " + techComm + StartT + EndT
            #print(scriptE)

            #["Filename", "Description", "Comments", "Reel Name", "Shot","Clip Color", "Good Take", "Production Name", "Crew Comments"]
            #shotList.append([reelname, prodName, shootDay, cam, slate, take, roll, clipNum, soundroll, Lens, circle, selType, complete, Comment, techComm, caption, descript])
            #shotList.append([reelname, descript, Comment, reelname, caption, selType, circle, prodName, techComm])
        
        shotList.append([StartD, TCIn, TCOut, roll, prodName, shootDay, cam, descript, Comment, slate + take, circle])
        rows.append({"Start Date": StartD, "Start Time":StartT, "End Time":EndT, "Camera Roll": roll, "Production Name": prodName, "Shoot Day": shootDay,"Camera": cam,"Description":descript, "Comment": Comment, "Slate": slate})
        df = pd.DataFrame(rows, columns = df_cols)
    #print(df)
    print(shotList)
    clipsA_startTC = []
    clipsB_startTC = []
    for x in Clips:
        name =  list(x.GetClipProperty("Clip Name").values())[0]
        camera = str(name)[:1]
        #print(camera)
        if camera == "A":
            clipsA_startTC.append(Timecode(fps,list(x.GetClipProperty("Start TC").values())[0]).frames)
        elif camera == "B":
            clipsB_startTC.append(Timecode(fps,list(x.GetClipProperty("Start TC").values())[0]).frames)

    #print(clips_startTC)
    shotListA = []
    shotListB = []
    shotListOther = []
    for x in shotList:
        if x[6] == "A":
            shotListA.append(x)
        if x[6] == "B":
            shotListB.append(x)
        else:
            shotListOther.append(x)
    print("ShotListA" + str(shotListA) ) 
    for i in shotListA:
        if len(clipsA_startTC) > 0:    
            Matched_TC = min(clipsA_startTC, key=lambda x:abs(x-Timecode(fps,i[1]).frames))
            print("There are shots in A")
            i[1] = Timecode(fps, frames=Matched_TC)

    
    for x in shotListA:
        for y in Clips:
            Cam_num = str(list(y.GetClipProperty("Clip Name").values())[0])[:1]
            #print(Cam_num)
            #print(x[1])
            if x[1] == list(y.GetClipProperty("Start TC").values())[0] and Cam_num == "A":
                print("found a match at " + str(x[1]))
                y.SetMetadata('Production Name', str(x[4]))
                y.SetMetadata('Shoot Day', str(x[5]))
                y.SetMetadata('Camera #', str(x[6]))
                y.SetMetadata('Description', str(x[7]))
                y.SetMetadata('Comments', str(x[8]))
                y.SetMetadata('Shot Type', str(x[10]))
                y.SetMetadata('Shot', str(x[9]))
         
    print(shotListB)
    for i in shotListB:
        if len(clipsB_startTC) > 0: 
            Matched_TC = min(clipsB_startTC, key=lambda x:abs(x-Timecode(fps,i[1]).frames))
            print("There are shots in B")
            i[1] = Timecode(fps, frames=Matched_TC)


    #print(shotListB)
    
    for x in shotListB:
        for y in Clips:
            Cam_num = str(list(y.GetClipProperty("Clip Name").values())[0])[:1]
            if x[1] == list(y.GetClipProperty("Start TC").values())[0] and Cam_num == "B":
                print("found a match at " + str(x[1]))
                y.SetMetadata('Production Name', str(x[4]))
                y.SetMetadata('Shoot Day', str(x[5]))
                y.SetMetadata('Camera #', str(x[6]))
                y.SetMetadata('Description', str(x[7]))
                y.SetMetadata('Comments', str(x[8]))
                y.SetMetadata('Shot Type', str(x[10]))
                y.SetMetadata('Shot', str(x[9]))

                


    

Get_ClipList()
itm['ClipList'].Text = "clips to append metadata to: " + str(clip_list)

def _func(ev):
    
    Select_CSVFolder()
    itm['Status'].Text = "Adding Lens Metadata"
    Add_Metadata()
    print("finished")
    itm['Status'].Text = "Finished"




dlg.On.PrintButton.Clicked = _func


def _func(ev):
    root = Tk()
    itm['Status'].Text = "Adding script Metadata"
    ScriptEfilename = filedialog.askopenfilename(initialdir=r"W:\Tribal\Tribal_Cycle_II_Working\Tribal 2 Editor Reports", title="Select file",
                                               filetypes=(("ScriptE XML", "*.xml"), ("all files", "*.*")))
    root.withdraw()
    print (ScriptEfilename)
    ScriptEfilename = os.path.abspath(ScriptEfilename)
    SL3 = ScriptE_XML_read(ScriptEfilename)
    #print(SL3)
    Add_ScriptE_Metadata()
    print("finished")
    itm['Status'].Text = "Finished"



dlg.On.ScriptEButton.Clicked = _func


# def _func(ev):
#	print(itm['TC2'].Text)
# dlg.On.PrintButton.Clicked = _func

# def _func(ev):
#     if str(itm['TC1'].Text)[-1] not in ('0123456789:'):
#         itm['TC1'].Text = itm['TC1'].Text[:-1]
#     print(str(itm['TC1'].Text))
#     if len(itm['TC1'].Text) > 11:
#         itm['TC1'].Text = itm['TC1'].Text[:-1]
#
#     my_str = re.sub('[:]', '', itm['TC1'].Text)
#     # my_str = re.sub('[;]', '', values['tc1'])
#     my_str = ':'.join([my_str[i:i + 2] for i in range(0, len(my_str), 2)])
#     # my_str = ';'.join([my_str[i:i + 2] for i in range(0, len(my_str), 2)])
#     itm['TC1'].Text = str(my_str)


# print(my_str)


# dlg.On.TC1.TextChanged = _func
#
#
# def _func(ev):
#     if str(itm['TC1'].Text)[-1] not in ('0123456789'):
#         itm['TC1'].Text = itm['TC1'].Text[:-1]
#
#
# dlg.On.Alt.TextChanged = _func


def _func(ev):
    ## Close the current main window
    # dlg.Hide()

    ## Display an "About dialog" window
    AboutWindow()


dlg.On.AboutDialogButton.Clicked = _func

dlg.Show()
disp.RunLoop()
dlg.Hide()

