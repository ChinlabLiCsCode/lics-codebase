function [atom_num temp psd atom_tsq atom_t] = process_last_run(run_catalog,evap_dist,running_stats,atom_num,temp,psd,atom_tsq,atom_t)

make_constants;

my_num = length(evap_dist);

atoms = running_stats(run_catalog{my_num},9)*1E-5;
temperatures = amu*133/k_B*1E6*(8.4E-6)^2/(.03^2-.005^2)*(running_stats(run_catalog{my_num,1},2).^2-mean(running_stats(run_catalog{my_num,2},2))^2);

atom_num(my_num) = mean(atoms);
temp(my_num) = mean(temperatures);
psd(my_num) = mean(atoms./(temperatures.^3));
atom_tsq(my_num) = mean(atoms./(temperatures.^2));
atom_t(my_num) = mean(atoms./(temperatures));
