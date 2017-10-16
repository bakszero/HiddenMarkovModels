#NO NORMALISATION!
import sys, os, math, re, random, copy

def init_a(tag_list):
    a={}
    
    for i in tag_list:
        for j in tag_list:
            if i not in a:
                a[i]={}
            a[i][j]=random.random()
            

        a[i]['f']=random.random()
        #print "a[", i,a[i]['f']
    #Normalise data
    return a


def normalise_a(a, tag_list):
    sum=0.
    a_matrix = copy.deepcopy(a)
    for tag_1 in tag_list:
        for tag_2 in tag_list:
            sum+= a_matrix[tag_1][tag_2] 
        sum+= a_matrix[tag_1]['f']

    for tag_1 in tag_list:
        for tag_2 in tag_list:
            a_matrix[tag_1][tag_2] = float(a_matrix[tag_1][tag_2])/sum
        a_matrix[tag_1]['f'] = float(a_matrix[tag_1]['f'])/sum
        #print "normalising a...", tag_1, a_matrix[tag_1]['f']


    return a_matrix



def init_b(tag_list, line_list):
    b={}
    for sentence in line_list:
        
        for word in sentence:
            if word =='':
                continue
            for i in tag_list:
                if i not in b:
                    b[i]={}
                b[i][word]=random.random()

    return b

def normalise_b(b, tag_list, line_list):
    
    for sentence in line_list:
        
        
        for tag in tag_list:
            sum=0.
            for word in sentence:
                if word =='':
                    continue
                sum += b[tag][word]
            for word in sentence:
                if word == '':
                    continue
                b[tag][word] = b[tag][word] / sum
            
 
            #print "b", i, word, b[i][word]


    return b
                


def init_pi_and_normalise(tag_list):
    pi={}
    sum=0.
    for tag in tag_list:
        pi[tag]=random.random()
        sum+= pi[tag]

    for tag in tag_list:
        pi[tag] = pi[tag]/sum
    return pi

def normalise_b_internal(b, tag_list, sentence):
    #print line
    for tag in tag_list:
        sum=0.
        for word in sentence:
            sum += b[tag][word]
        for word in sentence:
            b[tag][word] = b[tag][word] / sum
    return b

def forward(a_matrix, b_matrix, pi, line, tag_list):
    fwd = {}
    ''' 
    It is of the format fwd[timestamp][tag]
    
            print "b [i][word]" , b_matri[i][word], sum
    '''
    
    #line  = line[0]
    
    for i, word in enumerate(line):
        if word == '':
            del line[i]

    #First make the dict of dicts for len of line_list
    for i in range(1,len(line)+1):
        fwd[i]={}
    
    #Now initialise the first timestamp probs
    #Make a dict of c values for scaling
    c={}
    #Also intialise c[1] along with it
    c[1] = 0. 
    for tag in tag_list:
        fwd[1][tag]=pi[tag]*b_matrix[tag][line[0]]
        c[1] = c[1] + fwd[1][tag]
    #Scale the fwd[1]
    c[1] = 1./ c[1]

    for tag in tag_list:
        fwd[1][tag] = (c[1] * fwd[1][tag])    

    
    #Now run the algorithm
    for i in range(2, len(line)+1):
        c[i] = 0.
        j = i-1
        for tag_pres in tag_list:
            fwd[i][tag_pres]=0.
            for tag_prev in tag_list: 
                #print fwd[i][tag_pres]
                #print fwd[j][tag_prev]
                #print a_matrix[tag_prev][tag_pres]
                
                fwd[i][tag_pres] += (fwd[j][tag_prev] * a_matrix[tag_prev][tag_pres]  )
            fwd[i][tag_pres] = fwd[i][tag_pres]* b_matrix[tag_pres][line[j]]
            #print i, tag_pres, "fwd", fwd[i][tag_pres]
            c[i] = c[i] + fwd[i][tag_pres]
         
        #Scale fwd[i][tag]
        #print i, "c[i]", c[i]
        
        c[i] = 1./c[i]

        for tag in tag_list:
            fwd[i][tag] = (c[i] * fwd[i][tag])
        
    
    #Final layer computation
    x = len(line)+1
    fwd[x]=0.

    for tag in tag_list:
        #Everyone receives summation lol!

        fwd[x] += (fwd[x-1][tag] * a_matrix[tag]['f'])
        #print "fwd[x]" , fwd[x]
        #print "FWD[x]" ,  x, tag,fwd[x-1][tag], a_matrix[tag]['f'], fwd[x]
    
    return fwd, c        

