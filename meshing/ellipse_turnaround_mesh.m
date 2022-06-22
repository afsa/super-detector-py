%% General settings

% Define the geometry scale. This option allows for quickly rescaling the
% geometry. This geometry is defined such that scale = 1 corresponds to a
% leg width of one coherence length.
scale = 14;

% Define the output directory and the output file name.
% The output directory is created if it does not exist.
outputDir = '../mesh';
fileName = sprintf('ellipse_%d.h5', scale);

%% Generate geometry
model = createpde;

% Define the lower leg rectangle.
R1 = makePolygon([
    5,  0.5;
    0,  0.5;
    0, -0.5;
    5, -0.5
], scale);

% Define the turnaround head rectangle.
R2 = makePolygon([
    8.5,  2.5;
    5,    2.5;
    5,   -0.5;
    8.5, -0.5
], scale);

% Define the upper leg rectangle.
R3 = makePolygon([
    5, 2.5;
    0, 2.5;
    0, 1.5;
    5, 1.5
], scale);

% Define the inner ellipse.
E1 = makeEllipse([5 1], 1.0, 0.5, scale);

% Merge the geometry objects into one geometry.
%
% The first argument is a set formula used to join the geometries. Plus,
% star, and minus is used for the operator union, intersection, and 
% difference, respectively.
% See https://se.mathworks.com/help/pde/ug/decsg.html#bu_fft3-sf for more
% information.
%
% The second argument defines the sets used in the set formula.
%
% The remaining arguments are the values of the sets.
g = makeGeometry('R1+(R2-E1)+R3', char('R1', 'R2', 'R3', 'E1'),...
    R1, R2, R3, E1);

% Plot the geometry.
geometryFromEdges(model, g);
clf()
pdegplot(model, 'EdgeLabels','on')

%% Geometry settings

% Define the input and output edges for the current flowing through the
% superconductor. The edge labels are found by running the section 
% "Generate geometry".
%
% NOTE: The length of the input and output edges need to have the same
% length. The code has not been tested with non-vertical input and output
% edges.
inputEdge = 8;
outputEdge = 9;

% Define the probe points to measure voltage between.
%
% NOTE: The probe points should not be too close to the input and output
% edges as the superconductor is suppressed close to these edges. If a too 
% small buffer region is used, then the voltage is non-zero in the 
% superconducting state.
voltageStart = [1, 0] * scale;
voltageEnd = [1, 2] * scale;

clf()
pdegplot(model, 'EdgeLabels','on')
hold on
plot(voltageStart(1), voltageStart(2), 'o')
plot(voltageEnd(1), voltageEnd(2), 'o')


%% Generate mesh

% Generate a mesh with max link size of 0.5 and minimal size of sqrt(0.1).
% The minimal link size limits the largest possible time step possible to
% use. This choise works well with a time step 0.01, when gamma = 10 and 
% u = 5.79.
generateMesh(model,'Hmax', 0.5, 'Hmin', sqrt(0.1),...
    'GeometricOrder', 'linear');
pdeplot(model)

%% Save mesh

filePath = fullfile(outputDir, fileName);
saveMesh(model, g, inputEdge, outputEdge, voltageStart, ...
voltageEnd, filePath);