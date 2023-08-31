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
                #5room,6slot:[1, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0], #reservation to room A, day 1
                "reserve1" : [1, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0], #reservation to room A, day 1
                "reserve2" : [0, 1, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0], #reservation to room A, day 1
                "reserve3" : [0, 0, 1, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0], #reservation to room A, day 1
                "reserve4" : [0, 0, 0, 0, 0, 0,   1, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0], #reservation to room B, day 2
                "reserve5" : [0, 0, 0, 0, 0, 0,   0, 1, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0,   0, 0, 0, 0, 0, 0], #reservation to room B, day 2
               }
    else: #reservation table
        data = {
                "day_1" : [1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1], #day 1
                "day_2" : [1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1,   1, 1, 1, 1, 1, 1], #day 2
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
    FED_data = genData()
    FED_encV = encryptData(FED_context, FED_data)
    
    User_context = genContext()
    User_data = genData(True)
    User_encV = encryptData(User_context, User_data)

    FED2User_encV = encryptData(User_context, FED_data) #conflict checking
    User2FED_encV = encryptData(FED_context, User_data) #reservation purpose

    #polynomial function for evaluation(binary masking) a + bx + cx^2
    inqr_poly = [0, -0.5, 0.5]  #inquiry    : 0.5x^2 - 0.5x
    rsv_poly = [0, 0.5, 0.5]    #reservation: 0.5x^2 + 0.5x

    print("case 1, 1st reservation ")
    rsv1 = FED_encV["day_1"] - User2FED_encV["reserve1"]
    makeReservation(rsv1, "day_1",  "reserve1")
    
    print("case 2, 2nd reservation ")
    rsv2 = FED_encV["day_1"] - User2FED_encV["reserve2"]
    makeReservation(rsv2, "day_1",  "reserve2")
    
    print("case 3, 3rd reservation ")
    rsv3 = FED_encV["day_1"] - User2FED_encV["reserve3"]
    makeReservation(rsv3, "day_1",  "reserve3")
    
    print("case 4, 4th reservation ")
    rsv4 = FED_encV["day_2"] - User2FED_encV["reserve4"]
    makeReservation(rsv4, "day_2",  "reserve4")
    
    print("case 5, 5th reservation ")
    rsv5 = FED_encV["day_2"] - User2FED_encV["reserve5"]
    makeReservation(rsv5, "day_2",  "reserve5")
    