def backward(a_matrix, b_matrix, pi, line, tag_list, c ):
    backwd = {}
    ''' 
    It is of the format backwd[timestamp][tag]
    
    '''
    
    #line  = line[0]
    for i, word in enumerate(line):
        if word == '':
            del line[i]

    #print line


    #First make the dict of dicts for len of line_list
    for i in range(1,len(line)+1):
        backwd[i]={}
    
    #Now initialise the T timestamp probs
    for tag in tag_list:
        backwd[len(line)][tag]=c[len(line)]
    #Now run the algorithm
    for i in range(len(line)-1, 0, -1):
        j = i+1
        for tag_pres in tag_list:
            backwd[i][tag_pres]=0.
            for tag_future in tag_list: 
                #print fwd[i][tag_pres]
                #print fwd[j][tag_prev]
                #print a_matrix[tag_prev][tag_pres]
                
                backwd[i][tag_pres] += (backwd[j][tag_future] * a_matrix[tag_pres][tag_future] * b_matrix[tag_future][line[i]] )

            #Scale backwd[i][tag] with same scale factor as fwd[i][tag] and we have passed c here!
            backwd[i][tag_pres] = (c[i] * backwd[i][tag_pres] )
    
    #Final layer computation, well this actually does not matter!
    x = 0
    backwd[x]=0.
    

    for tag in tag_list:
        #Everyone receives summation lol!
        backwd[x] += (backwd[x+1][tag] * pi[tag])
    
    return backwd


def compute_eta(a_matrix, b_matrix, fwd, backwd, tag_list , line):

    #Cleanse the data line first
    for i, word in enumerate(line):
        if word == '':
            del line[i]
    #INITIALISATION OF ETA dict.
    eta={}
    for i in range(1, len(line)+1):
        eta[i]={}
        for tag in tag_list:
            eta[i][tag] = {}
    

    #Side algo

    #Algorithm computation
    for i  in range(1, len(line)):
        for tag_1 in tag_list:
            for tag_2 in tag_list:
                #print "eta"
                
                eta[i][tag_1][tag_2] = float(fwd[i][tag_1] * backwd[i+1][tag_2] * a_matrix[tag_1][tag_2] * b_matrix[tag_2][line[i]]) /fwd[len(line)+1]
                #print eta[i][tag_1][tag_2]
            
    return eta

def compute_gamma(fwd, backwd, tag_list, line):
    #Cleanse the data line first
    for i, word in enumerate(line):
        if word == '':
            del line[i]

    #Initialise the gamma values
    gamma = {}
    for i in range(1, len(line)+1):
        gamma[i]={}
    
    #Algorithm computation
    for i in range(1, len(line)+1):
        for tag in tag_list:
            #print "fwd", fwd[i][tag] , backwd[i][tag] , fwd[len(line)+1]
            gamma[i][tag] = (fwd[i][tag] * backwd[i][tag]) / fwd[len(line)+1]
    
    return gamma
    
def expt_compute_eta_and_gamma(a_matrix, b_matrix, fwd, backwd,tag_list, line):
    #Cleanse the data line first
    for i, word in enumerate(line):
        if word == '':
            del line[i]
    #INITIALISATION OF ETA dict.
    eta={}
    for i in range(1, len(line)+1):
        eta[i]={}
        for tag in tag_list:
            eta[i][tag] = {}
    
    #Initialise the gamma values
    gamma = {}
    for i in range(1, len(line)+1):
        gamma[i]={}

    #Algorithm
    for time in range(1, len(line)):
        denom=0.
        for tag_1 in tag_list:
            for tag_2 in tag_list:
                denom = denom + (fwd[time][tag_1]*a_matrix[tag_1][tag_2]*b_matrix[tag_2][line[time]]*backwd[time+1][tag_2])

        
        for tag_1 in tag_list:
            gamma[time][tag_1]=0.
            for tag_2 in tag_list:
                eta[time][tag_1][tag_2] = (fwd[time][tag_1]*a_matrix[tag_1][tag_2]*b_matrix[tag_2][line[time]]*backwd[time+1][tag_2])
                gamma[time][tag_1] = gamma[time][tag_1] + eta[time][tag_1][tag_2]

    #Special case for gamma[T][tag]
    denom=0.
    for tag in tag_list:
        denom = denom + fwd[len(line)][tag]
    for tag in tag_list:
        gamma[len(line)][tag] = fwd[len(line)][tag]/denom

    return eta , gamma



