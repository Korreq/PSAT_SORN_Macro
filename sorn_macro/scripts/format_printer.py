
print_element_text = """"""

print_element_list = print_element_text.splitlines()
if __name__ == '__main__':

    for element in print_element_list:

        print(f'{{"name":"{element}"}},')
        