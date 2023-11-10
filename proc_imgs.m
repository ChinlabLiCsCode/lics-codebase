function nd = proc_imgs(shots, params, dfinfo, bginfo)

           

debug = params.debug;

%% enable user to pass bginfo and dfinfo in params
if nargin < 4
    bginfo = params.bginfo;
end
if nargin < 3
    dfinfo = params.dfinfo;
end

%% figure out how the user supplied bginfo.
if debug
    disp('loading bg');
end
% bgcase tells us about the method
% bg is the actual background we will subtract
if ischar(bginfo)
    switch bginfo
        case 'none'
            % Case 1: "none" - Do no bg subtraction (V images).
            bgcase = 1;
        case 'self'
            % Case 2: "self" - Use the background frame (H images).
            bgcase = 2;
        otherwise
            error('Invalid bginfo input');
    end
elseif isnumeric(bginfo) || iscell(bginfo)
    % Case 3: array of shots, assuming today, or cell with date and shots
    bgcase = 3;
    bg = mean(load_img(bginfo, params), 1);
else
    error('Invalid bginfo input');
end

%% figure out how the user supplied dfinfo.
if debug
    disp('loading df');
end
% dfcase tells us about the method
% L is the light frames 
if ischar(dfinfo)
    switch dfinfo
        case 'none'
            % Case 1: "none" - Do no defringing.
            dfcase = 1;
        case 'self'
            % Case 2: "self" - Defringe using only images from dataset.
            dfcase = 2;
        otherwise
            error('Invalid dfinfo input');
    end
elseif isnumeric(dfinfo) || iscell(dfinfo)
    % Case 3: array of shots, assuming today, or cell with date and shots
    dfcase = 3;
    dfload = load_img(dfinfo, params);
    switch bgcase
        case 1 
            Lload = dfload(:, :, :, 2);
            Aload = dfload(:, :, :, 1);
        case 2
            Lload = dfload(:, :, :, 2) - dfload(:, :, :, 3);
            Aload = dfload(:, :, :, 1) - dfload(:, :, :, 3);
        case 3
            Lload = dfload(:, :, :, 2) - bg(:, :, :, 2);
            Aload = dfload(:, :, :, 1) - bg(:, :, :, 1);
    end
else
    error('Invalid dfinfo input');
end


%% load images 
if debug
    disp('loading imgs');
end

raw = load_img(shots, params);

A = raw(:, :, :, 1); 
L = raw(:, :, :, 2);

if bgcase == 2
    A = A - raw(:, :, :, 3);
    L = L - raw(:, :, :, 3);
elseif bgcase == 3
    A = A - bg(:, :, :, 1);
    L = L - bg(:, :, :, 2);
end

if debug
    imgstack_viewer(A, 'A (ebg subtracted)');
    imgstack_viewer(L, 'L (ebg subtracted)');
end


%% perform defringing and od calculation

if dfcase == 3
    L = cat(1, Lload, L);
end

if debug
    disp('dfobj_create');
end
% dfobj = dfobj_create(L, params.mask, params.pcanum);
dfobj = cvpcreatedefringeset(L, params.mask, params.pcanum);
if debug
    disp('dfobj_apply');
end
% Aprime = dfobj_apply(A, dfobj);
Aprime = A;
for a = 1:size(A, 1)
    Aprime(a, :, :) = cvpdefringe(A(a, :, :), dfobj);
end
if debug
    disp('nd calc');
end
nd = nd_calc(A, Aprime, params);

if debug
    imgstack_viewer(Aprime, 'Aprime');
    imgstack_viewer(nd, 'ND');
end

if debug
    disp('reshaping');
end
if ndims(shots) > 1
    szA = size(nd);
    if iscell(shots)
        szB = size(shots{2});
    else
        szB = size(shots);
    end
    nd = reshape(nd, [szB(1), szB(2), szA(2), szA(3)]);
end


end

