
clear;
close all;
clc;
day = [2023 10 02];
build_params;

params = paramsCV_IS;

bginfo = struct('date', [2023 09 29], 'shots', 5:64);
dfinfo = struct('date', [2023 09 29], 'shots', 98:199);
shots = struct('date', [2023 09 29], 'shots', 198:217);

% proc_scan(shots, paramsCV_IS, shots.shots, dfinfo, bginfo, 'test', 'shot')
% 
% 
%% figure out how the user supplied bginfo.

% bgcase tells us about the method
% bg is the actual background we will subtract



bgcase = 3;
bg = mean(load_img(bginfo, params), 1);



%% figure out how the user supplied dfinfo.

% dfcase tells us about the method
% L is the actual light frames we will use

% if ischar(dfinfo)
%     switch dfinfo
%         case 'none'
%             % Case 1: "none" - Do no defringeing.
%             dfcase = 1;
%         case 'self'
%             % Case 2: "self" - Use just the light images from the 
%             dfcase = 2;
%         otherwise
%             error('Invalid dfinfo input');
%     end
% elseif isnumeric(dfinfo) && size(dfinfo, 1) == 1
%     % Case 3: 1D array of shots - Use a 1D array of shots data.
%     dfcase = 3;
%     L = load_img(dfinfo, params);
%     L = L(:, :, :, 2);
% elseif isstruct(dfinfo) && isfield(dfinfo, 'shots') && isfield(dfinfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
dfcase = 3;
L = load_img(dfinfo, params);
L = L(:, :, :, 2);
% else
%     error('Invalid dfinfo input');
% end



%% load images 

% load shots
raw = load_img(shots, params);

A = raw(:, :, :, 1); % atom frames

% add shots to light stack
% switch dfcase
%     case 2 % self
%         L = raw(:, :, :, 2); % light frames
%     case 3 % self + extra 
%         L = cat(1, raw(:, :, :, 2), L);
% end

% add shots to background stack
if bgcase == 2 % use background frames from the images 
    bg = mean(raw(:, :, :, :), 1); % background frames
end

% get lengths 
n = size(A, 1); % atom set length
m = size(L, 1); % light set length


%% pick out correct bg frames from bg stack

if params.cam == 'H'
    Abg = bg(:, :, :, 3);
    Lbg = Abg;
else
    Abg = bg(:, :, :, 1);
    Lbg = bg(:, :, :, 2);
end


%% subtract electronic background

% atom set 
A = A - Abg;

% light set 
L = L - Lbg;


%% calculate mean light image and subtract from light and atom images

Lavg = mean(L, 1);

% atom set 
dA = A - Lavg;

% light set 
dL = L - Lavg;


%% perform defringing

dfobj = dfobj_create(dL, params.mask, params.pcanum);
dAprime = dfobj_apply(dA, dfobj);

figure();
imagesc(imtile(A));
axis image;
colorbar();

Aprime = dAprime + Lavg;


%% calculate OD 

imgs = od_calc(A, Aprime, params);

figure()
imagesc(squeeze(imgs(1, :, :))')
axis image;
colorbar;