function fpath = localpath(type)

switch type
    case 'H'
        fpath = ['C:\\Users\\chinl\\Box\\CHIN_LICS\\NAS_Data_Backup\\', ...
            'Data\\%1$04d%2$02d%3$02d\\%1$04d%2$02d%3$02d_%4$d.mat'];
    case 'V'
        fpath = ['C:\\Users\\chinl\\Box\\CHIN_LICS\\NAS_Data_Backup\\', ...
            'V_Images\\Data\\%1$04d/%2$02d/%1$04d%2$02d%3$02d/%1$04d%2$02d%3$02d_%4$d.mat'];
    case 'saveparams'
        fpath = ['C:\\Users\\chinl\\Box\\CHIN_LICS\\NAS_Data_Backup\\', ...
            'paramlogs'];
    case 'loadparams'
        % By having an error here, we can prevent users on remote machines 
        % from overwriting the NAS synced version on box.
        error('Trying to save params from a non-lab machine!');
end

        
end