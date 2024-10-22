function [A, B, C] = get_field_params(varargin)

if nargin < 1
    revision = 'traditional';
else
    revision = varargin{1};
end

if ischar(revision)
    switch revision
        case '201309aa'
            A = 842.88/1.770324707031250;
            B = 0;
        case '201311aa'
            A = 8.428951262754101e+02/1.770324707031250;
            B = 0;
        case '201311aat4'
            A = 8.428951262754101e+02/1.770324707031250;
            B = -0.174914494589643;
        case '201311aashim'
            A =  8.428523695314807e+02/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.361488592384092;
        case '201311aashim_2'
            A = 842.899/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20131218aashim'%N.B.: 420 kHz
            A = 843/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20131219aashim1'%N.B.: 330 kHz
            A = 842.965/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20131220aashim1'%N.B.: 300 kHz
            A = 842.953/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20140122aashim1'%N.B.: 240 kHz
            A = 842.93/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20140130aashim1'%N.B.: f=11315.43 MHz, B=843.004 G
            A = 843.004/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20140131aashim'%N.B.: f=11315.51 MHz B=843.035 G
            A = 843.035/1.770324707031250;
            if nargin >= 2
                shim = varargin{2};
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20140905abshim'%N.B.: f=11450.516 B = 895.454
            A = 8.954547653131303e+02/1.879882812500000;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20150427_0_153'%Valid for B = 0-153 G/V_HH = 0-.317
            A = 102.326/.2114868;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20150427_153_307'%Valid for B = 153-307 G/V_HH = .317-.634
            A = 204.561/.4229736;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20150427_307_512'%Valid for B = 307-512 G/V_HH = .634-1.05
            A = 409.738/.8459473;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20150427_512_716'%Valid for B = 512-716 G/V_HH = 1.05-1.48
            A = 613.542/1.2689209;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20150427_716_856'%Valid for B = 716-856 G/V_HH = 1.48-1.77
            A = 818.095/1.6918945;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20150427'%Valid for B > 856 G/V_HH > 1.77
            A = 894.937/1.8508911;
            if nargin >= 2
                shim = varargin{2}+1.351;
            else
                shim = 0;
            end
            B = shim*0.3605;
        case '20151014'
            A = 122.7673164909108;
            if nargin >= 2
                shim = varargin{2}+3.588013;
            else
                shim = 0;
            end
            B = shim*0.366339;
%             B = -0.3909;
        otherwise
            if ~strcmp(revision,'traditional')
                warning(['unrecognized field calibration: ' revision]); %#ok<WNTAG>
            end
%             fb_sens = 4.7240965340e+02;
%             A = 477.0594;
%             A = 488.597691;
%             A = [118.643631553 5.50900426 .366614621;-167.016064469 -4089.245023659 0;82027.80611493 478688.841858727 0];
%             A = 122.7677140537881;
%             if nargin >= 2
%                 shim = varargin{2}+3.588013;
%             else
%                 shim = 0;
%             end
%             A = [118.5027423256 5.509004260157962 .3666146205;-167.0160644694 -4089.245023659 0;82027.8061149295 478688.8418587274 0];
%             B = [-.444127;-164.3555;0];
            A = [118.5027423256 5.509004260157962 .3666146205;-167.0160644694 -4103.557381242 0;82027.8061149295 478688.8418587274 0];
            B = [-.444127;-163.7823;0];
%             B = shim*0.366339;
%             B = -0.3909;
    end
else
%     if revision<1000
%         revision = revision/1000+11315;
%     end
%     A = (843+(revision-11315.42)/2.571825)/1.770324707031250;
%     if nargin>=2
%         shim = varargin{2};
%     else
%         shim = 0;
%     end
%     B = shim*0.3605;
%     if revision<1000
%         revision = revision/1000+11450;
%     end
%     A = (895.255+(revision-11450)/2.578274417375724)/1.8798828125;
%     if nargin>=2
%         shim = varargin{2}+1.351;
%     else
%         shim = 0;
%     end
%     B = shim*0.3605;
%     if revision<1000
%         revision = revision/1000+11442;
%     end
%     A = (892.407826+(revision-11443)/2.577923)/1.8438720703125;
%     A = (892.5394082231854+(revision-11443)/2.577923)/1.8438720703125;
%     if nargin>=2
%         shim = varargin{2}+1.376;
%     else
%         shim = 0;
%     end
%     B = shim*0.3605;
%     A = [118.5027423256 5.509004260157962 .3666146205;-167.0160644694 -4103.557381242 0;82027.8061149295 478688.8418587274 0];%Before modifying control circuitry
%     B = [-.444127;-163.7823;0];%Before modifying control circuitry
    A = [-11.414079399644 -.543883895925 .3666146205;16.086839709008 405.129252087202 0;-7900.845782976771 -47259.2032881527 0];
