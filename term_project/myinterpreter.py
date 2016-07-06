######## SECTION 1 ########

import sys
import re
import time

FLOAT, STRING, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, LCBRACKET, RCBRACKET, ASSIGN, SEMIC, COMA, IF, ELSE, FOR, WHILE, ID, METHOD, LEQ, LT, GEQ, GT, EQ, NEQ, AND, OR = (
    'FLOAT', 'STRING', 'PLUS', 'MINUS', 'MUL', 'DIV', 'LPAREN', 'RPAREN', 'LCBRACKET', 'RCBRACKET' ,'ASSIGN', 'SEMIC', 'COMA' ,'IF', 
    'ELSE', 'FOR', 'WHILE', 'ID', 'METHOD', 'LEQ', 'LT', 'GEQ', 'GT', 'EQ', 'NEQ', 'AND', 'OR'
)

token_exprs = [
    (r'[ \n\t]+',              None),
    (r'%[^\n]*',               None),
    (r'\"[^\n]*\"',            STRING),
    (r'\<-',                   ASSIGN),
    (r'\(',                    LPAREN),
    (r'\)',                    RPAREN),
    (r'\{',                    LCBRACKET),
    (r'\}',                    RCBRACKET),
    (r';',                     SEMIC),
    (r',',                     COMA),
    (r'\+',                    PLUS),
    (r'-',                     MINUS),
    (r'\*',                    MUL),
    (r'/',                     DIV),
    (r'<=',                    LEQ),
    (r'<',                     LT),
    (r'>=',                    GEQ),
    (r'>',                     GT),
    (r'=',                     EQ),
    (r'!=',                    NEQ),
    (r'and',                   AND),
    (r'or',                    OR),
    (r'if',                    IF),
    (r'else',                  ELSE),
    (r'for',                   FOR),
    (r'while',                 WHILE),
    (r'[0-9]+([.][0-9]+)?',    FLOAT),
    (r'[a-z][A-Za-z0-9_]*',    ID),
    (r'[A-Z][A-Za-z0-9_]*',    METHOD),
]

#we create a symbol table by the use of a dictionary, which is a hash table indexed by the hash value of the identifier, and which entry contains the current value of that identifier
stable={}


######## SECTION 2 ########

class Token(object): #each token is defined by an object with two attributes (token type and token value)
    def __init__(self, type, value):
        self.type = type #token type: FLOAT, PLUS, MINUS, MUL, DIV...
        self.value = value #token value: FLOAT value, '+', '-', '*', '/'...


def lex(characters, token_exprs):
    pos = 0 #we start by the first character
    tokens = [] #we initialize the vector of tokens (vector of subtokens, delimited by ";")
    subtokens = [] #we initialize the vector of subtokens
    while pos < len(characters):
        match = None
        for token_expr in token_exprs: #we check for each row of the regular expressions list if it matches our text
            pattern, tag = token_expr #we divide each row into a "pattern" and a "tag"
            regex = re.compile(pattern) #we make use of the method "compile" and "match" from "re" library to match patterns to our text
            match = regex.match(characters, pos)
            if match: #when a match is found...
                text = match.group(0) #...we save the value of the token found
                if tag: #and in case that the tag is not "None"...
                    if tag==ID:
                        if not (text in stable): #if the identifier is not in the symbol table 
                            stable[text]=None #we create an empty entry in it with the identifier name as the key value
                    token = Token(tag,text) #...we create a token object with the value of the token found and its type (the type of the reg exp used)

                    if tag==SEMIC:
                        tokens.append(subtokens)
                        subtokens = []
                    else:
                        subtokens.append(token) #then we append this token to the tokens vector...
                break #...and we stop checking the regular expression lists (we exit the "for token_expr in token_exprs" loop)
        if not match: #if we finished traversing the regular expression list and we have not found any match...
            sys.stderr.write('Illegal character: %s\\n' % characters[pos]) #...we inform of the error and stop the program
            sys.exit(1)
        else: #but if the search succeeded we save the position of the last character of the match as the position from where we will start the new search 
            pos = match.end(0)
    # for token in tokens: #THIS IS TO TEST AND SEE THE TOKEN LIST
    #     for aa in token:
    #         print(aa.value,aa.type)
    #     print("---")
    return tokens #when we have finished traversing all characters of the file (we exit the "while pos < len(characters)" loop ) we return the "tokens" vector.


