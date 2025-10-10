'''
Script to process a CSV file and insert a double quote at a specific position in lines after a certain line number.
This version reads all lines into memory first.
'''
import os

# Define relative paths for input and a new output file
input_file = os.path.join('Archivos', 'transactions.csv')
output_file = os.path.join('Archivos', 'transactions_copy_3.csv')

try:
    # Open the input file and read all lines into a list
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    modified_lines = []
    # Process each line with its index
    for i, line in enumerate(lines):
        # Check if the current line number (i + 1) is 161 or greater
        if (i + 1) >= 161:
            # Check if the line is long enough for the insertion
            if len(line) >= 21:
                # Insert a double quote at the 21st character (index 20)
                modified_line = line[:20] + '"' + line[20:]
                modified_lines.append(modified_line)
            else:
                # If the line is too short, append it without modification
                modified_lines.append(line)
        else:
            # For lines before 161, append them without modification
            modified_lines.append(line)

    # Write the modified lines to the output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(modified_lines)
    
    print(f"Procesamiento completado con un método alternativo. El resultado se ha guardado en '{output_file}'")

except FileNotFoundError:
    print(f"Error: No se pudo encontrar el archivo '{input_file}'")
except Exception as e:
    print(f"Ha ocurrido un error inesperado: {e}")
