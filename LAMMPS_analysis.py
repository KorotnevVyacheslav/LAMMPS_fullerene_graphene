import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re

def get_files(folder_path, el='gr'):
    pos_files = glob.glob(os.path.join(folder_path, '**', el + '*.pos'), recursive=True)

    return pos_files

def count_data(filepath):
    coordinates = []

    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("ITEM: TIMESTEP"):
                timestep = int(lines[lines.index(line) + 1].strip())
            if line.startswith("ITEM: ATOMS"):
                line_atom = line
                break

        for line in lines[lines.index(line_atom)+1:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 5:
                    x = float(parts[2])
                    y = float(parts[3])
                    z = float(parts[4])
                    vx = float(parts[5])
                    vy = float(parts[6])
                    vz = float(parts[7])
                    if len(parts) >=9:
                        c = float(parts[8])
                    else:
                        c = -1
                    coordinates.append([x, y, z, vx, vy, vz, c])
                    

    coordinates = np.array(coordinates)

    mean_coordinates = np.mean(coordinates, axis=0)

    #print(f"Timestep: {timestep}")
    #print(f"Средние координаты атомов (x, y, z): {mean_coordinates}"
    
    return np.append(mean_coordinates, timestep)


def get_dataset(pos_files):
    data = []

    for filepath in pos_files:
        data.append(count_data(filepath))

    df = pd.DataFrame(data, columns=['x', 'y', 'z', 'vx', 'vy', 'vz', 'c', 'Step'])

    df = df.sort_values(by='Step')

    return df

def get_plots_coords_velocities(df, name='default'):
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(df.Step, df.x, label='x', color='r')
    plt.xlabel('Timestep')
    plt.ylabel('x')
    plt.title('Координаты x от времени')
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(df.Step, df.y, label='y', color='g')
    plt.xlabel('Timestep')
    plt.ylabel('y')
    plt.title('Координаты y от времени')
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(df.Step, df.z, label='z', color='b')
    plt.xlabel('Timestep')
    plt.ylabel('z')
    plt.title('Координаты z от времени')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(name + '_coordinates_plot.png', dpi=300, bbox_inches='tight') 
    #plt.show()
    
    
    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(df.Step, df.vx, label='x', color='r')
    plt.xlabel('Timestep')
    plt.ylabel('x')
    plt.title('Скорость x от времени')
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(df.Step, df.vy, label='y', color='g')
    plt.xlabel('Timestep')
    plt.ylabel('y')
    plt.title('Скорость y от времени')
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(df.Step, df.vz, label='z', color='b')
    plt.xlabel('Timestep')
    plt.ylabel('z')
    plt.title('Скорость z от времени')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(name + '_velocities_plot.png', dpi=300, bbox_inches='tight') 
    #plt.show()
    
    
    plt.figure(figsize=(12, 8))

    plt.plot(df.Step, df.c, label='x', color='r')
    plt.xlabel('Timestep')
    plt.ylabel('c')
    plt.title('Среднее количесвто связей')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(name + '_connections_plot.png', dpi=300, bbox_inches='tight') 
    #plt.show()

def is_broken_graphene(df, alpha = 0.05):
    std_c = df['c'].std()
    mean_c = df['c'].mean()

    relative_variance_c = (std_c / mean_c)
    
    min_c = df['c'].min()
    
    if (1 - min_c/3) > alpha:
        return True
    
    return False
    
def is_broken_c60_coords(df, z = 20):
    if ((df['z'] > 20) & (df['vz'] > 0)).any():
        return True
    else:
        return False