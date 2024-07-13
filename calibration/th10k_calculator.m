function out = th10k_calculator(in, type)

% https://www.thorlabs.com/drawings/53d601347d56f1bc-E094CEF3-FC83-EA0D-4FAD955DD9651A1C/TH10K-SpecSheet.pdf

switch type 
    case 'R'
        R0 = 10e3;
        a = 3.3540170e-03;
        b = 2.5617244e-04;
        c = 2.1400943e-06;
        d = -7.2405219e-08;
        celsius = 273.15;

        lt = log(in./R0);
        out = 1./(a + b.*lt + c.*lt.^2 + d.*lt.^3) - celsius;

    case 'T'
        R0 = 10e3;
        A = -1.5470381e+01;
        B = 5.6022839e+03;
        C = -3.7886070e+05;
        D = 2.4971623e+07;
        
        T = in + celsius;
        out = R0.*exp(A + B./T + C./T.^2 + D./T.^3);

    otherwise   
        error('Invalid type');
end

end

