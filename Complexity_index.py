# -*- coding: utf-8 -*-
from connect import *
import numpy as np
import os
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import ttk
import datetime

###############################################################################################################################
###############################################################################################################################
###############################################################################################################################
###############################################################################################################################
"""
### UI to get IDPatient list ###
#root = Tk()
#root.title("Copy and past below the IDPatient to analyse:")

#v = StringVar()
#textbox1 = Entry(root, textvariable=v)
#textbox1.grid(column=0,row=0)
#textbox1.config(width=40)

#def Quit():
# root.destroy()

#butt1 = Button(root, text = 'Run the script', command = Quit)
#butt1.grid(column=1, row=0)
#butt1.config(width=40)

#root.mainloop()

#IDText = v.get()
#IDList = IDText.split(",")
### UI to get IDPatient list ###
"""

def fonction_calculate_MCSv_LT(patient,case,plan):

 the_plan = plan
 #the_plan = get_current('Plan')
 #List_Name_Plans.append(the_plan.Name)
 the_beamset = get_current('BeamSet')
 
 ##################################
 ## Calcul du nombre d'arcs, de CP et de MU dans le plan
 ##
 ###############################

 # Nombre d'arcs
 Nombre_Arcs = the_beamset.Beams.Count

 # Nombre de CP
 List_Nombre_CP=[]
 for i_arc in range(Nombre_Arcs):
    List_Nombre_CP.append(the_beamset.Beams[i_arc].Segments.Count)

 # Nombre de MU
 List_Nombre_MU=[]
 for i_arc in range(Nombre_Arcs):
    List_Nombre_MU.append(the_beamset.Beams[i_arc].BeamMU)

 Total_MU = sum(List_Nombre_MU)
 #List_MU_Plans.append(Total_MU)
 
 print(" \n ------------------------------------------------------------------------------- \n ")
 print("  Nom du Plan :", the_plan.Name) 
 #print("  N° du Plan :", num_plan)
 print("  Le nombre d'arcs:", Nombre_Arcs)
 print("  Le nombre de CP pour chaque arc:", List_Nombre_CP)
 print("  Le nombre de MU pour chaque arc:", List_Nombre_MU)
 print("  Le nombre total de MU:", Total_MU)
 print(" \n  ")


 ##################################
 ## Structure des données en Array 4D: 
 ## Array = [arc][CP][Gauche ou Droite][indice de la lame]
 ##################################
 
 list_Arc_Array=[]                       # liste pour stocker les positions des lames de chaque CP et de chaque arc
 list_Arc_Weight=[]                       # liste pour stocker les poids de chaque CP dans chaque arc
 list_indice_jaw_Y=[]

 for i_arc in the_beamset.Beams:
    list_CP_Array=[]                      # liste pour stocker les positions des lames de chaque CP
    list_CP_Weight=[]                      # liste pour stocker les poids de chaque CP (le poids = MU_CP/MU_Arc)
    list_indice_jaw_Y_CP=[]
    
    for i_cp in i_arc.Segments:
    
     Temp_Array_G_D = np.copy(i_cp.LeafPositions)            # ici on recupere de Raystation une liste de Array avec les positions des lames du cote gauche et droit
     Temp_Array_G_D = np.array(Temp_Array_G_D)               # ici on transforme la liste des positions des lames sous la forme d'une array 2D [Gauche/Droite][indice_de_lame]
     list_CP_Array.append(Temp_Array_G_D)
     
     Temp_Weight = i_cp.RelativeWeight
     list_CP_Weight.append(Temp_Weight)
     
     jaw_position_Y1 = i_cp.JawPositions[2]     # Position des machoires. Les indice [2] et [3] correspondent respectivement aux directions Y1 et Y2 (bas et et haut) 
     jaw_position_Y2 = i_cp.JawPositions[3]     # Remarque: La position des machoires peut changer d'un CP à un autre pou les Elekta et les varian truebeam, fixe sur les rapidarc, mais laissé en variables pour avoir un code commun pour tous les accélérateurs varian
     
                           # Indice de la lame dans le champ de traitement (limite du bas du "open field"). Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y1 + 1    (car l'indexation dans python commence à 0 et le TPS on commence à 1)
     if int(jaw_position_Y1)<=-10:    #alors la première lame ouverte est une grande lame
        indice_jaw_position_Y1=21+int(jaw_position_Y1)
     else:           #alors la première lame ouverte est une petite lame
        indice_jaw_position_Y1=int(float(jaw_position_Y1)*2+31)   
                                 # Indice de la première lame en dehors du champ. Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y2      (car dans l'indexation start:end le end n'est pas inclus)  
     if int(jaw_position_Y2)>10:     #alors la dernière lame ouverte est une grande lame
        indice_jaw_position_Y2=40+int(jaw_position_Y2)
     else:            #alors la dernière lame ouverte est une petite lame
        indice_jaw_position_Y2=30+int(jaw_position_Y2*2)
     list_indice_jaw_Y_CP.append([indice_jaw_position_Y1,indice_jaw_position_Y2])
     #print("première lame ouverte :")  #test pour vérifier que le calcul de la première lame ouverte est correcte
     #print (indice_jaw_position_Y1)
     #print("dernière lame ouverte :")  #test pour vérifier que le calcul de la dernière lame ouverte est correcte
     #print (indice_jaw_position_Y2)

    list_CP_Array = np.array(list_CP_Array)                 # ici on transforme la liste des CP en array 3D [CP][G/D][indice_de_lame]
    list_Arc_Array.append(list_CP_Array)
    
    list_CP_Weight=np.array(list_CP_Weight)
    list_Arc_Weight.append(list_CP_Weight)
    
    list_indice_jaw_Y_CP = np.array(list_indice_jaw_Y_CP)
    list_indice_jaw_Y.append(list_indice_jaw_Y_CP)
    
 list_Arc_Array = np.array(list_Arc_Array)                 # ici on transforme la liste des Arcs en array à 4D [Arc][CP][G/D][indice_de_lame]
 list_Arc_Weight = np.array(list_Arc_Weight)
 list_indice_jaw_Y = np.array(list_indice_jaw_Y)
 #print("\n indice y \n",list_indice_jaw_Y)
 #print("\n indice y shape \n",list_indice_jaw_Y.shape)
 
 ##################################
 ## Calcul du LSV
 ##
 ##################################
 
 list_Arc_Array_LSV=[]                      # liste pour stocker les LSV de chaque CP pour chaque arc

 for i_arc in range(Nombre_Arcs):
    list_CP_Array_LSV=[]
    
    for i_cp_ in range(List_Nombre_CP[i_arc]):
     Array_LSV_CP_G = np.copy(list_Arc_Array[i_arc][i_cp_,0])            # array avec les positions des lames gauches de l'arc "i_arc" et du CP "i_cp_"   (on boucle sur tous les CP et tous les arcs) 
     Array_LSV_CP_D = np.copy(list_Arc_Array[i_arc][i_cp_,1])            # array avec les positions des lames droites de l'arc "i_arc" et du CP "i_cp_"   (on boucle sur tous les CP et tous les arcs)

     indice_jaw_position_Y1=list_indice_jaw_Y[i_arc][i_cp_,0]             # Indice de première la lame dans le champ de traitement (limite du bas du "open field"). Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y1 + 1    (car l'indexation dans python commence à 0 et le TPS on commence à 1)
     indice_jaw_position_Y2=list_indice_jaw_Y[i_arc][i_cp_,1]                # Indice de la première lame en dehors du champ. Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y2      (car dans l'indexation start:end le end n'est pas inclus)  
     
     Array_LSV_CP_G = np.copy(Array_LSV_CP_G[indice_jaw_position_Y1-1:indice_jaw_position_Y2])                      #tableau regroupant la position des lames G "ouvertes", ie de la première lame ouverte à la dernière lame ouverte
     Array_LSV_CP_D = np.copy(Array_LSV_CP_D[indice_jaw_position_Y1-1:indice_jaw_position_Y2])
     
     #print(Array_LSV_CP_G)
     N_open_field = Array_LSV_CP_G.size                        ###N= nombre de lames de gauche dans le champ de traitement, ie celles qui ne sont pas sous les mâchoires
     # Calcul de Pos_Max qui est obtenu en faisant max(Pos)-min(Pos)
     #print("nombre de lames dans le champ : ")
     #print(N_open_field)

     Max_Pos_LSV_G_CP=np.amax(Array_LSV_CP_G)               # calcul du max(pos) pour les lames de gauche et dans le champ de traitement
     Max_Pos_LSV_D_CP=np.amax(Array_LSV_CP_D)               # idem à droite
     
     Min_Pos_LSV_G_CP=np.amin(Array_LSV_CP_G)               # calcul du min(pos) pour les lames de gauche et dans le champ de traitement
     Min_Pos_LSV_D_CP=np.amin(Array_LSV_CP_D)               # idem à droite

     Pos_Max_LSV_CP_G = np.copy(Max_Pos_LSV_G_CP - Min_Pos_LSV_G_CP)           ###Calcul du Pos_Max de gauche pour la formule du LSV. Pos_max est l'écart maximum entre la position maximale et minimale occupée par les lames dans un CP
     Pos_Max_LSV_CP_D = np.copy(Max_Pos_LSV_D_CP - Min_Pos_LSV_D_CP)           ###Calcul du Pos_Max de droite pour la formule du LSV.
     
     #print(Pos_Max_LSV_CP_G)          #vérification sur le TPS à différents points de contrôle que le calcul de la différence max est correct
     
     #print(Array_LSV_CP_G)
     
     # Reshape des Array pour le calcul du LSV afin d'avoir l'element n et l'element (n+1)
     
     Array_LSV_CP_G_calc_1 = np.copy(Array_LSV_CP_G[:-1])            # Cela correspond à la position "n" de gauche. Le dernier element est supprimé. On a une array avec (N-1) element
     Array_LSV_CP_D_calc_1 = np.copy(Array_LSV_CP_D[:-1])            
     #print(Array_LSV_CP_G_calc_1)
     Array_LSV_CP_G_calc_2 = np.copy(Array_LSV_CP_G[1:])             # Cela correspond à la position "n+1" de gauche. Le premier element est supprimé. On a une array avec (N-1) element
     Array_LSV_CP_D_calc_2 = np.copy(Array_LSV_CP_D[1:])
     #print(Array_LSV_CP_G_calc_2)

     LSV_CP_G_diff_Array = np.copy(Array_LSV_CP_G_calc_1 - Array_LSV_CP_G_calc_2)        # On fait la difference entre la position "n" et "n+1 = différence de position entre les 2 lames adjacentes"
     LSV_CP_G_diff_Array = np.absolute(LSV_CP_G_diff_Array)            # On prend la valeur absolue de la difference 

     LSV_CP_G_up = (N_open_field)* Pos_Max_LSV_CP_G - np.sum(LSV_CP_G_diff_Array)       # Calcul du numerateur du LSV gauche 
     LSV_CP_G_down = (N_open_field)* Pos_Max_LSV_CP_G             # Calcul du dénominateur du LSV gauche
     LSV_CP_G = LSV_CP_G_up / LSV_CP_G_down                # Calcul du LSV gauche


     LSV_CP_D_diff_Array = np.copy(Array_LSV_CP_D_calc_1 - Array_LSV_CP_D_calc_2)        # idem à droite
     LSV_CP_D_diff_Array = np.absolute(LSV_CP_D_diff_Array)

     LSV_CP_D_up = (N_open_field)* Pos_Max_LSV_CP_D - np.sum(LSV_CP_D_diff_Array) 
     LSV_CP_D_down = (N_open_field)* Pos_Max_LSV_CP_D
     LSV_CP_D = LSV_CP_D_up / LSV_CP_D_down

     LSV_CP = LSV_CP_G * LSV_CP_D                  ###***!!!***###   Calcul du LSV du CP   ###***!!!***### 
     list_CP_Array_LSV.append(LSV_CP)              #list_CP_Array_LSV = liste avec les valeurs du LSV de chaque point de contrôle
     

    list_CP_Array_LSV = np.array(list_CP_Array_LSV)     #array avec les valeurs du LSV de chaque point de contrôle
    #print("list_CP_Array_LSV")
    #print(list_CP_Array_LSV)
    list_Arc_Array_LSV.append(list_CP_Array_LSV)  #concaténation des LSV pour chaque arc   
    
    
    
 list_Arc_Array_LSV = np.array(list_Arc_Array_LSV) #array avec autant de liste de LSV que d'arc
 #print("liste des LSV de chaque arc")
 #print(list_Arc_Array_LSV)

 #print(" \n ---------------------- \n ")
 #print(" list_Arc_Array_LSV = \n ",list_Arc_Array_LSV)
 #print(" Max_Pos_LSV_G_CP = \n ",Max_Pos_LSV_G_CP)
 #print(" Max_Pos_LSV_D_CP = \n ",Max_Pos_LSV_D_CP)
 #print("N_open_field=",N_open_field)
 #print("LSV_CP_D_diff_Array shape =",LSV_CP_D_diff_Array.shape)
 #print(" \n ---------------------- \n ")
 #print(" shape = ",list_Arc_Array_LSV.shape)
 #print(" dim = ",list_Arc_Array_LSV.ndim)


 #######################################
 ## Calcul du AAV
 ##
 ######################################

 ## Calcul du Maximum aperture AAV_max

 list_Arc_Array_AAV_max=[]

 for i_arc in range(Nombre_Arcs):
    for i_cp_ in range(List_Nombre_CP[i_arc]):
     temp_Array_AAV_CP_G = np.copy(list_Arc_Array[i_arc][i_cp_,0])    #tableau avec la position de toutes les lames de gauche pour les i points de contrôle, pour les i arc
     temp_Array_AAV_CP_D = np.copy(list_Arc_Array[i_arc][i_cp_,1])    #tableau avec la position de toutes les lames de droite pour les i points de contrôle, pour les i arc
     #temp_Array_AAV_CP_diff = np.copy(Array_AAV_CP_D - Array_AAV_CP_G)         # La position de droite est toujours superieure à celle de gauche Donc les elements de temp_Array_AAV_CP_diff sont positifs. 

     indice_jaw_position_Y1=list_indice_jaw_Y[i_arc][i_cp_,0]                 # Indice de la première lame dans le champ de traitement (limite du bas du "open field"). Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y1 + 1    (car l'indexation dans python commence à 0 et le TPS on commence à 1)
     #print("indice de la première lame dans le champ")
     #print(indice_jaw_position_Y1)
     indice_jaw_position_Y2=list_indice_jaw_Y[i_arc][i_cp_,1]                 # Indice de la dernière lame dans le champ. Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y2      (car dans l'indexation start:end le end n'est pas inclus)  
     #print("indice de la dernière lame dans le champ")
     #print(indice_jaw_position_Y2)
     #print("indice_jaw_position_Y1 : test pour vérifier la première lame dans le champ")           #test pour vérifier la première lame dans le champ
     #print(indice_jaw_position_Y1)           #test pour vérifier la première lame dans le champ
     #print("indice_jaw_position_Y2 : test pour vérifier la dernière lame dans le champ")           #test pour vérifier la dernière lame dans le champ
     #print(indice_jaw_position_Y2)           #test pour vérifier la dernière lame dans le champ
     temp_Array_AAV_CP_G[:indice_jaw_position_Y1-1] = 0       #position de toutes les lames de gauche de la lame 1 à la première lame ouverte exclue
     temp_Array_AAV_CP_G[indice_jaw_position_Y2:] = 0       #position de toutes les lames de gauche de la dernière lame ouverte à la lame 60
     #print("position de toutes les lames de gauche de la dernière lame ouverte à la lame 60")
     #print(temp_Array_AAV_CP_G)
     
    
     #print("temp_Array_AAV_CP_G")
     #print(temp_Array_AAV_CP_G)
     
     temp_Array_AAV_CP_D[:indice_jaw_position_Y1] = 0  # mise à 0 de la position des lames de la 1 à la lame avant la première lame ouverte
     temp_Array_AAV_CP_D[indice_jaw_position_Y2:] = 0    # mise à 0 de la position de la première lame fermée à la dernière lame
    
     if i_cp_ == 0:                      # pour initialiser le Array_AAV_CP_diff
        Array_AAV_min_CP_G = np.copy(list_Arc_Array[i_arc][i_cp_,0])  # liste de la position de toutes les lames de gauche
        Array_AAV_max_CP_D = np.copy(list_Arc_Array[i_arc][i_cp_,1])  # liste de la position de toutes les lames de droite
        #print("liste de toutes les lames de gauche")
        #print(Array_AAV_min_CP_G)
        indice_jaw_position_Y1_min_AAV = indice_jaw_position_Y1
        indice_jaw_position_Y2_max_AAV = indice_jaw_position_Y2
        
     for i_indice in range(Array_AAV_min_CP_G.shape[0]):                 # taille de la matrice Array_AAV_min_CP_G = nombre de lames= 60 , i correspond aux lames
        if Array_AAV_min_CP_G[i_indice]>temp_Array_AAV_CP_G[i_indice]:       
         Array_AAV_min_CP_G[i_indice]=temp_Array_AAV_CP_G[i_indice]       # On cherche la plus petite position de la lame à gauche (lame la plus à gauche donc min_pos_gauche )
         
        if Array_AAV_max_CP_D[i_indice]<temp_Array_AAV_CP_D[i_indice]:       
         Array_AAV_max_CP_D[i_indice]=temp_Array_AAV_CP_D[i_indice]       # On cherche la plus grande position de la lame à droite (lame la plus à droite donc max_pos_droite )   
     
     if indice_jaw_position_Y1_min_AAV>indice_jaw_position_Y2:
        indice_jaw_position_Y1_min_AAV = indice_jaw_position_Y2  

     if indice_jaw_position_Y2_max_AAV<indice_jaw_position_Y1:
        indice_jaw_position_Y2_max_AAV = indice_jaw_position_Y1   

    
    Array_AAV_min_CP_G[:indice_jaw_position_Y1_min_AAV] = 0  
    Array_AAV_min_CP_G[indice_jaw_position_Y2_max_AAV:] = 0
    
    Array_AAV_max_CP_D[:indice_jaw_position_Y1_min_AAV] = 0
    Array_AAV_max_CP_D[indice_jaw_position_Y2_max_AAV:] = 0
 
    Array_AAV_CP_diff = np.copy(Array_AAV_max_CP_D - Array_AAV_min_CP_G)
    AAV_max_arc = np.sum(Array_AAV_CP_diff)   
    list_Arc_Array_AAV_max.append(AAV_max_arc)
    
 list_Arc_Array_AAV_max = np.array(list_Arc_Array_AAV_max)            ###***!!!***###   Calcul du AAV_max de l'arc   ###***!!!***### 

 #print("---------------------------------------------------------------------")
 #print("\n list_Arc_Array_AAV_max \n", list_Arc_Array_AAV_max)
 #print("---------------------------------------------------------------------")

 ## Calcul du   AAV

 list_Arc_Array_AAV=[]
 for i_arc in range(Nombre_Arcs):
    list_CP_Array_AAV=[]
    for i_cp_ in range(List_Nombre_CP[i_arc]):
     Array_AAV_CP_G_calc1 = np.copy(list_Arc_Array[i_arc][i_cp_,0]) #un tableau pour chaque point de contrôle, contenant la position des lames de gauche
     #print("Array_AAV_CP_G_calc1")
     #print(Array_AAV_CP_G_calc1)
     Array_AAV_CP_D_calc2 = np.copy(list_Arc_Array[i_arc][i_cp_,1])  #un tableau pour chaque point de contrôle, contenant la position des lames de droite
     Array_AAV_CP_diff_calc = np.copy(Array_AAV_CP_D_calc2 - Array_AAV_CP_G_calc1)     # Calcul de la surface entre lame de droite et lame de gauche pour un CP, initialisation poru elekta
     #print("différence")
     #print(Array_AAV_CP_diff_calc)
     Array_AAV_CP_diff_calc[0] = Array_AAV_CP_D_calc2[0] - Array_AAV_CP_G_calc1[0]   # lames 1 à 10 (indexation 0 à 9) et lames 51 à 60 (indexation 50 à 59): 1cm d'épaisseur => pour avoir la surface, il faut juste soustraire la droite de la gauche
     Array_AAV_CP_diff_calc[1] = Array_AAV_CP_D_calc2[1] - Array_AAV_CP_G_calc1[1]
     Array_AAV_CP_diff_calc[2] = Array_AAV_CP_D_calc2[2] - Array_AAV_CP_G_calc1[2]
     Array_AAV_CP_diff_calc[3] = Array_AAV_CP_D_calc2[3] - Array_AAV_CP_G_calc1[3]
     Array_AAV_CP_diff_calc[4] = Array_AAV_CP_D_calc2[4] - Array_AAV_CP_G_calc1[4]
     Array_AAV_CP_diff_calc[5] = Array_AAV_CP_D_calc2[5] - Array_AAV_CP_G_calc1[5]
     Array_AAV_CP_diff_calc[6] = Array_AAV_CP_D_calc2[6] - Array_AAV_CP_G_calc1[6]
     Array_AAV_CP_diff_calc[7] = Array_AAV_CP_D_calc2[7] - Array_AAV_CP_G_calc1[7]
     Array_AAV_CP_diff_calc[8] = Array_AAV_CP_D_calc2[8] - Array_AAV_CP_G_calc1[8]
     Array_AAV_CP_diff_calc[9] = Array_AAV_CP_D_calc2[9] - Array_AAV_CP_G_calc1[9]
     Array_AAV_CP_diff_calc[10] = (Array_AAV_CP_D_calc2[10] - Array_AAV_CP_G_calc1[10])*0.5  # lames 11 à 50 (indexation 10 à 49) : 0.5cm d'épaisseur => pour avoir la surface, il faut multiplier par 0.5 la soustraction entre la droite et la gauche
     Array_AAV_CP_diff_calc[11] = (Array_AAV_CP_D_calc2[11] - Array_AAV_CP_G_calc1[11])*0.5
     Array_AAV_CP_diff_calc[12] = (Array_AAV_CP_D_calc2[12] - Array_AAV_CP_G_calc1[12])*0.5
     Array_AAV_CP_diff_calc[13] = (Array_AAV_CP_D_calc2[13] - Array_AAV_CP_G_calc1[13])*0.5
     Array_AAV_CP_diff_calc[14] = (Array_AAV_CP_D_calc2[14] - Array_AAV_CP_G_calc1[14])*0.5
     Array_AAV_CP_diff_calc[15] = (Array_AAV_CP_D_calc2[15] - Array_AAV_CP_G_calc1[15])*0.5
     Array_AAV_CP_diff_calc[16] = (Array_AAV_CP_D_calc2[16] - Array_AAV_CP_G_calc1[16])*0.5
     Array_AAV_CP_diff_calc[17] = (Array_AAV_CP_D_calc2[17] - Array_AAV_CP_G_calc1[17])*0.5
     Array_AAV_CP_diff_calc[18] = (Array_AAV_CP_D_calc2[18] - Array_AAV_CP_G_calc1[18])*0.5
     Array_AAV_CP_diff_calc[19] = (Array_AAV_CP_D_calc2[19] - Array_AAV_CP_G_calc1[19])*0.5
     Array_AAV_CP_diff_calc[20] = (Array_AAV_CP_D_calc2[20] - Array_AAV_CP_G_calc1[20])*0.5
     Array_AAV_CP_diff_calc[21] = (Array_AAV_CP_D_calc2[21] - Array_AAV_CP_G_calc1[21])*0.5
     Array_AAV_CP_diff_calc[22] = (Array_AAV_CP_D_calc2[22] - Array_AAV_CP_G_calc1[22])*0.5
     Array_AAV_CP_diff_calc[23] = (Array_AAV_CP_D_calc2[23] - Array_AAV_CP_G_calc1[23])*0.5
     Array_AAV_CP_diff_calc[24] = (Array_AAV_CP_D_calc2[24] - Array_AAV_CP_G_calc1[24])*0.5
     Array_AAV_CP_diff_calc[25] = (Array_AAV_CP_D_calc2[25] - Array_AAV_CP_G_calc1[25])*0.5
     Array_AAV_CP_diff_calc[26] = (Array_AAV_CP_D_calc2[26] - Array_AAV_CP_G_calc1[26])*0.5
     Array_AAV_CP_diff_calc[27] = (Array_AAV_CP_D_calc2[27] - Array_AAV_CP_G_calc1[27])*0.5
     Array_AAV_CP_diff_calc[28] = (Array_AAV_CP_D_calc2[28] - Array_AAV_CP_G_calc1[28])*0.5
     Array_AAV_CP_diff_calc[29] = (Array_AAV_CP_D_calc2[29] - Array_AAV_CP_G_calc1[29])*0.5
     Array_AAV_CP_diff_calc[30] = (Array_AAV_CP_D_calc2[30] - Array_AAV_CP_G_calc1[30])*0.5
     Array_AAV_CP_diff_calc[31] = (Array_AAV_CP_D_calc2[31] - Array_AAV_CP_G_calc1[31])*0.5
     Array_AAV_CP_diff_calc[32] = (Array_AAV_CP_D_calc2[32] - Array_AAV_CP_G_calc1[32])*0.5
     Array_AAV_CP_diff_calc[33] = (Array_AAV_CP_D_calc2[33] - Array_AAV_CP_G_calc1[33])*0.5
     Array_AAV_CP_diff_calc[34] = (Array_AAV_CP_D_calc2[34] - Array_AAV_CP_G_calc1[34])*0.5
     Array_AAV_CP_diff_calc[35] = (Array_AAV_CP_D_calc2[35] - Array_AAV_CP_G_calc1[35])*0.5
     Array_AAV_CP_diff_calc[36] = (Array_AAV_CP_D_calc2[36] - Array_AAV_CP_G_calc1[36])*0.5
     Array_AAV_CP_diff_calc[37] = (Array_AAV_CP_D_calc2[37] - Array_AAV_CP_G_calc1[37])*0.5
     Array_AAV_CP_diff_calc[38] = (Array_AAV_CP_D_calc2[38] - Array_AAV_CP_G_calc1[38])*0.5
     Array_AAV_CP_diff_calc[39] = (Array_AAV_CP_D_calc2[39] - Array_AAV_CP_G_calc1[38])*0.5
     Array_AAV_CP_diff_calc[40] = (Array_AAV_CP_D_calc2[40] - Array_AAV_CP_G_calc1[40])*0.5
     Array_AAV_CP_diff_calc[41] = (Array_AAV_CP_D_calc2[41] - Array_AAV_CP_G_calc1[41])*0.5
     Array_AAV_CP_diff_calc[42] = (Array_AAV_CP_D_calc2[42] - Array_AAV_CP_G_calc1[42])*0.5
     Array_AAV_CP_diff_calc[43] = (Array_AAV_CP_D_calc2[43] - Array_AAV_CP_G_calc1[43])*0.5
     Array_AAV_CP_diff_calc[44] = (Array_AAV_CP_D_calc2[44] - Array_AAV_CP_G_calc1[44])*0.5
     Array_AAV_CP_diff_calc[45] = (Array_AAV_CP_D_calc2[45] - Array_AAV_CP_G_calc1[45])*0.5
     Array_AAV_CP_diff_calc[46] = (Array_AAV_CP_D_calc2[46] - Array_AAV_CP_G_calc1[46])*0.5
     Array_AAV_CP_diff_calc[47] = (Array_AAV_CP_D_calc2[47] - Array_AAV_CP_G_calc1[47])*0.5
     Array_AAV_CP_diff_calc[48] = (Array_AAV_CP_D_calc2[48] - Array_AAV_CP_G_calc1[48])*0.5
     Array_AAV_CP_diff_calc[49] = (Array_AAV_CP_D_calc2[49] - Array_AAV_CP_G_calc1[49])*0.5
     Array_AAV_CP_diff_calc[50] = (Array_AAV_CP_D_calc2[50] - Array_AAV_CP_G_calc1[50])
     Array_AAV_CP_diff_calc[51] = (Array_AAV_CP_D_calc2[51] - Array_AAV_CP_G_calc1[51])
     Array_AAV_CP_diff_calc[52] = (Array_AAV_CP_D_calc2[52] - Array_AAV_CP_G_calc1[52])
     Array_AAV_CP_diff_calc[53] = (Array_AAV_CP_D_calc2[53] - Array_AAV_CP_G_calc1[53])
     Array_AAV_CP_diff_calc[54] = (Array_AAV_CP_D_calc2[54] - Array_AAV_CP_G_calc1[54])
     Array_AAV_CP_diff_calc[55] = (Array_AAV_CP_D_calc2[55] - Array_AAV_CP_G_calc1[55])
     Array_AAV_CP_diff_calc[56] = (Array_AAV_CP_D_calc2[56] - Array_AAV_CP_G_calc1[56])
     Array_AAV_CP_diff_calc[57] = (Array_AAV_CP_D_calc2[57] - Array_AAV_CP_G_calc1[57])
     Array_AAV_CP_diff_calc[58] = (Array_AAV_CP_D_calc2[58] - Array_AAV_CP_G_calc1[58])
     Array_AAV_CP_diff_calc[59] = (Array_AAV_CP_D_calc2[59] - Array_AAV_CP_G_calc1[59])
     
     #print(Array_AAV_CP_diff_calc)   #vérification du calcul de la surface
 
     indice_jaw_position_Y1=list_indice_jaw_Y[i_arc][i_cp_,0]                 # Indice de la lame dans le champ de traitement (limite du bas du "open field"). Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y1 + 1    (car l'indexation dans python commence à 0 et le TPS on commence à 1)
     indice_jaw_position_Y2=list_indice_jaw_Y[i_arc][i_cp_,1]                # Indice de la première lame en dehors du champ. Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y2      (car dans l'indexation start:end le end n'est pas inclus)  
     
     Array_AAV_CP_diff_calc[:indice_jaw_position_Y1-1] = 0  # Mise à zéro de la surface pour les lames comprises entre la lame 0 et la lame d'avant la première lame ouverte
     Array_AAV_CP_diff_calc[indice_jaw_position_Y2:] = 0   # Mise à zéro de la surface pour les lames comprises entre la première lame fermée et la dernière lame
     
     AAV_CP_up = np.sum(Array_AAV_CP_diff_calc)              # Calcul de la surface totale délimitée par les lames = somme de toutes les surfaces
     #print(AAV_CP_up)          # vérification de la somme pour chaque point de contrôle
     AAV_CP = AAV_CP_up/list_Arc_Array_AAV_max[i_arc]                 ###***!!!***###   Calcul du AAV du CP   ###***!!!***###        
     
     list_CP_Array_AAV.append(AAV_CP)
     
    list_CP_Array_AAV=np.array(list_CP_Array_AAV)
    list_Arc_Array_AAV.append(list_CP_Array_AAV)    # liste des AAV de chaque point de contrôle

 list_Arc_Array_AAV=np.array(list_Arc_Array_AAV)
 #print("List_arc_aav",list_Arc_Array_AAV)


 #######################################
 ## Calcul du MCSv
 ##
 ######################################


 list_Arc_MCSv_AAV=[] # ajout
 list_Arc_MCSv_LSV=[]   # ajout
 list_Arc_MCSv=[]
 for i_arc in range(Nombre_Arcs):
    indice_MCSv=0
    indice_MCSv_AAV=0   # ajout
    indice_MCSv_LSV=0   # ajout
    for i_cp_ in range( (List_Nombre_CP[i_arc]-1) ):              # nombre de points de contrôle, on ne prend pas le dernier element car on fait la somme de l'element "n" et "n+1"
     
     temp_MCSv_AAV = ( list_Arc_Array_AAV[i_arc][i_cp_]+ list_Arc_Array_AAV[i_arc][i_cp_+1] )/2   # Calcul du AAV entre le CP i et le CP i+1, publication de Masi
     temp_MCSv_LSV = ( list_Arc_Array_LSV[i_arc][i_cp_]+ list_Arc_Array_LSV[i_arc][i_cp_+1] )/2    # idem por le LSV
     
