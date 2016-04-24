import os
import sys
from stop_words import get_stop_words
from collections import Counter
import string
import bs4
import math

################################################################################
#################  MACHINE LEARNING PROJECT ON SPAM FILTERS  ###################
################################################################################

spam_dict = {}   # Dictionary of words along with their frequency in spam emails
ham_dict = {}    # Dictionary of words along with their frequency in spam emails
spamicity = {}   # Dictionary of words along with their spamicity
correct_ans = 0
total_mails = 0
spam_threshold = 80    # Threshold value for classifying email as spam
epsilon = 0.00001        # A small number to remove cases of 0 and 1 probability
spam_true = 0			
spam_false = 0			
predicted_positive = 0
predicted_negative = 0
true_positive = 0
true_negative = 0
false_positive = 0
false_negative = 0
RARE_WORD = 5           
RARE_WORD_WEIGHT = 3


# non-spam mails have been referred to as Ham
# this function applies formula for naive bayesian spam filtering
def bayer_formula(temp_list , frequency_list):
	
	fact1 = 1.0
	fact2 = 1.0
	for i in temp_list:
		fact1 = fact1 * i
		fact2 = fact2 * (1-i)

	if ((fact1+fact2) == 0):
		return 0.1

	return ( fact1/(fact1+fact2))


# this function takes the dictionary made from a input email set
# and appends features to the list whose | 0.5 - p | >= 0.3
# the list has features which strongly classify a mail as spam or ham

def bayer(test_dict , label):
	temp_list = []
	frequency_list = []
	global correct_ans , total_mails , spam_threshold , epsilon , predicted_positive , predicted_negative 
	global false_positive , false_negative , true_positive , true_negative
	for i in test_dict.keys():
	    if spamicity.has_key(i):
	    	if (math.fabs(0.5 - spamicity[i]) >= 0.3):    # ignoring words with spamicity between 0.2 and 0.8
	    		if ((spam_dict[i]+ham_dict[i])<= RARE_WORD):
	    			temp_list.append ((RARE_WORD_WEIGHT*0.5 + test_dict[i] * spamicity[i])/(RARE_WORD_WEIGHT+test_dict[i]))
	    		elif (spamicity[i] == 0):
	    			temp_list.append(epsilon) 			
	    			
	    		elif (spamicity[i] == 1 ):
	    			temp_list.append(1-epsilon)
	    			
	    		else:
	    			temp_list.append(spamicity[i])
	    			
	            	


	if (len (temp_list) >= 1):
		result = ( bayer_formula(temp_list , frequency_list) )* 100
		if (result > spam_threshold):
			predicted_positive += 1
			if ( label == "SPAM"):
				true_positive+=1
				correct_ans += 1
			else:
				false_positive += 1

		else :
			predicted_negative += 1
			if ( label == "HAM"):
				false_negative += 1
				correct_ans +=1 
			else:
				true_negative +=1
			
		
		total_mails+=1

		

# returns a dictionary of features of the input email 

def word_list(text ) :

    list = {}
    words = text.split()
    stop_words = get_stop_words('en')          # stop words is a list of common words used in English
    stop_words = get_stop_words('english')     

    words = [word for word in words if word not in stop_words]    #removing stop words

    for i in words:
        if all(j.isdigit() for j in i):     # classifing token as number feature
            if list.has_key("NUMBER"):
                list["NUMBER"]+=1
            else:
                list["NUMBER"]=1

        elif (len (i) >=4 and i[0] == 'h' and i[1] == 't' and i[2] == 't' and i[3] == 'p'):
        	if list.has_key("LINKS"):     # classifing token as link feature
        		list["LINKS"]+=1
        	else:
        		list["LINKS"]=1
        	

        elif all(j in string.punctuation for j in i):
            if list.has_key("PUNCTUATION"):        # classifing token as punctuation feature
                list["PUNCTUATION"]+=1
            else:
                list["PUNCTUATION"]=1

        elif len(i.translate(None,string.punctuation)) < 3:
            continue

        elif i.upper()==i:
            if list.has_key("CAPSLOCK"):        # classifing token as capital word feature
                list["CAPSLOCK"]+=1
            else:
                list["CAPSLOCK"]=1
        
        else:
            j = i.translate(None,string.punctuation).lower()
            if list.has_key(j):
                list[j]+=1
            else:
                list[j]=1
            
    
    
    return list


# seletively adds the dictionary to either spam_dictionary or ham_dictionary

def filter(text,label):
	global spam_dict , ham_dict
	dict = Counter(word_list(text))   
	    
	if label == "SPAM":
	    spam_dict = Counter(spam_dict)
	    spam_dict = dict + spam_dict
	    
	        
	if label == "HAM":
	    ham_dict = Counter(ham_dict)
	    ham_dict = dict + ham_dict


# calculates the spamicity of each feature present in either ham dictionary or spam dictionary

def calcSpamicity():	
	global spamicity    

	for i in spam_dict.keys():
        
	    if ham_dict.has_key(i):
	        spamicity[i] = (float)(spam_dict[i])/(spam_dict[i]+ham_dict[i])
	    else :
	        spamicity[i] = 1

	for i in ham_dict.keys():

	    if spam_dict.has_key(i):
	        spamicity[i] = (float)(spam_dict[i])/(spam_dict[i]+ham_dict[i])
	    else :
	        spamicity[i] = 0

	
# this function calls the required functions neded for testing

def testing(text,label) :       

	test_dict = word_list(text)
	bayer(test_dict , label)  



# this fucntion extracts the email from the given source path
 

def extractEmail (src_dir , label , test):
	global spam_false , spam_true
	if not os.path.exists(src_dir):
		print ("Source directory does not exist... ")
		sys.exit()
	files_in_directory = os.listdir(src_dir)

	for file in files_in_directory:
		src_path = os.path.join(src_dir, file)
		if not os.path.exists(src_path): 
			print ("File does not exist")
			continue
		
		
		fp = open (src_path , 'r')
		text = fp.read()
		try:
			text = bs4.UnicodeDammit.detwingle(text).decode('utf-8')
		except:
			continue
		text = text.encode('ascii', 'ignore')

		if (label == "HAM"):
			spam_false += 1
		elif ( label == "SPAM"):
			spam_true += 1

		if test==0:
			filter(text,label)
		else:
			testing(text,label)



			



def main():
	global correct_ans , total_mails , spam_true , spam_false , predicted_positive , predicted_negative
	print ("Machine Learning Project on Spam Filter")
	print ("Input Source Directory for Ham :")
	src_dir = raw_input()
	extractEmail(src_dir , "HAM" , 0)
	print ("Input Source Directory for Spam :")
	src_dir = raw_input()
	extractEmail(src_dir , "SPAM" , 0)
	calcSpamicity()

	print ("\n\nTraining over...\n\n")

	print ("Input Source Directory for Testing Ham :")
	src_dir = raw_input()
	extractEmail(src_dir , "HAM" , 1)

	
	

	print ("Input Source Directory for Testing Spam :")
	src_dir = raw_input()
	extractEmail(src_dir , "SPAM" , 1)

	print ("accuracy for test cases ")
	print ((float)((correct_ans+0.0)/total_mails) * 100)


	print ("false positive ratio is ")
	print ((false_positive+0.0)/(predicted_positive))
	
	print ("false negative ratio is ")
	print ((false_negative+0.0)/(predicted_negative))
	
	print ("true positive ratio is ")
	print ((true_positive+0.0)/(predicted_positive))
	
	print ("true negative ratio is ")
	print ((true_negative+0.0)/(predicted_negative))
	

if __name__ == '__main__':
 	main()