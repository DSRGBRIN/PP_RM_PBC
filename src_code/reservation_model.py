import tenseal as ts
#import numpy as np
import time
import pickle 

def genContext():
    context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60],
            encryption_type=ts.ENCRYPTION_TYPE.ASYMMETRIC,
            #context.generate_galois_keys()
        )
    context.global_scale = pow(2, 40)
    return context

def genData(user=False):
    if user:
        data = {
                "reserve1" : [1, 0, 0, 0, 0, 0], #reservation to room A
                "reserve2" : [0, 1, 0, 0, 0, 0], #reservation to room A
                "reserve3" : [0, 0, 1, 0, 0, 0], #reservation to room A
                "reserve4" : [0, 0, 0, 1, 0, 0], #reservation to room A
                "reserve5" : [0, 0, 0, 0, 1, 0]  #reservation to room A
               }
    else: #reservation table
        data = {
                "room_A" : [1, 1, 1, 1, 1, 1], #room A
                "room_B" : [1, 1, 1, 1, 1, 1], #room B
                "room_C" : [1, 1, 1, 1, 1, 1], #room C
                "room_D" : [1, 1, 1, 1, 1, 1], #room D
                "room_E" : [1, 1, 1, 1, 1, 1] #room E
               }
    return data
    
def encryptData(context, plainData):
    enc_vector = {}
    for k in plainData.keys():
        enc_vector[k] = ts.ckks_vector(context, plainData[k])
    return enc_vector

def decrypt(encV):
    result = []
    decrypted_vec = encV.decrypt()
    for k in decrypted_vec:
        result.append(k)
    #print(result)
    return result
   
def decrypt2Int(encV):
    int_result = []
    decrypted_vec = encV.decrypt()
    for k in decrypted_vec:
        int_result.append(int(k))
    #print(int_result)
    return int_result
   
def getConflictValue(encV):
    total = 0
    decrypted_vec = encV.decrypt()
    for k in decrypted_vec:
        total += int(k)
    #print(total)
    return total

def makeInquiry(inqV, VTable, VInquiry):
    print("Initial table : ",FED_data[VTable])
    print("Inqr vector   : ",User_data[VInquiry])
    postI = decrypt2Int(inqV.polyval(inqr_poly))
    print("Conflict value: ",postI)
    CV = getConflictValue(inqV.polyval(inqr_poly))
    if CV > 0:
        print("Conflicting schedule: ", CV, " entries")
    else:
        print("No conflicting schedule, CV =", CV)

def makeUpdate(room, newValue):
    global FED_data, FED_encV
    FED_data[room] = newValue
    FED_encV[room] = ts.ckks_vector(FED_context, FED_data[room])
    
def makeReservation(encV, VTable, VReserve):
    #generate conflict status
    rsv_C = encV
    postI = decrypt2Int(rsv_C.polyval(inqr_poly))
    CV = getConflictValue(rsv_C.polyval(inqr_poly))
    #generate new table
    print("Init  ",VTable,": ",FED_data[VTable])
    print("Rsv vector    : ",User_data[VReserve])
    if CV == 0:
        print("No conflicting schedule, CV = ", CV)
        rsv_V = encV
        
        postComp = rsv_V.polyval(rsv_poly)
        #print( decrypt(postComp) )
        
        postR = decrypt2Int(postComp)
        makeUpdate(VTable, postR)
        print("Updated",VTable,":", postR)
        
    else:
        print("Conflict value: ",postI)
        print("Conflicting schedule: ", CV, " entries")
        print("Reservation table is not updated")
        print("post ",VTable," : ", FED_data["room_C"])

if __name__ == "__main__":
    import sys
    
    FED_context = genContext()
    FED_data = genData2()
    FED_encV = encryptData(FED_context, FED_data)
    
    User_context = genContext()
    User_data = genData2(True)
    User_encV = encryptData(User_context, User_data)

    FED2User_encV = encryptData(User_context, FED_data) #conflict checking
    User2FED_encV = encryptData(FED_context, User_data) #reservation purpose

    #polynomial function for evaluation(binary masking) a + bx + cx^2
    inqr_poly = [0, -0.5, 0.5]  #inquiry    : 0.5x^2 - 0.5x
    rsv_poly = [0, 0.5, 0.5]    #reservation: 0.5x^2 + 0.5x

    print("case 1, 1st reservation ")
    rsv1 = FED_encV["room_A"] - User2FED_encV["reserve1"]
    makeReservation(rsv1, "room_A",  "reserve1")
    
    print("case 2, 2nd reservation ")
    rsv1 = FED_encV["room_A"] - User2FED_encV["reserve2"]
    makeReservation(rsv1, "room_A",  "reserve2")
    
    print("case 3, 3rd reservation ")
    rsv1 = FED_encV["room_A"] - User2FED_encV["reserve3"]
    makeReservation(rsv1, "room_A",  "reserve3")
    
    print("case 4, 4th reservation ")
    rsv1 = FED_encV["room_A"] - User2FED_encV["reserve4"]
    makeReservation(rsv1, "room_A",  "reserve4")
    
    print("case 5, 5th reservation ")
    rsv1 = FED_encV["room_A"] - User2FED_encV["reserve5"]
    makeReservation(rsv1, "room_A",  "reserve5")
        
        
