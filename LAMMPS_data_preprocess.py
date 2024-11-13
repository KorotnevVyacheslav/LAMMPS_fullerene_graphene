import numpy as np
    

def generate_graphene(a=1.42, n=20, m=20, output_file="graphene.data"):
    # a - расстояние между атомами в графене, n и m - размеры решетки (n - по оси x, m - по оси y)
    graph_coords = []
    atom_types = []
    mass = 12.0107  

    for i in range(n):
        for j in range(m):
            if not ((i % 3 == 1 and j % 2 == 0) or (i % 3 == 2 and j % 2 == 1)):
                x = a * i + (a / 2 if j % 2 == 1 else 0)  
                y = np.sqrt(3) * a * j / 2 

                graph_coords.append((x, y, 0.0))
                atom_types.append(1)  

    x_coords = [coord[0] for coord in graph_coords]
    y_coords = [coord[1] for coord in graph_coords]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)

    edge_threshold = 0.1  

    for i, (x, y, z) in enumerate(graph_coords):
        if (abs(x - x_min) <=  edge_threshold * (x_max - x_min) or
            abs(x - x_max) <=  edge_threshold * (x_max - x_min) or
            abs(y - y_min) <=  edge_threshold * (y_max - y_min) or
            abs(y - y_max) <=  edge_threshold * (y_max - y_min)):
            atom_types[i] = 3  
        else:
            atom_types[i] = 2  

    with open(output_file, "w") as f:
        f.write("#Graphene\n")
        f.write(f"{len(graph_coords)} atoms\n")
        f.write("3 atom types\n")  # 
        f.write("\n")
        f.write(f"{x_min - 1} {x_max + 1} xlo xhi\n")  
        f.write(f"{y_min - 1} {y_max + 1} ylo yhi\n")
        f.write("0 100 zlo zhi\n")  
        f.write("\n")
        f.write("Masses\n")
        f.write("1 {}\n".format(mass))  
        f.write("2 {}\n".format(mass))  
        f.write("3 {}\n".format(mass))  
        f.write("\n")
        f.write("Atoms\n")
        
        for i, (x, y, z) in enumerate(graph_coords):
            atom_type = atom_types[i]  
            f.write(f"{i + 1} {atom_type} 0 {x:.6f} {y:.6f} {z:.6f}\n")

    print(f"Graphene structure with {len(graph_coords)} atoms has been written to {output_file}.")
    


def center_coordinates(input_file, output_file, z=0):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    if "Atoms\n" not in lines:
        raise ValueError("Файл не содержит секции 'Atoms'.")

    atom_start = lines.index("Atoms\n") + 1
    atom_count = int(lines[1].split()[0]) 
    
    coords = []
    atom_types = []  
    for line in lines[atom_start:]:
        if line.strip(): 
            parts = line.split()
            coords.append((float(parts[3]), float(parts[4]), float(parts[5])))  # x, y, z
            atom_types.append(int(parts[1])) 

    coords = np.array(coords)
    center_of_mass_x = np.mean(coords[:, 0])
    center_of_mass_y = np.mean(coords[:, 1])
    centered_coords = coords - np.array([center_of_mass_x, center_of_mass_y, -z])

    # Определение новых границ ячейки
    min_coords = np.min(centered_coords, axis=0)
    max_coords = np.max(centered_coords, axis=0)

    # Запись обратно в новый файл
    with open(output_file, 'w') as f:
        f.write("#Данные\n")
        f.write(f"{atom_count} atoms\n")
        
        unique_atom_types = set(atom_types) 
        f.write(f"{len(unique_atom_types)} atom types\n\n")

        f.write(f"{min_coords[0] - 1} {max_coords[0] + 1} xlo xhi\n")
        f.write(f"{min_coords[1] - 1} {max_coords[1] + 1} ylo yhi\n")
        f.write("0 100 zlo zhi\n") 
        f.write("\n")

        f.write("Masses\n\n")
        for atom_type in unique_atom_types:
            f.write(f"{atom_type} 12.0107\n\n")  

        f.write("Atoms\n\n")
        for i, (x, y, z) in enumerate(centered_coords):
            atom_type = atom_types[i]  
            f.write(f"{i + 1} {atom_type} 0 {x:.6f} {y:.6f} {z:.6f}\n")
            


def merge_data_files(file1, file2, output_file):
    mass = 12.0107
    
    with open(file1, 'r') as f:
        lines1 = f.readlines()

    with open(file2, 'r') as f:
        lines2 = f.readlines()

    coords1 = []
    atom_types1 = []
    atom_start1 = lines1.index("Atoms\n") + 1
    for line in lines1[atom_start1:]:
        if line.strip(): 
            parts = line.split()
            coords1.append((float(parts[3]), float(parts[4]), float(parts[5])))  # x, y, z
            atom_types1.append(int(parts[1]))

    coords2 = []
    atom_types2 = []
    atom_start2 = lines2.index("Atoms\n") + 1
    for line in lines2[atom_start2:]:
        if line.strip():  
            parts = line.split()
            coords2.append((float(parts[3]), float(parts[4]), float(parts[5])))  # x, y, z
            atom_types2.append(int(parts[1]))  

    all_coords = np.array(coords1 + coords2)
    all_atom_types = atom_types1 + atom_types2

    min_coords = np.min(all_coords, axis=0)
    max_coords = np.max(all_coords, axis=0)

    with open(output_file, 'w') as f:
        f.write("# Все данные\n")
        total_atoms = len(all_coords)
        f.write(f"{total_atoms} atoms\n")
        f.write("3 atom types\n\n")
        f.write(f"{min_coords[0] - 1} {max_coords[0] + 1} xlo xhi\n")
        f.write(f"{min_coords[1] - 1} {max_coords[1] + 1} ylo yhi\n")
        f.write("-50 100 zlo zhi\n\n")
        
        f.write("Masses\n\n")
        f.write("1 {}\n".format(mass)) 
        f.write("2 {}\n".format(mass)) 
        f.write("3 {}\n".format(mass))  
        f.write("\n")

        f.write("Atoms\n\n")
        for i, (x, y, z) in enumerate(all_coords):
            atom_type = all_atom_types[i]  
            f.write(f"{i + 1} {atom_type} 0 {x:.6f} {y:.6f} {z:.6f}\n")
            
            
def prepare_data(graphene_size=[40, 40], input_c60_file = 'C60.data', output_c60_centered = 'centered_C60.data', 
                output_graphene_centered = 'centered_graphene.data', output_file='combined.data',
                output_graphene = 'graphene.data', z_graphene = 20, z_c60 = 25):

    print('Preparing data started.\n')
    generate_graphene(n=graphene_size[0], m=graphene_size[1], output_file = output_graphene)

    print('Graphene has generated. Centering data started.\n')
    center_coordinates(output_graphene, output_graphene_centered, z = z_graphene)
    center_coordinates(input_c60_file, output_c60_centered, z = z_c60)

    print('Data centered. Merging data started.\n')
    merge_data_files(output_c60_centered, output_graphene_centered, output_file)

    print('Data prepared')