######## SECTION 3 ########

class Interpreter(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens[0] # set current token to the first token taken from the input
        self.pos = 0
        self.methodDict = {
            'Mod': self.mModulus,
            'Disp': self.mDisplay,
            'Bitshift': self.mBitshift
        }

    def mModulus(self,argumentsVector):
        return (Interpreter(argumentsVector[0]).expr()%Interpreter(argumentsVector[1]).expr())

    def mDisplay(self,argumentsVector):
        ToBePrinted=""
        for argument in argumentsVector:
            ToBePrinted=ToBePrinted+str(Interpreter(argument).expr())
        print(ToBePrinted)

    def mBitshift(self,argumentsVector):
        return None

    def error(self,text):
        raise Exception(text)

    def eat(self):
        # "eat" the current token and assign the next token to the self.current_token
        if self.pos+1 < len(self.tokens):
            self.pos=self.pos+1
            self.current_token = self.tokens[self.pos]  

    def expr(self):
        result = None

        if self.current_token.type == ID and len(self.tokens) > 1 and self.tokens[self.pos+1].type == ASSIGN: #if the expression starts with an ID followed by an assignment
            #print("assign found")
            AssignExpr=self.tokens[self.pos+2:] #we save as a vector of tokens the right part of the assignment
            interpreterAssignExpr = Interpreter(AssignExpr) #we create an object of the class Interpreter, initialized with the vector of tokens that conform the assignment expression
            stable[self.current_token.value]=interpreterAssignExpr.expr()  #process and save whole expressions
            return(stable[self.current_token.value])

        elif self.current_token.type in (ID, FLOAT, LPAREN, MINUS): #if the expression starts with either an ID (not followed by an assignment), a number, a minus or a left parenthesis it means that it's an arithmetic operation
            if len(self.tokens) == 1: #if the length of the expression is only one we just return its value
                if self.current_token.type == ID: #in case it was an identifier we return its value from the symbol table
                    #print("identifier call found")
                    return(float(stable[self.current_token.value]))
                else: #and in case it was a float we just return it
                    return(float(self.current_token.value))
            else: #however if the length of the expression is more than 1 we have to separate the terms
                plevel=0 #parentheses level initialized to 0
                andorfound=False #has an operator AND|OR been found outside a parentheses during the while loop?
                compfound=False #has an operator <|<=|>|>=|=|!= been found outside a parentheses during the while loop?
                plusfound=False #has an operator PLUS been found outside a parentheses during the while loop?
                minusfound=False #has an operator MINUS been found outside a parentheses during the while loop?
                muldivfound=False #has an operator MUL|DIV been found outside a parentheses during the while loop?
                   
                while (not andorfound) and self.pos < (len(self.tokens)-1): #while an operator has not been legally found and we haven't reached the end of the expression
                    if (self.current_token.type in (AND,OR)) and plevel==0: #if we find an operator outside parentheses
                        andorfound=True
                        leftexpr=Interpreter(self.tokens[:self.pos]).expr()
                        rightexpr=Interpreter(self.tokens[self.pos+1:]).expr()
                        if self.current_token.type == AND:
                            return bool(leftexpr and rightexpr)
                        else:
                            return bool(leftexpr or rightexpr)
                    elif self.current_token.type == LPAREN:
                        plevel=plevel+1
                    elif self.current_token.type == RPAREN:
                        plevel=plevel-1
                    self.eat()

                if not andorfound: #if an AND or an OR hasn't been found outside parentheses we have to search again, this time looking for comparison operators outside parentheses
                    self.pos=0
                    self.current_token=self.tokens[0]
                    plevel=0 #parentheses level initialized to 0    
                    while (not compfound) and self.pos < (len(self.tokens)-1): #while an operator has not been legally found and we haven't reached the end of the expression
                        if (self.current_token.type in (LEQ, LT, GEQ, GT, EQ, NEQ)) and plevel==0: #if we find an operator outside parentheses
                            compfound=True
                            leftexpr=Interpreter(self.tokens[:self.pos]).expr()
                            rightexpr=Interpreter(self.tokens[self.pos+1:]).expr()
                            if self.current_token.type == LEQ:
                                return bool(leftexpr <= rightexpr)
                            elif self.current_token.type == LT:
                                return bool(leftexpr < rightexpr) 
                            elif self.current_token.type == GEQ:
                                return bool(leftexpr >= rightexpr)
                            elif self.current_token.type == GT:
                                return bool(leftexpr > rightexpr)
                            elif self.current_token.type == EQ:
                                return bool(leftexpr == rightexpr)
                            else:
                                return bool(leftexpr != rightexpr)       
                        elif self.current_token.type == LPAREN:
                            plevel=plevel+1
                        elif self.current_token.type == RPAREN:
                            plevel=plevel-1
                        self.eat()

                    if not compfound: #if a comparison operator hasn't been found outside parentheses we have to search again, this time looking for PLUS outside parentheses
                        self.pos=0
                        self.current_token=self.tokens[0]
                        plevel=0 #parentheses level initialized to 0    
                        while (not plusfound) and self.pos < (len(self.tokens)-1): #while an operator has not been legally found and we haven't reached the end of the expression
                            if self.current_token.type == PLUS and plevel==0: #if we find an operator outside parentheses
                                plusfound=True
                                leftexpr=Interpreter(self.tokens[:self.pos]).expr()
                                rightexpr=Interpreter(self.tokens[self.pos+1:]).expr()
                                return(leftexpr+rightexpr)
                            elif self.current_token.type == LPAREN:
                                plevel=plevel+1
                            elif self.current_token.type == RPAREN:
                                plevel=plevel-1
                            self.eat()

                        if not plusfound: #if a plus hasn't been found outside parentheses we have to search again, this time looking for mult and div outside parentheses
                            self.pos=0
                            self.current_token=self.tokens[0]
                            plevel=0 #parentheses level initialized to 0
                            while (not minusfound) and self.pos < (len(self.tokens)-1): #while an operator has not been legally found and we haven't reached the end of the expression
                                if self.current_token.type == MINUS and plevel==0: #if we find an operator outside parentheses
                                    minusfound=True
                                    if self.pos > 0:
                                        leftexpr=Interpreter(self.tokens[:self.pos]).expr()
                                    else:
                                        leftexpr=0
                                    rightexpr=Interpreter(self.tokens[self.pos+1:]).expr()
                                    return(leftexpr-rightexpr)
                                elif self.current_token.type == LPAREN:
                                    plevel=plevel+1
                                elif self.current_token.type == RPAREN:
                                    plevel=plevel-1
                                self.eat()
                            if not minusfound: #if neither a plus or minus has been found outside parentheses we have to look for multiplication and division
                                self.pos=0
                                self.current_token=self.tokens[0]
                                plevel=0 #parentheses level initialized to 0
                                while (not muldivfound) and self.pos < (len(self.tokens)-1): #while an operator has not been legally found and we haven't reached the end of the expression
                                    if (self.current_token.type in (MUL,DIV)) and plevel==0: #if we find an operator outside parentheses
                                        muldivfound=True
                                        if self.current_token.type==MUL:
                                            leftexpr=Interpreter(self.tokens[:self.pos]).expr()
                                            rightexpr=Interpreter(self.tokens[self.pos+1:]).expr()
                                            return(leftexpr*rightexpr)
                                        else:
                                            leftexpr=Interpreter(self.tokens[:self.pos]).expr()
                                            rightexpr=Interpreter(self.tokens[self.pos+1:]).expr()
                                            return(leftexpr/rightexpr)
                                    elif self.current_token.type == LPAREN:
                                        plevel=plevel+1
                                    elif self.current_token.type == RPAREN:
                                        plevel=plevel-1
                                    self.eat()
                                if not muldivfound: #however, if neither a plus, minus, mul or div has been found outside parentheses we have to take out the parentheses and evaluate its content
                                    return(Interpreter(self.tokens[1:len(self.tokens)-1]).expr())


        elif self.current_token.type == STRING:
            return (self.current_token.value[1:len(self.current_token.value)-1]) #we return the string but we take out the quotes at both sides of it

        ##########   BEGINNING OF "IF-ELSE" CLAUSE  ########## if (pred) {body of if} else {body of else}
        elif self.current_token.type == IF:
            subtokensIfBody=[] #initialize the vector containing the token in the "if" body
            subtokensElseBody=[] #initialize the vector containing the token in the "else" body
            elseClause=False #flag to determine if there's "else" clause or not

            self.eat() #we eat the if
            self.eat() #we eat the left parenthesis
            subtokens=[]
            plevel=1 #parentheses level initialized to 0

            while plevel>0:  #we create a vector of tokens that conform the predicate
                if self.current_token.type == LPAREN:
                    plevel=plevel+1
                elif self.current_token.type == RPAREN:
                    plevel=plevel-1

                if plevel > 0:
                    subtokens.append(self.current_token)
                    self.eat()

            self.eat() #we eat the right parenthesis when we finish with the predicate
            self.eat() #we eat the left curly bracket of the "if" body
            clevel=1 #curly bracket level initialized to 1
            tempvector=[]
            inipos=self.pos #position of the first token of the "if" body
            endpos=self.pos
            while clevel>0: #while we don't find the final right curly bracket...
                if self.current_token.type in (LCBRACKET,LPAREN):
                    clevel=clevel+1
                    tempvector.append(self.current_token)
                    self.eat()
                elif self.current_token.type in (RCBRACKET,RPAREN):
                    clevel=clevel-1
                    if clevel==0:
                        endpos=self.pos
                        subtokensIfBody.append(tempvector)
                    else:
                        tempvector.append(self.current_token)
                        self.eat()
                else:
                    if self.current_token.type==COMA and clevel==1:
                        subtokensIfBody.append(tempvector)
                        tempvector=[]
                    else:
                        tempvector.append(self.current_token)
                    self.eat()

            if inipos==endpos:
                self.error("Body of the if clause can't be empty")
            elif len(subtokensIfBody) == 0:
                    self.error("Coma expected at the end of each \"if\" body expression")
            
            if (self.pos+1) != len(self.tokens): #if we are not at the last token of the expression means that there is an "else" clause afterwards
                elseClause=True
                self.eat() #we eat the closing curly bracket of the "if" body and point to the "else" clause
                self.eat() #we eat the "else" clause and point to the left curly bracket of the body
                self.eat() #we eat the left curly bracket of the "else" body and point to the first token of the body
                clevel=1
                tempvector=[]
                inipos=self.pos #position of the first token of the "else" body
                endpos=self.pos
                while clevel>0: #while we don't find the final right curly bracket...
                    if self.current_token.type in (LCBRACKET,LPAREN):
                        clevel=clevel+1
                        tempvector.append(self.current_token)
                        self.eat()
                    elif self.current_token.type in (RCBRACKET,RPAREN):
                        clevel=clevel-1
                        if clevel==0:
                            endpos=self.pos
                            subtokensElseBody.append(tempvector)
                        else:
                            tempvector.append(self.current_token)
                            self.eat()
                    else:
                        if self.current_token.type==COMA and (clevel==1):
                            subtokensElseBody.append(tempvector)
                            tempvector=[]
                        else:
                            tempvector.append(self.current_token)
                        self.eat()
                if inipos==endpos:
                    self.error("Body of the else clause can't be empty")
                elif len(subtokensElseBody) == 0:
                    self.error("Coma expected at the end of each \"else\" body expression")

            if Interpreter(subtokens).expr():
                result = "Pred true"
                for line in subtokensIfBody:
                    interpreterLine = Interpreter(line) #we create an object of the class Interpreter, initialized with the vector of tokens that conform the line
                    resultLine = interpreterLine.expr() 
                    #print(resultLine)
                                    
            elif elseClause: #if the predicate is not true we have to check if there is an else, and in that case we execute its body
                result = "Pred false"
                for line in subtokensElseBody:
                    interpreterLine = Interpreter(line) #we create an object of the class Interpreter, initialized with the vector of tokens that conform the line
                    resultLine = interpreterLine.expr() 
                    #print(resultLine)
            else:
                result="Pred false and no Else clause"
        ##########   END OF "IF-ELSE" CLAUSE  ##########

        ##########   BEGINNING OF "FOR" CLAUSE  ########## for (initialization, eval, update,) {body of the for}
        elif self.current_token.type == FOR:
            subtokensForPred=[] #initialize the vector containing the tokens in the "for" predicate
            subtokensForBody=[] #initialize the vector containing the tokens in the "for" body
            self.eat() #we eat the "for"
            self.eat() #we eat the left parenthesis
            tempVectorPred=[]
            while self.current_token.type!=RPAREN: #we create a vector of tokens that conform the predicate
                if self.current_token.type==COMA:
                    subtokensForPred.append(tempVectorPred)
                    tempVectorPred=[]
                else:
                    tempVectorPred.append(self.current_token)
                self.eat()
            subtokensForPred.append(tempVectorPred) #we append the last argument found before the right parenthesis

            self.eat() #we eat the right parenthesis when we finish with the predicate
            self.eat() #we eat the left curly bracket of the "for" body
            clevel=1
            tempvector=[]
            inipos=self.pos #position of the first token of the "for" body
            endpos=self.pos
            while clevel>0: #while we don't find the final right curly bracket...
                if self.current_token.type in (LCBRACKET,LPAREN):
                    clevel=clevel+1
                    tempvector.append(self.current_token)
                    self.eat()
                elif self.current_token.type in (RCBRACKET,RPAREN):
                    clevel=clevel-1
                    if clevel==0:
                        endpos=self.pos
                        subtokensForBody.append(tempvector)
                    else:
                        tempvector.append(self.current_token)
                        self.eat()
                else:
                    if self.current_token.type==COMA and clevel==1:
                        subtokensForBody.append(tempvector)
                        tempvector=[]
                    else:
                        tempvector.append(self.current_token)
                    self.eat()

            if inipos==endpos:
                self.error("Body of the for clause can't be empty")
            elif len(subtokensForBody) == 0:
                self.error("Coma expected at the end of each \"for\" body expression")

            Interpreter(subtokensForPred[0]).expr() #we create an object of the class Interpreter, initialized with the vector of tokens that conform the initialization of the predicate

            while Interpreter(subtokensForPred[1]).expr(): #while the condition of the "for" predicate is true...
                for line in subtokensForBody: #...we execute all the lines inside its body
                    interpreterLine = Interpreter(line) #we create an object of the class Interpreter, initialized with the vector of tokens that conform the line
                    resultLine = interpreterLine.expr() 
                    #print(resultLine)
                Interpreter(subtokensForPred[2]).expr() #and at the end of the body we execute the update part of the predicate    
            result = "For loop finished execution"            
        ##########   END OF "FOR" CLAUSE  ##########

        ##########   BEGINNING OF "WHILE" CLAUSE  ########## while (pred) {body of while}
        elif self.current_token.type == WHILE:
            subtokensWhileBody=[] #initialize the vector containing the token in the "while" body

            self.eat() #we eat the while
            self.eat() #we eat the left parenthesis
            subtokens=[]
            plevel=1 #parentheses level initialized to 0

            while plevel>0:  #we create a vector of tokens that conform the predicate
                if self.current_token.type == LPAREN:
                    plevel=plevel+1
                elif self.current_token.type == RPAREN:
                    plevel=plevel-1

                if plevel > 0:
                    subtokens.append(self.current_token)
                    self.eat()

            self.eat() #we eat the right parenthesis when we finish with the predicate
            self.eat() #we eat the left curly bracket of the "while" body
            clevel=1
            tempvector=[]
            inipos=self.pos #position of the first token of the "while" body
            endpos=self.pos
            while clevel>0: #while we don't find the final right curly bracket...
                if self.current_token.type in (LCBRACKET,LPAREN):
                    clevel=clevel+1
                    tempvector.append(self.current_token)
                    self.eat()
                elif self.current_token.type in (RCBRACKET,RPAREN):
                    clevel=clevel-1
                    if clevel==0:
                        endpos=self.pos
                        subtokensWhileBody.append(tempvector)
                    else:
                        tempvector.append(self.current_token)
                        self.eat()
                else:
                    if self.current_token.type==COMA and clevel==1:
                        subtokensWhileBody.append(tempvector)
                        tempvector=[]
                    else:
                        tempvector.append(self.current_token)
                    self.eat()

            if inipos==endpos:
                self.error("Body of the while clause can't be empty")
            elif len(subtokensWhileBody) == 0:
                    self.error("Coma expected at the end of each \"while\" body expression")

            while Interpreter(subtokens).expr():
                for line in subtokensWhileBody:
                    interpreterLine = Interpreter(line) #we create an object of the class Interpreter, initialized with the vector of tokens that conform the line
                    resultLine = interpreterLine.expr() 
                    #print(resultLine)
            result = "While loop finished execution"
        ##########   END OF "WHILE" CLAUSE  ##########

        ##########   BEGINNING OF "METHOD" CLAUSE  ########## methodName(argument1, argument2, ..., argumentN)
        elif self.current_token.type == METHOD:
            mName=self.current_token.value #we save the name of the method to be called
            subtokensMethodArguments=[] #initialize the vector containing the tokens in the method call arguments
            self.eat() #we eat the method name
            self.eat() #we eat the left parenthesis
            tempVector=[]
            while self.current_token.type!=RPAREN: #we create a vector of tokens that conform the predicate
                if self.current_token.type==COMA:
                    subtokensMethodArguments.append(tempVector)
                    tempVector=[]
                else:
                    tempVector.append(self.current_token)
                self.eat()
            subtokensMethodArguments.append(tempVector) #we append the last argument before the right parenthesis

            if not (mName in self.methodDict):
                self.error("Method not recognized")
            else:
                result = self.methodDict[mName](subtokensMethodArguments)            
        ##########   END OF "METHOD" CLAUSE  ##########

        return result


######## SECTION 4 ########

if __name__ == '__main__': #this is how the main function is called in python
    start_time = time.clock() #we initialize the time meter
    #Command to execute this code: shell> python <nameOfThisFile>.py <sourceCodeFile>
    filename = sys.argv[1] #the argument of the python call will be the name of the source code file
    file = open(filename) #we prepare the source code file to be read
    characters = file.read() #and we read all the characters of the file and put them into a char array called "characters"
    file.close() #we close the source code file because we already have loaded the content of it
    tokens = lex(characters, token_exprs) #and now we tokenize that data according to the regular expressions, and save the tokens into a vector called "tokens". This is the lexer pass
    # for token in tokens: #this is the parsing and interpreting pass, which process token by token the whole source code
    for subtokens in tokens:
        interpreter = Interpreter(subtokens) #we create an object of the class Interpreter, initialized with the vector of tokens
        result = interpreter.expr() 
    print("--- %s python miliseconds ---" % ((time.clock() - start_time)*1000)) #we print the execution time required for the interpreter