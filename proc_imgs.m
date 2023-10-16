function od = proc_imgs(shots, params, dfinfo, bginfo)

           

debug = params.debug;

%% enable user to pass bginfo and dfinfo in params
if nargin < 4
    bginfo = params.bginfo;
end
if nargin < 3
    dfinfo = params.dfinfo;
end

%% figure out how the user supplied bginfo.
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
    bg = mean(load_img(bginfo, params), 3);
else
    error('Invalid bginfo input');
end

%% figure out how the user supplied dfinfo.
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


if strcmp(params.dfmethod, 'norm')

    if dfcase == 3
        L = cat(3, Lload, L);
    end
    
    dfobj = dfobj_create(L, params.mask, params.pcanum);
    Aprime = dfobj_apply(A, dfobj);
    od = od_calc(A, Aprime, params);
    
    if debug
        imgstack_viewer(dfobj.eigvecims, 'dfobj.eigvecims');
        imgstack_viewer(Aprime, 'Aprime');
        imgstack_viewer(od, 'OD');
    end

% elseif strcmp(params.dfmethod, 'odnorm')
% 
%     dfod = od_calc(Aload, Lload, params);
%     dfobj = dfobj_create(dfod, params.mask, params.pcanum);
%     odraw = od_calc(A, L, params);
%     od = odraw - dfobj_apply(odraw, dfobj);
% 
%     if debug
%         imgstack_viewer(dfobj.eigvecims, 'dfobj.eigvecims');
%         imgstack_viewer(dfod, 'dfod');
%         imgstack_viewer(odraw, 'odraw');
%         imgstack_viewer(od, 'OD');
%     end
% 
% elseif strcmp(params.dfmethod, 'cvp')
% 
%     dfod = od_calc(Aload, Lload, params);
%     dfodavg = mean(dfod, 3);
%     ddfod = dfod - dfodavg;
%     dfobj = dfobj_create(ddfod, params.mask, params.pcanum);
%     odraw = od_calc(A, L, params);
%     dodraw = odraw - dfodavg;
%     dodrawprime = dfobj_apply(dodraw, dfobj);
%     od = odraw - dodrawprime;
% 
%     if debug
%         imgstack_viewer(dfobj.eigvecims, 'dfobj.eigvecims');
%         imgstack_viewer(dfod, 'dfod');
%         imgstack_viewer(dfodavg, 'dfodavg');
%         imgstack_viewer(ddfod, 'ddfod');
%         imgstack_viewer(odraw, 'odraw');
%         imgstack_viewer(dodraw, 'dodraw');
%         imgstack_viewer(dodrawprime, 'dodrawprime');
%         imgstack_viewer(od, 'OD');
%     end

else 
    error('invalid params.dfmethod');
end




