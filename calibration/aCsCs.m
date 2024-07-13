function [a] = aCsCs(B)

a = zeros(1,length(B));
%B = round(B*10)/10;

fid = fopen('Cs_a_vs_B.txt');
Cs_a_vs_B = fscanf(fid, '%f %f',[2 inf]);
fclose(fid);

%apparently I have to add this because of legacy behavior of interp1 in MATLAB I
%guess.
[Cs_a_vs_B_u,ind] = unique(Cs_a_vs_B(1,:)); 

for i = 1 : length(B)
    if B(i) > 0 && B(i) < 1200;
        a(i) = interp1(Cs_a_vs_B_u,Cs_a_vs_B(2,ind),B(i),'spline');
        
        %[x y] = find(Cs_a_vs_B(1,:) == B(i));
        %a(i) = Cs_a_vs_B(2,y);
    else
        a(i) = NaN;
     
    end
end