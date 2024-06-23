import pandas as pd
import itertools

def read_elements_from_txt(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    elements = content.split(',')
    return [str(element).replace(" ", "") for element in elements if element]

def generate_passwords(elements, max_length=3):
    passwords = set()
    special_chars = ["", "!", "*", "123"]
    
    for length in range(1, max_length + 1):
        for permutation in itertools.permutations(elements, length):
            for separator in itertools.product(special_chars, repeat=length-1):
                combined_elements = "".join(itertools.chain(*zip(permutation, separator + ("",))))
                passwords.add(combined_elements)
                passwords.add(combined_elements.lower())
                passwords.add(combined_elements.upper())
    return passwords

def save_passwords(passwords, filename):
    with open(filename, 'w') as file:
        for password in passwords:
            file.write(f"{password}\n")

file_path = 'Personal_Details.txt'
print("Creating password list")
elements = read_elements_from_txt(file_path)
passwords = generate_passwords(elements)
save_passwords(passwords, "wordlist.txt")
print("Password list created in file wordlist.txt")
