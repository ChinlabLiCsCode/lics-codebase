function fpath = localpath(type)

switch type
    case 'H'
        fpath = ['/Users/henry/Library/CloudStorage/Box-Box/CHIN_LICS/NAS_Data_Backup/', ...
            'Data/%1$04d%2$02d%3$02d/%1$04d%2$02d%3$02d_%4$d.mat'];
    case 'V'
        fpath = ['/Users/henry/Library/CloudStorage/Box-Box/CHIN_LICS/NAS_Data_Backup/', ...
            'V_Images/Data/%1$04d/%2$02d/%1$04d%2$02d%3$02d/%1$04d%2$02d%3$02d_%4$d.mat'];
    case 'loadparams'
        fpath = ['/Users/henry/Library/CloudStorage/Box-Box/CHIN_LICS/NAS_Data_Backup/', ...
            'paramlogs'];
    case 'saveparams'
        error('Trying to save params from a non-lab machine!');
end

        
end