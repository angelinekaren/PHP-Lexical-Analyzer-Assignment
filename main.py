import re

class LexicalAnalyzer:
    # Store the token
    tokens = []

    # Find the starting index of the matched keyword
    def findIndexWord(self, pattern, text):
        # Find the index of the matched keyword according to the pattern
        for match in re.finditer(pattern, text):
            # Get index where the matched keyword start
            s = match.start()
            return s

    # Function for the output format
    def outputFormat(self, indexRow, indexCol, tokenClass=True, tokenValue=None):
        LINE = indexRow+1
        COLUMN = indexCol+1

        # Says that we don't pass tokenValue, we don't print it
        if tokenValue == None:
            return f"{LINE}, {COLUMN}, {tokenClass}"
        else:
            return f"{LINE}, {COLUMN}, {tokenClass}, {tokenValue}"

    # Function for the error output format
    def errorFormat(self, fileName, indexRow, indexCol, error_statement):
        raise ValueError(f"{fileName} : {indexRow} : {indexCol} : {error_statement}")

    # Opening Tag
    def openingTag(self, word, index):
        # Find string that match
        opening_tag = "^<\?php$"  

        # Search word that matches the pattern
        if re.match(opening_tag, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(opening_tag, word), "php-opening-tag")])
            return True
        return False

    # Closing Tag
    def closingTag(self, word, index):
        # Find string that match
        closing_tag = "^\?>$"  

        # Search word that matches the pattern
        if re.match(closing_tag, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(closing_tag, word), "php-closing-tag")])
            return True
        return False

    # Class token
    def classToken(self, word, splitted_words, sentence, index, indexWord):
        # Regex to find class
        class_tag = "^class$"

        # Search word that matches the pattern
        if re.search(class_tag, word):
            try:
                # Find the class value (it will skip the class declaration)
                class_value = splitted_words[indexWord+1]
                # Search the class name and store it in class_name
                class_name = re.search("[A-Z][a-zA-Z]+", class_value)[0]

                # Append token
                self.tokens.append([self.outputFormat(index, self.findIndexWord("class", sentence), "class")])
                self.tokens.append([self.outputFormat(index, self.findIndexWord(class_name, sentence), "type-identifier", class_name)])

            # Raise error if there is no class name
            except:
                self.outputFormat(file_name, index, self.findIndexWord(class_tag, sentence), "MISSING CLASS NAME")

    # Function token
    def functionToken(self, word, splitted_words, sentence, index, indexWord):
        # Regex to find function
        function_tag = "^function$"

        # Search word that matches the pattern
        if re.search(function_tag, word):
            try:
                # Append token for function declaration (function)
                self.tokens.append([self.outputFormat(index, self.findIndexWord("function", sentence), "function")])
                
                # Find the function value (it will skip the function declaration)
                function_value = splitted_words[indexWord+1]

                # Search the function name and store it in function_name
                function_name = re.search("[a-zA-Z]+", function_value)[0]

                # Append token
                self.tokens.append([self.outputFormat(index, self.findIndexWord(function_name, sentence), "type-identifier", function_name)])

            # Raise error if there is no function name
            except:
                self.outputFormat(file_name, index, self.findIndexWord(function_tag, sentence), "MISSING FUNCTION NAME")

    # Variable token
    def variableToken(self, word, sentence, index):
        # Regex to find variable
        variable_tag = "\$[a-zA-Z]+"

        find = re.findall(variable_tag, word)

        if len(find) != 0:
            try:
                for wordFind in find:
                    wordFind = wordFind.replace("$", "\$")
        
                    # Append token for variable declaration ($)
                    self.tokens.append([self.outputFormat(index, self.findIndexWord(wordFind, sentence), "variable")])

                    # Search the variable identifier by searching the characters after the variable declaration ($)
                    var_identifier = re.search(wordFind, word).group()[1:]

                    # Append token for variable identifier 
                    # +1 index to skip the variable declaration (start from the variable identifier)
                    self.tokens.append([self.outputFormat(index, self.findIndexWord(wordFind, sentence)+1, "type-identifier", var_identifier)])

            except:
                self.outputFormat(file_name, index, self.findIndexWord(variable_tag, sentence), "MISSING VARIABLE NAME")
        # # Search word that matches the pattern
        # if re.search(variable_tag, word):  
        #     try:
                
                
        #         # Search the variable identifier by searching the characters after the variable declaration ($)
        #         var_identifier = re.search(variable_tag, word).group()[1:]

        #         # Append token for variable identifier 
        #         # +1 index to skip the variable declaration (start from the variable identifier)
        #         self.tokens.append([self.outputFormat(index, self.findIndexWord(variable_tag, sentence)+1, "type-identifier", var_identifier)])

        #     # Raise error if there is no variable name
        #     except:
        #         self.outputFormat(file_name, index, self.findIndexWord(variable_tag, sentence), "MISSING VARIABLE NAME")

    # Assign token
    def assign(self, word, sentence, index):
        # Regex to find assign
        assign_tag = "\="

        # Search word that matches the pattern
        if re.search(assign_tag, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(assign_tag, sentence), "assign")])

    # String literal token
    def stringLiteral(self, word, sentence, index):
        # Regex to find word that matches "({anything})"
        str_tag = '"(.+)"'
        
        # Search word that matches the pattern
        if re.search(str_tag, word):
            # Search the matched string value
            str_value = re.search(str_tag, word)[0]

            # To change $ into \$ so it won't be detected as $ (end of string) in regex
            new_str_value = self.replaceBacklash(str_value)

            # Replace whitespace and single quote
            res = self.stringReplace(str_value)

            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(new_str_value, sentence), "string-literal", res)])
        

    # Function to replace backslash
    def replaceBacklash(self, text):
        # Iterate through the text
        for i in text:
            # If there is $ or ?, which is a special character in regex
            if i == '$' or i == '?':
                # Replace it with an additional \ in the beginning to escape the special character ($ or ?)
                text = text.replace(i, "\\" + i)
        return text

    # Function for string replacement
    def stringReplace(self, text):
        # Iterate through the text
        for i in text:
            # If there is a space
            if i == " ":
                # Replace it with &nbsp
                text = text.replace(i, "&nbsp")
            # If there is a single quote
            if i == "'":
                # Replace it with \'
                text = text.replace(i, "\'")
        return text

    # Opening bracket
    def openingBracket(self, word, sentence, index):
        # Regex to find opening brackets
        opening_bracket = "(.*)\("

        # Search word that matches the pattern
        if re.search(opening_bracket, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord("\(", sentence), "bracket-opening")])
            return True
        return False

    # Closing bracket
    def closingBracket(self, word, sentence, index):
        # Regex to find closing brackets
        closing_bracket = "(.*)\)"

        # Search word that matches the pattern
        if re.search(closing_bracket, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord("\)", sentence), "bracket-closing")])
            return True
        return False

    # Opening curly bracket
    def openingCurlyBracket(self, word, sentence, index):
        # We can use brackets even if there is a character before or after it in php, 
        # and so we do not use ^ or $ but (.*) -> 0 or many charac
        opening_curly_bracket = "(.*)\{"

        # Search word that matches the pattern
        if re.search(opening_curly_bracket, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord("\{", sentence), "curly-bracket-opening")])
            return True
        return False

    # Closing curly bracket
    def closingCurlyBracket(self, word, sentence, index):
        # We can use brackets even if there is a character before or after it in php, 
        # and so we do not use ^ or $ but (.*) -> 0 or many charac
        closing_curly_bracket = "(.*)\}"

        # Search word that matches the pattern
        if re.search(closing_curly_bracket, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord("\}", sentence), "curly-bracket-closing")])
            return True
        return False

    # Operator token
    def operator(self, word, sentence, index):
        # Regex to search operator (+, -, *, /, %)
        operator_tag = "[\+|\-|\*|\/|\%]+"

        # Find all matches of the pattern in a list of strings
        find = re.findall(operator_tag, word)
        op = ""
        
        # If there is a match
        if len(find) != 0:
            # Word in the list
            for wordFind in find:
                # Escape backslash
                wordFind = "\\" +  wordFind
                # Search the identifiers
                identifier = re.search(wordFind, word).group()

                # Error handling to not read / in /* as division operator
                if wordFind == "\/*":
                    break
                else:
                    # Multiplication operator
                    if identifier == "*":
                        op = "times"
                    # Division operator
                    elif identifier == "/":
                        op = "division"
                    # Addition operator
                    elif identifier == "+":
                        op = "addition"
                    # Substraction operator
                    elif identifier == "-":
                        op = "substraction"
                    # Modulo operator
                    elif identifier == "%":
                        op = "modulo"
                    else:
                        return False

                    # Append token
                    self.tokens.append([self.outputFormat(index, self.findIndexWord(operator_tag, sentence), f"math-{op}")])

    # Numbers 
    def numbers(self, word, sentence, index):
        # Regex to find numbers
        number_tag = "[0-9]"

        # Search word that matches the pattern
        if re.search(number_tag, word):
            # Store the matched word -> token value
            number = re.search(number_tag, word)[0]
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(number_tag, sentence), "number", number)])

    # Semicolon
    def semicolon(self, word, sentence, index):
        # Regex to find semicolon
        sc_tag = ";"

        # Search word that matches the pattern
        if re.search(sc_tag, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(sc_tag, sentence), "semicolon")])

    # Echo / Output
    def echo(self, word, sentence, index):
        # Regex to find the word "echo" -> printing output
        echo_tag = "[Ee][Cc][Hh][Oo]"

        # Find word that matches the pattern
        if re.match(echo_tag, word):
            # Append token
            self.tokens.append([self.outputFormat(index, self.findIndexWord(echo_tag, sentence), "print-output")])

    # Concatenation token
    def concate(self, word, sentence, index):
        # Regex to find the concatenation tag 
        # Match concatenate excluding float numbers
        concatenation_tag = "[^0-9]\."

        # Search word that matches the pattern
        if re.search(concatenation_tag, word):
            # Append token
            # +1 in searching the column index since negate will match the character before \.
            self.tokens.append([self.outputFormat(index, self.findIndexWord(concatenation_tag, sentence)+1, "concate")])

    # Single comment handling
    def singleComment(self, word):
        # Regex to find single comment
        singleComment_tag = "\/\/|#"

        # Find word that matches the pattern
        if re.match(singleComment_tag, word):
            # If there is/are comment(s), return True
            return True

    # Multiline comment handling
    def multilineComment(self, word):
        # Regex to find multiline comment
        multilineComment_tag = "\/*((.*?|\n)*)*\/"

        # Find word that matches the pattern
        if re.match(multilineComment_tag, word):
            # If there is/are comment(s), return True
            return True

    # Token function
    def token(self, file_context):
        # Variable for string literals
        strLit = ""
        strChecker = 0
        
        # Variable to check opening & closing php tag
        openingTagCheck = 0
        closingTagCheck = 0

        # Loop through sentences in the data
        for index, sentences in enumerate(file_context):
            # Split each sentences into list of words
            words = sentences.split()

            # Loop through word in words
            for indexWord, word in enumerate(words):
                # Call the function

                # If there is an opening tag
                if self.openingTag(word, index):
                    # Increment by 1
                    openingTagCheck += 1
                
                # If there is no opening tag
                if openingTagCheck != 1:
                    # Raise value error
                    self.errorFormat(file_name, index+1, self.findIndexWord(word, sentences)+1, "MISSING OPENING TAG")

                # If there is a closing tag
                if self.closingTag(word, index):
                    # Increment by 1
                    closingTagCheck += 1

                self.classToken(word, words, sentences, index, indexWord)
                self.functionToken(word, words, sentences, index, indexWord)
                self.assign(word, sentences, index)
                self.concate(word, sentences, index)
                self.variableToken(word, sentences, index)
                self.openingBracket(word, sentences, index)
                self.closingBracket(word, sentences, index)
                self.operator(word, sentences, index)
                self.semicolon(word, sentences, index)
                self.openingCurlyBracket(word, sentences, index)
                self.closingCurlyBracket(word, sentences, index)
                self.numbers(word, sentences, index)
                self.echo(word, sentences, index) 
                
                # if strChecker is 1
                if strChecker == 1:
                    # Concatenate the word
                    strLit += " " + word
                    # If the string literal is already matched inside ""
                    if re.search('"(.+)"', strLit):
                        # Call the function
                        self.stringLiteral(strLit, sentences, index)
                        # Reset values
                        strLit = ''
                        strChecker = 0
                        
                # Checking for string literal with "" as indicator
                elif '"' in word:
                    # If string literal is more than one word 
                    if re.search('"(.+)"', word) == None:
                        # Concatenate the word
                        strLit += " " + word 
                        # If string literal is 2 words
                        if re.search('"(.+)"', strLit):
                            # Call function
                            self.stringLiteral(strLit, sentences, index)
                            # Reset strLit
                            strLit = ''
                        # If more than 2 words                    
                        else:
                            # Change strChecker to 1
                            strChecker = 1
                    # If string literal is exactly one word
                    elif re.match('"(.+)"', word):
                        self.stringLiteral(word, sentences, index)
        
                # Handling single comment
                # If true, it will continue searching for tokens
                if self.singleComment(word):
                    continue
                
                # Handling multiline comment
                # If true, it will continue searching for tokens
                if self.multilineComment(word):
                    continue
            
            if strChecker == 1:
                strChecker = 0
                for i in word:
                    # If there is $ or ?, which is a special character in regex
                    if i == '$' or i == '?':
                        # Replace it with an additional \ in the beginning to escape the special character ($ or ?)
                        wordsss = word.replace(i, "\\" + i)

                self.errorFormat(file_name, index+1, self.findIndexWord(wordsss, sentences)+1, "WRONG STRING FORMAT")
                
            # if oBracket > cBracket:
            #     self.outputFormat(file_name, index, indexWord, "MISSING CLOSING CURLY BRACKET")
            # elif cBracket > oBracket: 
            #     self.outputFormat(file_name, index, indexWord, "MISSING OPENING CURLY BRACKET")

            # Find index for the last line in the file
            indexCol = file_context.index(file_context[-1])+1

            # If there is no closing tag
        if closingTagCheck != 1:
            # Raise value error 
            self.errorFormat(file_name, indexCol, self.findIndexWord(word, sentences)+1, "MISSING CLOSING TAG")

        return self.tokens


# Main function
if __name__ == "__main__":
    # File that we want to read
    file_name = "data.php"

    # Open the file data
    with open(file_name) as d:
        # Return list of each line in the file
        file = d.readlines()

    # Call lexical analyzer
    lexical = LexicalAnalyzer()

    # Get the tokens
    t = lexical.token(file)

    # Loop through all the token stored inside tokens list
    for i in t:
        # Print out
        print(i)