
print_element_text2= """"""

print_element_text = """"""

print_element_text3=""""""


print_element_list = print_element_text.splitlines()
print_element_list2 = print_element_text2.splitlines()
print_element_list3 = print_element_text3.splitlines()

if __name__ == '__main__':

    found_elements = []

    for i in range(len(print_element_list)):

        name = print_element_list[i][:3].strip()
        zone = print_element_list3[i].strip()
        enabled = print_element_list2[i].strip()
        
        found = False    
        for y in range(len(found_elements)):
            if found_elements[y][0] == name and found_elements[y][1] == zone and found_elements[y][2] == enabled:
                found = True
                break
        
        if not found:
            found_elements.append([name, zone, enabled])

    for element in found_elements:
        name, zone, enabled = element
        print(f'{{"name":"{name}", "zone": {zone}, "enabled": {enabled}}},')
        