%     C = [-.444127;-163.7823;0];%Offset with voltage=0%2016-08-02
    C = [-.444127;-163.7823;0];%Offset with voltage=0%2016-08-10
    B = [-77.945659273596831;.066789879899831;0];%Calculated electronic voltage offset
%     B = [-77.945659273596831;.066789879899831;.003041340791263];%Calculated electronic voltage offset 2016-08-02
%     B = [-77.945659273596831;.066789879899831;.043598097583236];%Calculated electronic voltage offset 2016-08-10
%     B = [-77.945659273596831;.066789879899831;.040213161266431];%Calculated electronic voltage offset 2016-08-12
%     B = [-77.945659273596831;.066789879899831;.028272245305233];%Calculated electronic voltage offset 2016-08-15
%     B = [-77.945659273596831;.066789879899831;.036625023553661];%Calculated electronic voltage offset 2016-08-16
%     B = [-77.945659273596831;.066789879899831;-.004113409446394];%Calculated electronic voltage offset 2016-08-18
%     B = [-77.945659273596831;.066789879899831;-.012392822413753];%Calculated electronic voltage offset 2016-08-20
%     B = [-77.945659273596831;.066789879899831;-.013224278036519];%Calculated electronic voltage offset 2016-08-29
%     B = [-77.945659273596831;.066789879899831;.023990157318235];%Calculated electronic voltage offset 2016-08-30
%     B = [-77.945659273596831;.066789879899831;.029484247255477];%Calculated electronic voltage offset 2016-08-31
%     B = [-77.945659273596831;.066789879899831;-.019796537975293];%Calculated electronic voltage offset 2016-09-01
%     B = [-77.945659273596831;.066789879899831;-.020051249091202];%Calculated electronic voltage offset 2016-09-02
%     B = [-77.945659273596831;.066789879899831;-.023556168385879];%Calculated electronic voltage offset 2016-09-05
%     B = [-77.945659273596831;.066789879899831;.01075378745015];%Calculated electronic voltage offset 2016-09-06
%     B = [-77.945659273596831;.066789879899831;.01341423074312];%Calculated electronic voltage offset 2016-09-07
%     B = [-77.945659273596831;.066789879899831;.011568539380078];%Calculated electronic voltage offset 2016-09-08
%     B = [-77.945659273596831;.066789879899831;.01688522827739];%Calculated electronic voltage offset 2016-09-09
%     B = [-77.945659273596831;.066789879899831;-.016829019720684];%Calculated electronic voltage offset 2016-09-13
%     B = [-77.945659273596831;.066789879899831;-.003643493415479];%Calculated electronic voltage offset 2016-09-14
%     B = [-77.945659273596831;.066789879899831;.003619371590765];%Calculated electronic voltage offset 2016-09-15
%     B = [-77.945659273596831;.066789879899831;-.008054809300239];%Calculated electronic voltage offset 2016-09-16
%     B = [-77.945659273596831;.066789879899831;.007746805630352];%Calculated electronic voltage offset 2016-09-17
%     B = [-77.945659273596831;.066789879899831;-.001349370436205];%Calculated electronic voltage offset 2016-09-19
%     B = [-77.945659273596831;.066789879899831;.013519479307415];%Calculated electronic voltage offset 2016-09-20
%     B = [-77.945659273596831;.066789879899831;.014697264201411];%Calculated electronic voltage offset 2016-09-21
%     B = [-77.945659273596831;.066789879899831;.019189266585133];%Calculated electronic voltage offset 2016-09-22
%     B = [-77.945659273596831;.066789879899831;-.00005138715614892488];%Calculated electronic voltage offset 2016-09-23
%     B = [-77.945659273596831;.066789879899831;-.035705100995331];%Calculated electronic voltage offset 2016-09-26
%     B = [-77.945659273596831;.066789879899831;-.023055373978155];%Calculated electronic voltage offset 2016-09-28
%      B = [-77.945659273596831;.066789879899831;.02189898938157];%Calculated electronic voltage offset 2016-09-30
%     B = [-77.945659273596831;.066789879899831;.017821157553907];%Calculated electronic voltage offset 2016-10-03
%     B = [-77.945659273596831;.066789879899831;-.021161497063274];%Calculated electronic voltage offset 2016-10-04
%     B = [-77.945659273596831;.066789879899831;-.030530063992805];%Calculated electronic voltage offset 2016-10-05
%    B = [-77.945659273596831;.066789879899831;-.015236129168148];%Calculated electronic voltage offset 2016-10-06
%     cal_set = [7.56195068359375 -.34210205078125 -3.5296630859375];
%     cal_set = [7.56195068359375 -.34210205078125 -1.85];%Settings for calibrations on 2016-05-14
%     cal_set = [7.56195068359375 -.34210205078125 -1.63];%Settings for calibrations on 2016-05-16
%     cal_set = [7.56195068359375 -.34210205078125 -1.35];%Settings for calibrations on 2016-05-17
%     cal_set = [7.5604248046875 -.34210205078125 -1.92];%Settings for calibrations on 2016-05-18 and 2016-05-19 until the error
%     cal_set = [-.54046630859375 3.5162353515625 -1.8499755859375];%2016-08-03
%     cal_set = [-.54046630859375 3.5162353515625 -1.7498779296875];%2016-08-04
%     cal_set = [-.54046630859375 3.5162353515625 -1.7498779296875];%2016-08-05 to 2016-08-09
%     cal_set = [-.54046630859375 3.5162353515625 -1.65008544921875];%2016-08-10
%     cal_set = [-.54046630859375 3.5162353515625 -1.49993896484375];%2016-08-12
%     cal_set = [-.54046630859375 3.5162353515625 -1.400146484375];%2016-08-16
%     cal_set = [-.54046630859375 3.5162353515625 -1.300048828125];%2016-08-17
%     cal_set = [-.29998779296875 3.44512939453125 -2.5];%2016-08-18
%     cal_set = [-.29998779296875 3.44512939453125 -4.80010986328125];%2016-08-30
%     cal_set = [-.29998779296875 3.44512939453125 -2.5];%2016-09-01
%     cal_set = [-.54046630859375 3.5162353515625 -.6500244140625];%2016-09-06
%     cal_set = [-.54046630859375 3.5162353515625 -.71990966796875];%2016-09-07
%     cal_set = [-.54046630859375 3.5162353515625 -.10009765625];%2016-09-13
%     cal_set = [-.54046630859375 3.5162353515625 -.48004150390625];%2016-09-14
%     cal_set = [-.29998779296875 3.44512939453125 -2.5];%2016-09-16
%     cal_set = [-.29998779296875 3.44512939453125 -3.64990234375];%2016-09-17
%     cal_set = [-.29998779296875 3.44512939453125 -4.15008544921875];%2016-09-19
%     cal_set = [-.29998779296875 3.44512939453125 -5];%2016-09-22
%     cal_set = [-.29998779296875 3.44512939453125 -3.900146484375];%2016-09-23
%     cal_set = [-.29998779296875 3.44512939453125 -2.30010986328125];%2016-09-26
%     cal_set = [-.29998779296875 3.44512939453125 -1.7999267578125];%2016-09-28
%     cal_set = [-.29998779296875 3.44512939453125 -1.49993896484375];%2016-09-30
%     cal_set = [-.29998779296875 3.44512939453125 -1.35009765625];%2016-10-03
%     cal_set = [-.57891845703125 3.52630615234375 0];%2016-10-04
%     cal_set = [-.3094 3.44512939453125 -1.49993896484375];%2016-11-16
%     cal_set = [-.5399 3.5159 -1.3];%2016-11-16
%     cal_set = [-.5399 3.5159 5]; %2016-11-17
%     cal_set = [-0.7 3.4451 0]; %2017-01-20
%     cal_set = [-0.7001 4.5999 2.0001]; %2017-03-27
%     cal_set = [-0.7599 4.5999 0.14]; %2017-03-27
%     cal_set = [-0.766 4.5999 0]; %2017-03-27
%    cal_set = [-0.748 4.5999 0.7]; %2017-03-29
%    cal_set = [-0.513 4.5999 7.9999]; %2017-05-01
% cal_set = [-0.7 3.6 4]; %2017-05-05
% cal_set = [-0.7 3.85 4]; %2017-11-07
% cal_set = [0.43 3.85 4]; %2018-01-05
% cal_set = [0.3 3.85 0]; %2018-03-15
% cal_set = [0.1 3.85 -6.2]; %2018-05-23
% cal_set = [-0.7 3.85 3.4]; %2019-01-14

