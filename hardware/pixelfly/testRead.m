%An attempt to establish communication betweeb labVIEW on LiCs2 and MATLAB.
%Important notes: The port number that you put in at the beginning of this
%script (line 7) must match the port number in LabVIEW. The IP address must
%be correct. The Terminator (8) must be the delimiter for the LabVIEW
%output. Be sure to set the format (13) and delimeter (14).

cnct=tcpip('128.135.35.165',2280);%IP address and port number for LabVIEW
cnct.Terminator = ' ';
fopen(cnct);
pause(.05)

while (get(cnct, 'BytesAvailable')>0)
    [DataReceived,n] = fscanf(cnct,'%s');
    fprintf([DataReceived ' '])
end

fprintf('\n')

fclose(cnct);
delete(cnct);
clear cnct