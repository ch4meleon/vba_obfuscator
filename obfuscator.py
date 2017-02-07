import os
import sys
import re
import random
import string
from pprint import pprint


obfuscated = dict()

def get_random_string(length):
    tmpstr = ''.join(random.choice(string.lowercase)) + ''.join(random.choice(string.lowercase + string.digits) for i in range(length - 1))
    return tmpstr

RANDOM_STRING = get_random_string(8)
RANDOM_FUNCTION_NAME = get_random_string(8)

def yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def xor(data, key): 
    return bytearray(a^b for a, b in zip(*map(bytearray, [data, key]))) 

def str_xor(s1, s2):
    return "".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(s1,s2)])

def ed(data, key):
    resultStr = ""
    for c in data:
        dc = ord(c)
        newD = dc
        for a in key:
            newD = ord(a) ^ newD
        resultStr += chr(newD)
    
    return resultStr

content = open(sys.argv[1]).read()

print "[*] Obfuscating strings..."

# Find string not within double quotes only
m = re.findall("(\".+?\")", content)
for n in m:
    if (n.strip() != "\"\"") and (n.strip() != "\"\"\""):
        print "STRING FOUND: %s" % (n)
        tmpstr = n

        """ remove first '"' and last '"' """
        tmpstr = tmpstr[1:len(tmpstr) - 1]

        newline = ""

        encrypted_str = ed(tmpstr, RANDOM_STRING)
        for c in encrypted_str:
            """ randomly decide to convert to chr(xxx) or rename original """
            yesno = random.choice([1,2])
            if yesno == 1:
                newline = newline + "chr(" + str(ord(c)) + ") & "

                if random.choice([1,2]) == 2: # Add empty quote randomly
                    newline += '"" & ' 
            else:
                if c == '"':
                    c = '""' # Fixed "
                newline = newline + '"' + c + '" & '
                if random.choice([1,2]) == 2: # Add empty quote randomly
                    newline += '"" & ' 

        """ remove last '&' """
        newline = newline[0:len(newline) - 2]

        obfuscated[tmpstr] = newline # newline.rstrip()

# Find string not within double-double quotes only
m = re.findall("(\"\".*\"\")", content)
for n in m:
    if n.strip() != "":
        print "STRING FOUND: %s" % (n)
        tmpstr = n

        """ remove first '"' and last '"' """
        tmpstr = tmpstr[1:len(tmpstr) - 1]

        newline = ""

        encrypted_str = ed(tmpstr, RANDOM_STRING)
        for c in encrypted_str:
            """ randomly decide to convert to chr(xxx) or rename original """
            yesno = random.choice([1,2])
            if yesno == 1:
                newline = newline + "chr(" + str(ord(c)) + ") & "

                if random.choice([1,2]) == 2: # Add empty quote randomly
                    newline += '"" & ' 
            else:
                if c == '"':
                    c = '""' # Fixed "
                newline = newline + '"' + c + '" & '
                if random.choice([1,2]) == 2: # Add empty quote randomly
                    newline += '"" & ' 

        """ remove last '&' """
        newline = newline[0:len(newline) - 2]

        obfuscated[tmpstr] = newline # newline.rstrip()

# Write to new content
new_content = content
for o in obfuscated:
    new_content = new_content.replace('"' + o + '"', RANDOM_FUNCTION_NAME + "(" + obfuscated[o] + ")")

header = ""
header += 'Function str2byte(str As String) As Variant: Dim bytes() As Byte: bytes = str: str2byte = bytes: End Function\n'
header +='Function byte2str(bytes() As Byte) As String: Dim str As String: str = bytes: byte2str = str: End Function\n'

decrypt_method = """
Function ds(str As String) As String
    Const p_ As String = "<KEY>"
    Dim sb_() As Byte, pb_() As Byte
    sb_ = str2byte(str)
    pb_ = str2byte(p_)
    
    Dim uL As Long
    uL = UBound(sb_)
    
    ReDim scb_(0 To uL) As Byte
    
    Dim idx As Long
    
    For idx = LBound(sb_) To uL:
        If Not sb_(idx) = 0 Then
            c = sb_(idx)
            For i = 0 To UBound(pb_):
                c = c Xor pb_(i)
            Next i
            scb_(idx) = c
        End If
    
    Next idx
    
    ds = byte2str(scb_)
End Function\n
"""

""" Rename function ds with random function name """
decrypt_method = decrypt_method.replace("ds", RANDOM_FUNCTION_NAME)
decrypt_method = decrypt_method.replace("<KEY>", RANDOM_STRING)

""" Rename str2byte with random function name """
RANDOM_FUNCTION_NAME_1 = get_random_string(4)
header = header.replace("str2byte", RANDOM_FUNCTION_NAME_1)
decrypt_method = decrypt_method.replace("str2byte", RANDOM_FUNCTION_NAME_1)

""" Rename byte2str with random function name """
RANDOM_FUNCTION_NAME_2 = get_random_string(4)
header = header.replace("byte2str", RANDOM_FUNCTION_NAME_2)
decrypt_method = decrypt_method.replace("byte2str", RANDOM_FUNCTION_NAME_2)

print

# Rename the variables with random names
print "[*] Obfuscating variables..."

variables = re.findall("[dD]im (.+) [Aa]s .+:?", new_content)
for v in variables:
    if len(v) > 3:
        print "VARIABLE FOUND: " + v
        new_variable_random_name = get_random_string(8)
        new_content = new_content.replace(v, new_variable_random_name)
    else:
        print "SKIPPED VARIABLE: " + v + " (TOO SHORT)"

print

# Obfuscate the function names with random names
print "[*] Obfuscating function names..."

funcs = re.findall("function (.+) as", new_content, re.IGNORECASE)
for f in funcs:
    print f

subs = re.findall("sub (.+)", new_content, re.IGNORECASE)
for s in subs:
    if len(s) > 3:
        if "document_" in s.lower():
            print "SKIPPED FUNCTION NAME: " + s + " (VBA DOCUMENT FUNCTION)"
        else:
            new_function_random_name = get_random_string(8)

            if "()" in s:
                print "FUNCTION FOUND: " + s
                new_content = new_content.replace(s, new_function_random_name + "()")
            else:
                print "SKIPPED FUNCTION NAME: " + s + " (GOT PARAMETERS SO IGNORED)"

    else:
        print "SKIPPED FUNCTION NAME: " + s + " (TOO SHORT)"

# Combine header, decrypt method and content
new_content = header + decrypt_method + '\n' + new_content

print

# Print obfuscated
print "[*] Showing obfuscated result..."
pprint(obfuscated)

print

if yes_no('WARNING: Replace the file?') == True:
    f = open(sys.argv[1], "w+")
    f.write(new_content)
    f.close()