%cal_set = [0.1 3.85 -6.2]; %2019-05-17
%cal_set = [-0.04 3.85 -9]; %2019-08-22 200 Bohr BEC
%cal_set = [-0.7, 3.85, -5.2];
%cal_set = [-0.7, 3.85, 4]; %2020-11-04 near Cs - |a> FR
%cal_set = [0.1, 3.85, -5.2]; %2020-11-06 near Cs-Cs 0 Bohr
%cal_set = [-0.7, 3.85, 6.25]; %2021-04-09 Cs- |a> FR
%cal_set = [-0.85, 3.85, 3.6]; %2021-06-23 Cs- Li|a> FR   After Current Carrying Screw Heating issue
%cal_set = [-0.85, 3.85, 3]; %temp_FRANK
% cal_set = [-0.85, 3.85, 7.5]; %2021-09-17 sympathetic cooling field
%cal_set = [-0.85, 3.85, 3.9]; 
cal_set = [-0.85, 3.85, 2.95]; %2024-05-25 start of Shim Jump




    A(1,1) = (revision-C(1)-(cal_set(2)+B(2))*A(1,2)-cal_set(3)*A(1,3))/(cal_set(1)+B(1));
    B = A*B+C;
%     if nargin>=2
%         shim = varargin{2}+3.588013;
%     else
%         shim = 0;
%     end
%     B = shim*0.366339;
    C = A(1,3);
end