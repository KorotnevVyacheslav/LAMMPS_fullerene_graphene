import os

def generate_lammps_script(velocity, temperature, dump_dir, ts = [0.1, 0.1, 0.05], iterations = [1000, 1000, 0, 100000]):
    
    ts1, ts2, ts3 = ts[0], ts[1], ts[2]
    it1, it2, it3, it4 = iterations[0], iterations[1], iterations[2], iterations[3]
    
    lammps_script = f"""
#Example fullerene + graphene

units                   real
atom_style              charge

read_data               {dump_dir}/combined.data

comm_style      brick
fix             bal all balance 1000 1.05 shift xyz 5 1.05

group C60 type 1
group graphene type 2
group edges type 3

set group C60 type 1
set group edges type 1
set group graphene type 1

pair_style              reaxff NULL
pair_coeff              * * ffield_reax.cho2016 C C C
fix                     chg all qeq/reax 1 0.0 10.0 1.0e-6 reaxff

thermo_style    custom  step time temp pe ke etotal press vol
thermo          100

dump            1 all cfg 100 {dump_dir}/all.*.cfg mass type xs ys zs
dump            2 all custom 100 {dump_dir}/all.*.pos id type x y z vx vy vz

compute         coord all coord/atom cutoff 1.8
dump            3 graphene custom 100  {dump_dir}/pos/graphene.*.pos id type x y z vx vy vz c_coord
dump            4 C60 custom 100  {dump_dir}/pos/c60.*.pos id type x y z vx vy vz c_coord

fix relax graphene box/relax aniso 0.0
min_style       cg
minimize        1.0e-16 1.0e-8 15000 30000
unfix relax

timestep        {ts1}

fix 01 edges setforce 0 0 0

# Run 1 - NVT ensemble
fix 1 all nvt temp 10 {temperature} 10
run             {it1}

unfix    1
fix    2 all nvt temp {temperature} {temperature} 10
run    {it2}

unfix    2
fix    3 all nve

timestep    {ts2}
velocity C60 set 0. 0. {velocity}
run    {it3}

timestep    {ts[2]}
run    {it4}
"""
    return lammps_script


def generate_in_file(velocity, temperature, dump_dir='data', output_file = 'in.perforation', ts = [0.1, 0.1, 0.05], 
                     iterations = [1000, 1000, 0, 100000]):
    
    a = 1
    
    ts[2] = min(ts[2], round(0.001 * a / abs(velocity), 3))  

    iterations[2] = max(int(abs(4/velocity/ts[1])), iterations[2])
    iterations[3] = max(int(abs(50/velocity/ts[2])), iterations[3])
    
    try:
        os.mkdir(dump_dir)
        os.mkdir(dump_dir + '/pos')
    except FileExistsError:
        print('Folders already exist')
        
    with open(output_file, "w") as f:
        f.write(generate_lammps_script(velocity, temperature, ts=ts, iterations=iterations, dump_dir=dump_dir))
        
    print('In File generated.\n')