##### Essai pour imprimer le AAV et le LSV #####
     temp_MCSv_AAV_reel = temp_MCSv_AAV * list_Arc_Weight[i_arc][i_cp_]   # ajout   
     temp_MCSv_LSV_reel = temp_MCSv_LSV * list_Arc_Weight[i_arc][i_cp_]   # ajout
     
     indice_MCSv_AAV = indice_MCSv_AAV + temp_MCSv_AAV_reel    # ajout
     indice_MCSv_LSV = indice_MCSv_LSV + temp_MCSv_LSV_reel   # ajout


################################################
     
     
     
     temp_MCSv = temp_MCSv_AAV * temp_MCSv_LSV * list_Arc_Weight[i_arc][i_cp_]       # Calcul du MSCv du CP. il faut prendre en compte le poids de chaque CP
     
     indice_MCSv = indice_MCSv + temp_MCSv                ###***!!!***###   Calcul du MCSv de l'arc   ###***!!!***### 

    list_Arc_MCSv.append(indice_MCSv)
    list_Arc_MCSv_AAV.append(indice_MCSv_AAV)   # ajout
    list_Arc_MCSv_LSV.append(indice_MCSv_LSV)   # ajout

 Final_MCSv = 0
 Final_MCSv_AAV = 0   # ajout
 Final_MCSv_LSV = 0   # ajout
 #print("temp_MSC = moyenne de chaque point de contrôle consécutif")
 #print(temp_MCSv_AAV)
 for i_arc in range(Nombre_Arcs):
    Final_MCSv = Final_MCSv + list_Arc_MCSv[i_arc] * List_Nombre_MU[i_arc]/Total_MU       ###***!!!***###   Calcul du MCSv du plan   ###***!!!***### 
    Final_MCSv_AAV = Final_MCSv_AAV + list_Arc_MCSv_AAV[i_arc] * List_Nombre_MU[i_arc]/Total_MU   # ajout
    Final_MCSv_LSV = Final_MCSv_LSV + list_Arc_MCSv_LSV[i_arc] * List_Nombre_MU[i_arc]/Total_MU   # ajout
 
 #List_MCSv_Plans.append(Final_MCSv)

 print(" \n ")
 print("  Indice de modulation  ")
 #list_Arc_MCSv_print = [round(i_1,4) for i_1 in list_Arc_MCSv]
 print("  list_Arc_MCSv:  ", list_Arc_MCSv)
 #print("\n  ")
 print("  MCSv = ", round(Final_MCSv,4))
 print("  MCSv_AAV = ", round(Final_MCSv_AAV,4))
 print("  MCSv_LSV = ", round(Final_MCSv_LSV,4))
 #print(" ")
 
 
 
 
 
 ##################################
 ## Calcul du LT 
 ## On prend en compte que le champ de traitement (LT2)
 ##################################
 
 list_Arc_Array_LT=[]

 for i_arc in range(Nombre_Arcs):
 
    Array_LT_CP_Diff_G = np.zeros(60)     # initialisation d'un tableau pour les 60 lames de gauche
    Array_LT_CP_Diff_D = np.zeros(60)
    
    for i_cp_ in range(List_Nombre_CP[i_arc]-1):

     Array_LT_CP_G_0 = np.copy(list_Arc_Array[i_arc][i_cp_,0])            # array avec les positions des lames gauches de l'arc "i_arc" et du CP "i_cp_"   (on boucle sur tout les CP et tout les arcs) 
     Array_LT_CP_G_1 = np.copy(list_Arc_Array[i_arc][i_cp_+1,0])   # array avec les positions des lames gauches de l'arc "i_arc" et du CP suivant "i_cp_+1"

     Array_LT_CP_D_0 = np.copy(list_Arc_Array[i_arc][i_cp_,1])            # array avec les positions des lames droites de l'arc "i_arc" et du CP "i_cp_"   (on boucle sur tout les CP et tout les arcs)
     Array_LT_CP_D_1 = np.copy(list_Arc_Array[i_arc][i_cp_+1,1])


     indice_jaw_position_Y1_0 = list_indice_jaw_Y[i_arc][i_cp_,0]   # array regroupant la première lame ouverte du point de contrôle cp
     indice_jaw_position_Y2_0 = list_indice_jaw_Y[i_arc][i_cp_,1]   # array regroupant la première lame fermée du point de contrôle cp
     indice_jaw_position_Y1_1 = list_indice_jaw_Y[i_arc][i_cp_+1,0]  # array regroupant la première lame ouverte du point de contrôle cp+1
     indice_jaw_position_Y2_1 = list_indice_jaw_Y[i_arc][i_cp_+1,1]  # array regroupant la première lame fermée du point de contrôle cp+1

     indice_jaw_position_Y1 = max(indice_jaw_position_Y1_0,indice_jaw_position_Y1_1) # maximum entre la première lame ouverte des points de contrôle cp et cp+1
     indice_jaw_position_Y2 = min(indice_jaw_position_Y2_0,indice_jaw_position_Y2_1)  # minimum entre la première lame fermée des points de contrôle cp et cp+1

     Array_LT_CP_G_0[:indice_jaw_position_Y1] = 0 ; Array_LT_CP_D_0[:indice_jaw_position_Y1] = 0  # initialisation à 0
     Array_LT_CP_G_0[indice_jaw_position_Y2:] = 0 ; Array_LT_CP_D_0[indice_jaw_position_Y2:] = 0

     Array_LT_CP_G_1[:indice_jaw_position_Y1] = 0 ; Array_LT_CP_D_1[:indice_jaw_position_Y1] = 0 
     Array_LT_CP_G_1[indice_jaw_position_Y2:] = 0 ; Array_LT_CP_D_1[indice_jaw_position_Y2:] = 0




     Array_LT_CP_Diff_G_temp = np.copy(Array_LT_CP_G_1-Array_LT_CP_G_0)  # différence entre les indices de la première lame fermée entre les points de contrôle cp et cp+1 de gauche
     Array_LT_CP_Diff_G_temp = np.absolute(Array_LT_CP_Diff_G_temp)   # mise en valeur absolue

     Array_LT_CP_Diff_D_temp = np.copy(Array_LT_CP_D_1-Array_LT_CP_D_0)  # différence entre les indices de la première lame fermée entre les points de contrôle cp et cp+1 de droite
     Array_LT_CP_Diff_D_temp = np.absolute(Array_LT_CP_Diff_D_temp)   # mise en valeur absolue

     Array_LT_CP_Diff_G = Array_LT_CP_Diff_G + Array_LT_CP_Diff_G_temp  # incrémentation à chaque point de contrôle pour les lames de gauche
     Array_LT_CP_Diff_D = Array_LT_CP_Diff_D + Array_LT_CP_Diff_D_temp  # incrémentation à chaque point de contrôle pour les lames de droite
        
    #print("\n Array_LT_CP_Diff_G \n",Array_LT_CP_Diff_G)
    #print("\n Array_LT_CP_Diff_D \n",Array_LT_CP_Diff_D)
    
    
    ####### Code original, avec suppression des déplacements nuls dans le champ #######
    
    
    Array_LT_CP_Diff_G =np.where(Array_LT_CP_Diff_G != 0 , Array_LT_CP_Diff_G , Array_LT_CP_Diff_G )   # lorsque la somme des déplacements est non nulle, on remplit la somme des déplacements; lorsqu'elle est nulle, on met rien à la place (non a number)
    Array_LT_CP_Diff_D =np.where(Array_LT_CP_Diff_D != 0 , Array_LT_CP_Diff_D , Array_LT_CP_Diff_D )   # idem pour le banc de droite (suppression des déplacements nuls dans le champ ???? On ne devrait pas les garder ? et ne supprimer que ceux avant la lame ouverte et après la lame fermée
    #print("Array_LT_CP_Diff_G")
    #print(Array_LT_CP_Diff_G)
    #print("\n Array_LT_CP_Diff_G \n",Array_LT_CP_Diff_G)
    #print("\n Array_LT_CP_Diff_D \n",Array_LT_CP_Diff_D)

    #LT_mean_G = np.nanmean(Array_LT_CP_Diff_G)   # moyenne des déplacements de gauche (sans tenir compte des déplacements nuls
    #LT_mean_D = np.nanmean(Array_LT_CP_Diff_D) 
    
    
    ####### Nouveau code : prise en compte des déplacements nuls dans le champ => moyenne des déplacements entre la premièr elame ouverte et la dernière lame ouverte, seuls les déplacements hors champ (forcément nuls) ne sont pas pris en compte dans le calcul de la moyenne
    
    LT_mean_G = np.nanmean(Array_LT_CP_Diff_G[indice_jaw_position_Y1-1:indice_jaw_position_Y2])   # moyenne des déplacements de gauche (sans tenir compte des déplacements nuls)
    #print("LT_mean pour les lames dans le champ")
    #print(Array_LT_CP_Diff_G[indice_jaw_position_Y1-1:indice_jaw_position_Y2])
    #print("LT_mean_G")
    #print(LT_mean_G)
    LT_mean_D = np.nanmean(Array_LT_CP_Diff_D[indice_jaw_position_Y1-1:indice_jaw_position_Y2])

    ######################################################################################



    LT_mean_G_D = (LT_mean_G + LT_mean_D)/2   # moyenne des déplacements entre gauche et droite
    
    list_Arc_Array_LT.append(LT_mean_G_D)
    
    #print("LT_mean_G = ",LT_mean_G)
    #print("LT_mean_D = ",LT_mean_D)
    #print("LT_mean_G_D = ",LT_mean_G_D)
    
 
 
 LT_mean_Plan = 0
 for i_arc in range(Nombre_Arcs):
    LT_mean_Plan = LT_mean_Plan + list_Arc_Array_LT[i_arc]/Nombre_Arcs   # moyenne sur l'ensemble des arcs, par incrémentation
 
 #List_LT_Plans.append(LT_mean_Plan)
 
 print("  LT du champ de traitement")
 print("  LT List (cm)  = ",list_Arc_Array_LT)
 print("  LT Moyen du plan(cm) = ", round(LT_mean_Plan,4))
 
 
 
 ##################################
 ## Calcul du LTMCS 
 ## On ne prend en compte que le champ de traitement (LTMCS 2)
 ##################################
 
 the_LTMCS = Final_MCSv * (200-LT_mean_Plan)/200    # déplacement maximal = 20cm
 #List_LTMCS_Plans.append(the_LTMCS)
 
 print("  LTMCS = ", round(the_LTMCS,4))
 print(" \n ") 
 
 ##################################
 ## Calcul du SAS(1cm)
 ## Ratio Of Small Segments (<1cm²)
 ##################################
 list_sum_1_weight=[]
 list_sum_2_weight=[]
 
 for i_arc in range(Nombre_Arcs):
    Sum_Number_of_seg_SAS_weight = 0   # initialisation du nombre de segments < 1cm²
    Sum_Number_of_all_seg_weight = 0   # initialisation du nombre total de segments
    for i_cp_ in range(List_Nombre_CP[i_arc]):  # sur l'ensemble des points de contrôle
    
     Array_SAS_CP_G = np.copy(list_Arc_Array[i_arc][i_cp_,0])  # liste des positions de chaque lame de gauche de chaque CP et de chaque arc
     Array_SAS_CP_D = np.copy(list_Arc_Array[i_arc][i_cp_,1])  # idem à droite
     
     indice_jaw_position_Y1=list_indice_jaw_Y[i_arc][i_cp_,0]               # Indice de la lame dans le champ de traitement (limite du bas du "open field"). Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y1 + 1    (car l'indexation dans python commence à 0 et le TPS on commence à 1)
     indice_jaw_position_Y2=list_indice_jaw_Y[i_arc][i_cp_,1]               # Indice de la première lame en dehors du champ. Le numéro de lame correspondant dans le TPS est = indice_jaw_position_Y2      (car dans l'indexation start:end le end n'est pas inclus)  
     #print("indice_jaw_position_Y1")
     #print(indice_jaw_position_Y1)
     #print("indice_jaw_position_Y2")
     #print(indice_jaw_position_Y2)
     #Array_SAS_CP_G = Array_SAS_CP_G[indice_jaw_position_Y1:indice_jaw_position_Y2]  # limitation du tableau aux positions des lames de gauche de toutes les lames comprises entre la première ouverte et la dernière ouverte
     #Array_SAS_CP_D = Array_SAS_CP_D[indice_jaw_position_Y1:indice_jaw_position_Y2]  # idem à droite
     
     Array_SAS_diff = np.copy(Array_SAS_CP_D - Array_SAS_CP_G)   # aire => seulement la soustraction => VALABLE UNIQUEMENT POUR LES ELEKTA !!!!!!! Utile pour l'intialisation des varian
     
     Array_SAS_diff[0] = Array_SAS_CP_D[0] - Array_SAS_CP_G[0]   # lames 1 à 10 (indexation 0 à 9) et lames 51 à 60 (indexation 50 à 59): 1cm d'épaisseur => pour avoir la surface, il faut juste soustraire la droite de la gauche
     Array_SAS_diff[1] = Array_SAS_CP_D[1] - Array_SAS_CP_G[1]
     Array_SAS_diff[2] = Array_SAS_CP_D[2] - Array_SAS_CP_G[2]
     Array_SAS_diff[3] = Array_SAS_CP_D[3] - Array_SAS_CP_G[3]
     Array_SAS_diff[4] = Array_SAS_CP_D[4] - Array_SAS_CP_G[4]
     Array_SAS_diff[5] = Array_SAS_CP_D[5] - Array_SAS_CP_G[5]
     Array_SAS_diff[6] = Array_SAS_CP_D[6] - Array_SAS_CP_G[6]
     Array_SAS_diff[7] = Array_SAS_CP_D[7] - Array_SAS_CP_G[7]
     Array_SAS_diff[8] = Array_SAS_CP_D[8] - Array_SAS_CP_G[8]
     Array_SAS_diff[9] = Array_SAS_CP_D[9] - Array_SAS_CP_G[9]
     Array_SAS_diff[10] = (Array_SAS_CP_D[10] - Array_SAS_CP_G[10])*0.5  # lames 11 à 50 (indexation 10 à 49) : 0.5cm d'épaisseur => pour avoir la surface, il faut multiplier par 0.5 la soustraction entre la droite et la gauche
     Array_SAS_diff[11] = (Array_SAS_CP_D[11] - Array_SAS_CP_G[11])*0.5
     Array_SAS_diff[12] = (Array_SAS_CP_D[12] - Array_SAS_CP_G[12])*0.5
     Array_SAS_diff[13] = (Array_SAS_CP_D[13] - Array_SAS_CP_G[13])*0.5
     Array_SAS_diff[14] = (Array_SAS_CP_D[14] - Array_SAS_CP_G[14])*0.5
     Array_SAS_diff[15] = (Array_SAS_CP_D[15] - Array_SAS_CP_G[15])*0.5
     Array_SAS_diff[16] = (Array_SAS_CP_D[16] - Array_SAS_CP_G[16])*0.5
     Array_SAS_diff[17] = (Array_SAS_CP_D[17] - Array_SAS_CP_G[17])*0.5
     Array_SAS_diff[18] = (Array_SAS_CP_D[18] - Array_SAS_CP_G[18])*0.5
     Array_SAS_diff[19] = (Array_SAS_CP_D[19] - Array_SAS_CP_G[19])*0.5
     Array_SAS_diff[20] = (Array_SAS_CP_D[20] - Array_SAS_CP_G[20])*0.5
     Array_SAS_diff[21] = (Array_SAS_CP_D[21] - Array_SAS_CP_G[21])*0.5
     Array_SAS_diff[22] = (Array_SAS_CP_D[22] - Array_SAS_CP_G[22])*0.5
     Array_SAS_diff[23] = (Array_SAS_CP_D[23] - Array_SAS_CP_G[23])*0.5
     Array_SAS_diff[24] = (Array_SAS_CP_D[24] - Array_SAS_CP_G[24])*0.5
     Array_SAS_diff[25] = (Array_SAS_CP_D[25] - Array_SAS_CP_G[25])*0.5
     Array_SAS_diff[26] = (Array_SAS_CP_D[26] - Array_SAS_CP_G[26])*0.5
     Array_SAS_diff[27] = (Array_SAS_CP_D[27] - Array_SAS_CP_G[27])*0.5
     Array_SAS_diff[28] = (Array_SAS_CP_D[28] - Array_SAS_CP_G[28])*0.5
     Array_SAS_diff[29] = (Array_SAS_CP_D[29] - Array_SAS_CP_G[29])*0.5
     Array_SAS_diff[30] = (Array_SAS_CP_D[30] - Array_SAS_CP_G[30])*0.5
     Array_SAS_diff[31] = (Array_SAS_CP_D[31] - Array_SAS_CP_G[31])*0.5
     Array_SAS_diff[32] = (Array_SAS_CP_D[32] - Array_SAS_CP_G[32])*0.5
     Array_SAS_diff[33] = (Array_SAS_CP_D[33] - Array_SAS_CP_G[33])*0.5
     Array_SAS_diff[34] = (Array_SAS_CP_D[34] - Array_SAS_CP_G[34])*0.5
     Array_SAS_diff[35] = (Array_SAS_CP_D[35] - Array_SAS_CP_G[35])*0.5
     Array_SAS_diff[36] = (Array_SAS_CP_D[36] - Array_SAS_CP_G[36])*0.5
     Array_SAS_diff[37] = (Array_SAS_CP_D[37] - Array_SAS_CP_G[37])*0.5
     Array_SAS_diff[38] = (Array_SAS_CP_D[38] - Array_SAS_CP_G[38])*0.5
     Array_SAS_diff[39] = (Array_SAS_CP_D[39] - Array_SAS_CP_G[39])*0.5
     Array_SAS_diff[40] = (Array_SAS_CP_D[40] - Array_SAS_CP_G[40])*0.5
     Array_SAS_diff[41] = (Array_SAS_CP_D[41] - Array_SAS_CP_G[41])*0.5
     Array_SAS_diff[42] = (Array_SAS_CP_D[42] - Array_SAS_CP_G[42])*0.5
     Array_SAS_diff[43] = (Array_SAS_CP_D[43] - Array_SAS_CP_G[43])*0.5
     Array_SAS_diff[44] = (Array_SAS_CP_D[44] - Array_SAS_CP_G[44])*0.5
     Array_SAS_diff[45] = (Array_SAS_CP_D[45] - Array_SAS_CP_G[45])*0.5
     Array_SAS_diff[46] = (Array_SAS_CP_D[46] - Array_SAS_CP_G[46])*0.5
     Array_SAS_diff[47] = (Array_SAS_CP_D[47] - Array_SAS_CP_G[47])*0.5
     Array_SAS_diff[48] = (Array_SAS_CP_D[48] - Array_SAS_CP_G[48])*0.5
     Array_SAS_diff[49] = (Array_SAS_CP_D[49] - Array_SAS_CP_G[49])*0.5
     Array_SAS_diff[50] = Array_SAS_CP_D[50] - Array_SAS_CP_G[50]
     Array_SAS_diff[51] = Array_SAS_CP_D[51] - Array_SAS_CP_G[51]
     Array_SAS_diff[52] = Array_SAS_CP_D[52] - Array_SAS_CP_G[52]
     Array_SAS_diff[53] = Array_SAS_CP_D[53] - Array_SAS_CP_G[53]
     Array_SAS_diff[54] = Array_SAS_CP_D[54] - Array_SAS_CP_G[54]
     Array_SAS_diff[55] = Array_SAS_CP_D[55] - Array_SAS_CP_G[55]
     Array_SAS_diff[56] = Array_SAS_CP_D[56] - Array_SAS_CP_G[56]
     Array_SAS_diff[57] = Array_SAS_CP_D[57] - Array_SAS_CP_G[57]
     Array_SAS_diff[58] = Array_SAS_CP_D[58] - Array_SAS_CP_G[58]
     Array_SAS_diff[59] = Array_SAS_CP_D[59] - Array_SAS_CP_G[59]
     
     
     
     Array_SAS_ = np.where(Array_SAS_diff<=1,1,0)    # incrémentation des segments dont l'aire est < 1cm², segments dans ET hors du champ
     #Number_of_seg_SAS = np.sum(Array_SAS_)   # nombre de segments dont l'aire est < 1cm², segments dans ET hors du champ, OK pour Elekta
     Number_of_seg_SAS = np.sum(Array_SAS_)-(60-(indice_jaw_position_Y2-indice_jaw_position_Y1+1))  # nombre de segments dont l'aire est < 1cm² uniquement dans le champ
     #print("nombre de segments dont l'aire est <1cm²")
     #print(Number_of_seg_SAS)

     #print(60-(indice_jaw_position_Y2-indice_jaw_position_Y1+1))
     #print("nombre de lames en dehors du champs")
     
     #print("nombre de lames dans le champ")
     #print(indice_jaw_position_Y2-indice_jaw_position_Y1+1)
     
     Number_of_all_seg = indice_jaw_position_Y2-indice_jaw_position_Y1+1   # nombre de lames dans le champ
     #Number_of_all_seg = Array_SAS_.size     # nombre de segments total, ok pour Elekta
     #print("nombre de segments total")
     #print(Number_of_all_seg)         # = 60
     
         
     Sum_Number_of_seg_SAS_weight = Sum_Number_of_seg_SAS_weight + Number_of_seg_SAS * list_Arc_Weight[i_arc][i_cp_]  # pondération avec le poids du point de contrôle
     Sum_Number_of_all_seg_weight = Sum_Number_of_all_seg_weight + Number_of_all_seg * list_Arc_Weight[i_arc][i_cp_]
            
    list_sum_1_weight.append(Sum_Number_of_seg_SAS_weight)
    list_sum_2_weight.append(Sum_Number_of_all_seg_weight)
    
 total_Seg_SAS_weight = 0
 total_Seg_weight = 0
 for i_arc in range(Nombre_Arcs):
    total_Seg_SAS_weight = total_Seg_SAS_weight + list_sum_1_weight[i_arc] * List_Nombre_MU[i_arc]/Total_MU  # pondération avec le poids de l'arc
    total_Seg_weight = total_Seg_weight + list_sum_2_weight[i_arc] * List_Nombre_MU[i_arc]/Total_MU
    
 The_SAS_final_weight = total_Seg_SAS_weight/total_Seg_weight     # SAS = ratio entre les SAS et le nombre total de segments
 #List_SAS_weight_Plans.append(The_SAS_final_weight) 

 print("  Ratio du Nombre de Segments inf à 1cm SAS(1cm) avec pondération en MU \n")
 #print("\n  Nombre de petits segments pondéré en UM =  ", total_Seg_SAS_weight)
 #print("\n  Nombre total de segments pondéré en UM =  ", total_Seg_weight)
 print("\n  SAS(1cm) =  ", round(The_SAS_final_weight,4))
 print(" \n ") 
 return [round(The_SAS_final_weight,4),round(Final_MCSv,4),round(LT_mean_Plan,4),round(the_LTMCS,4),round(Final_MCSv_AAV,4),round(Final_MCSv_LSV,4)]
 
 #print("  MCSv = ", round(Final_MCSv,4))
 #print("  MCSv_AAV = ", round(Final_MCSv_AAV,4))
 #print("  MCSv_LSV = ", round(Final_MCSv_LSV,4))