def baum_welch(a_matrix, b_matrix, pi, tag_list, line_list):

    #Take the first element of the list now
    #line = line_list[0]
    for k , line in enumerate(line_list):
        
        if line=='':
            continue
        print "We are at iteration..." , k
        print "Sentence is :" , line
        temp_line = line
        #Cleanse the data line first
        for i, word in enumerate(line):
            if word == '':
                del line[i]
        #Iterate for a fixed no. of steps for one observation here
        iterations = 0 
        while(iterations < 10 ):
            print "..........", iterations
            
            #E-STEP
            fwd, c = forward(a_matrix, b_matrix, pi, line, tag_list)
            backwd = backward(a_matrix, b_matrix, pi, line, tag_list, c)
            gamma = compute_gamma(fwd, backwd, tag_list, line)
            eta = compute_eta(a_matrix, b_matrix, fwd, backwd, tag_list , line)

            #M-STEP

            old_a_matrix = copy.deepcopy(a_matrix)
            old_b_matrix = copy.deepcopy(b_matrix)

            
            ###############################Experimental only#################
            #eta, gamma = expt_compute_eta_and_gamma(a_matrix, b_matrix, fwd, backwd,tag_list, line)
            #Similar underflow with scaling as well.



            ##################################################################

            for tag_1 in tag_list:
                for tag_2 in tag_list:
                    num=0.
                    den=0.
                    for time in range(1, len(line)):
                        num += eta[time][tag_1][tag_2]
                        den += gamma[time][tag_1]
                        for temp_tag in tag_list:
                            den  += eta[time][tag_1][temp_tag]

                    #print "den is", den
                    a_matrix[tag_1][tag_2] = num/(den) 


            for tag in tag_list:
                for word in line:
                    num=0.
                    den=0.
                    for time in range(1, len(line)+1):
                        if line[time-1]==word:
                            num += gamma[time][tag]
                        den += gamma[time][tag]
                    #print "num", num
                    #print "den", den
                    b_matrix[tag][word]  = num/den
                    #print "b_maatrix" , tag, word, b_matrix[tag][word]

                #print tag,b_matrix[tag]['the']
            #a_matrix = normalise_a(a_matrix, tag_list)
            #b_matrix = normalise_b_internal(b_matrix, tag_list, temp_line)
            iterations+=1

    return a_matrix, b_matrix


def pos_tags():
    tag_list  = ['NP', 'NN', 'JJ', 'IN', 'VB', 'TO', 'DT', 'PRP', 'RB', 'CC']
    return tag_list

def tokenize(filename):
    '''
    Declare a list of lists for each file and return the list of lists.
    '''
    line_list = []
    
    '''
    Define the regex for compiling only alpha-numeric characters.
    '''

    regex = re.compile('[\W]+')

    #Scraping through the text file
    with open(filename, 'r') as f:
        for line in f:
            line = line.split(' ')
            
            if line[0].startswith("#"):
                continue
            #Only alpha-numeric characters
            for i, word in enumerate(line):
                line[i] = re.sub('[^a-zA-Z0-9]+', '', line[i])
                
                #Convert it into lowercase
                line[i] = line[i].lower()
                #If empty string is processed
                if line[i]=='':
                    del line[i]
            #print line

            if not line:
                continue
            
            line_list.append(line)

    return line_list            







if __name__ == '__main__':
    
    '''
    Brown Corpus used for the following:
    Dataset downloaded from http://www.sls.hawaii.edu/bley-vroman/brown_nolines.txt
    '''
    filename='brown_nolines.txt'

    '''
    Load the lines in the line_list variable
    '''
    line_list = tokenize(filename)

    '''
    Get the tag list of POS tags. The 10 list
    '''
    tag_list =  pos_tags()

    a_matrix = init_a(tag_list)
    #a_matrix =  normalise_a(a_matrix, tag_list)
    b_matrix = init_b(tag_list, line_list)
    #b_matrix = normalise_b(b_matrix, tag_list, line_list)
    pi = init_pi_and_normalise(tag_list)

    #print pi
    #fwd = forward(a_matrix, b_matrix, pi, line_list, tag_list)
    #backwd = backward(a_matrix, b_matrix, pi, line_list, tag_list)
    #print backwd

    #eta = compute_eta(a_matrix, b_matrix, fwd, backwd, tag_list , line_list[0])
    #gamma  = compute_gamma(fwd, backwd, tag_list, line_list[0])
    #print eta
    a_matrix, b_matrix = baum_welch(a_matrix, b_matrix, pi, tag_list, line_list)

    with open('final_temp__A_B.txt', 'w+') as m:
        m.write("A Matrix\n")
        for tag_1 in tag_list:
            for tag_2 in tag_list:
                m.write(tag_1+ "->"+tag_2+" "+str(a_matrix[tag_1][tag_2])+'\n')


        m.write("B Matrix\n")
        for line in line_list:
           
            for word in line:
                for tag in  tag_list:
                    m.write(tag+ "->"+word+" "+str(b_matrix[tag][word])+'\n')




