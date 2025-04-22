%An attempt to establish communication betweeb labVIEW on LiCs2 and MATLAB.
%Important notes: The port number that you put in at the beginning of this
%script (line 9) must match the port number in LabVIEW. The IP address must
%be correct. The Terminator (10) must be the delimiter for the LabVIEW
%output. Be sure to set the format (16) and delimeter (17).

% function readParams(fname)

cnct=tcpip('128.135.35.165',3391);%IP address and port number for LabVIEW
cnct.Terminator = ' ';
fopen(cnct);
% f1=fopen(fname);
pause(.05)

while (get(cnct, 'BytesAvailable')>0)
    DataReceived = fscanf(cnct,'%s');
    fprintf([DataReceived ' '])
end

fprintf('\n')

% fclose(f1);

fclose(cnct);
delete(cnct);
clear cnct

%procedures, ramping parameters, analog initial/final value, digital
%initial/final value, analog initial/final value 2