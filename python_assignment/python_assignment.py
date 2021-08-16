#!/usr/bin/python3

## 1. List_remove_append
# Remove SPSS from input_list=['SAS', 'R', 'PYTHON', 'SPSS'] and add 'SPARK'
# in its place.

input_list=['SAS', 'R', 'PYTHON', 'SPSS']
input_list[input_list.index("SPSS")]="SPARK"
print(input_list)

# -------------- xxxxxxxxxx --------------------

## 2. String to List Conversion
# Convert a string input_str = 'I love Data Science & Python' to a list by
# splitting it on ‘&’. The sample output for this string will be:
# ['I love Data Science', 'Python']

input_str = 'I love Data Science & Python'
print(input_str.split("&"))

# -------------- xxxxxxxxxx --------------------

## 3. List to String Conversion
# Convert a list ['Pythons syntax is easy to learn', 'Pythons syntax is very
# clear'] to a string using ‘&’. The sample output of this string will be:
# 'Pythons syntax is easy to learn & Pythons syntax is very clear'

input_lst = ['Pythons syntax is easy to learn', 'Pythons syntax is very clear']
full_stop = '.'
print(" & ".join(input_lst) + full_stop)

# -------------- xxxxxxxxxx --------------------

## 4. Nested List
# Extract 'Python' from a nested list

input_list = [['SAS','R'],['Tableau','SQL'],['Python','Java']]
print(input_list[2][0])

# -------------- xxxxxxxxxx --------------------

## 5. It’s the time to disco
# What is the output of: t[0][2]

t = ("disco", 12, 4.5)
print(t[0][2]) # output --> s

# -------------- xxxxxxxxxx --------------------

## 6. Paindrome

input_str = "madam"

if input_str == input_str[::-1]:
    print(1)
else:
    print(0)

# -------------- xxxxxxxxxx --------------------

## 7. Reverse words
# Given an input sentence: the order of words must be reversed,
# not the words themselves

input_str = "Hello how are you"

print(' '.join(input_str.split()[::-1]))

# -------------- xxxxxxxxxx --------------------

## 8. String Formatting
# Write a program to:
# caloRie ConsuMed --> calorie_consumed
# data science --> data_science
# datascience --> datascience

def format_func(input_str):
    
    return "_".join(input_str.strip().lower().split())

print(format_func("caloRie ConsuMed"))
print(format_func("data science"))
print(format_func("datascience"))