################## Modif ACD ################

# Query patients from path by calling functions from the patient database
db = get_current("PatientDB") 


#for elm in IDList:
# patient_results.append(db.QueryPatientInfo(Filter={'PatientID': elm}))

### on accède ensuite aux patients avec patient_results[y][i] avec y le premier patient de la database et avec les informations qui sont un dictionnaire, soit patient_results[y][i]['PatientID'] ###

#IDList = [201908971, 201707942,201902970,200902203,201903291,201902761,201911575,201910568, 202000066]
#IDList = [202001108,202001680]

ListToExport = ""
#for elm in IDList:

#    patient_results = db.QueryPatientInfo(Filter={'PatientID':elm})
#    db.LoadPatient(PatientInfo = patient_results[0])
patient = get_current('Patient')

#    ### Set case and plan variable ###
#case = patient.Cases['etude IC']
case = get_current('Case')
#case.CaseName
case.SetCurrent()
for elm in case.TreatmentPlans:
     elm.SetCurrent()
     plan = get_current('Plan')

     date = datetime.datetime.now()

     exportDate = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
      
      ### Get patient's informations ###
     namePatient = patient.Name
     nameToSplit = namePatient.split("^")
     firstNamePatient = nameToSplit[1]
     namePatient = nameToSplit[0]

      ### Fill ListToExport with patient's information ###
     patientInfo = [namePatient, firstNamePatient]
     patientID = patient.PatientID

     try:
        indices = fonction_calculate_MCSv_LT(patient,case,plan)
        ListToExport += str(exportDate) + "\t" + str(patientInfo) + "\t" + str(patientID) + "\t" + str(case.CaseName) + "\t" + str(plan.Name) + "\t" + str(indices[0]) + "\t" + str(indices[1]) + "\t" + str(indices[2]) + "\t" + str(indices[3])+ "\t" + str(indices[4]) + "\t" + str(indices[5])+"\n"
     except:
        print("il y a un problème dans le plan qui fait planter le calcul des indices de complexité")


################## UI ACD ################

root = Tk()

root.title("Copy and past the values below:")

v = StringVar()
textbox1 = Entry(root, textvariable=v)
textbox1.grid(column=0, row=4)
textbox1.config(width=100)
textbox1.insert(END, ListToExport)

def Quit():
 root.destroy()

butt1 = Button(root, text = 'Quit', command = Quit)
butt1.grid(column=0, row=6)
butt1.config(width=100)

root.mainloop()

################## UI ACD ################











