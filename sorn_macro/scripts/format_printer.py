
print_element_text= """"""

print_element_list = print_element_text.splitlines()

if __name__ == '__main__':

   

    for i in range(len(print_element_list)):

        element = print_element_list[i].split()
        print(f'{{"name": "{element[0]}", "enabled": {element[1]}}},')
