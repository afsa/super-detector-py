function saveMesh(model, geometry, input_edge, output_edge,...
    voltage_start, voltage_end, file_path)
%saveMesh Save the generated mesh to a HDF5 file for use in other programs.
%   model is the object created from createpde
%   geometry is the geometry object used to create the model
%   input_edge is the edge number for the input current
%   output_edge is the edge number for the output current
%   voltage_start is the point where the voltage mesaurement starts
%   voltage_end is the point where the voltage measurement ends
%   file_path is the path to the HDF5 file

% Add the output directory if it does not exist.
[parent_path] = fileparts(file_path);
if ~exist(parent_path, 'dir')
    mkdir(parent_path);
end

% Check that the file does not already exist.
if exist(file_path, 'file')
    error('The file already exists.');
end

% Extract the geometry data.
input_data = geometry(:, input_edge);
output_data = geometry(:, output_edge);

if input_data(1) ~= 2
    throw(MException('Input edge must be flat.'))
end

if output_data(1) ~= 2
    throw(MException('Output edge must be flat.'))
end

% Extract mesh data.
% Convert from 1-indexed (as is used in Matlab) to 0-indexed (as is used in
% Python).
x = model.Mesh.Nodes(1, :);
y = model.Mesh.Nodes(2, :);
elements = model.Mesh.Elements - 1;

% Compute the voltage start and end points
voltage_start_index = findNodes(model.Mesh, 'Nearest',...
    transpose(voltage_start)) - 1;
voltage_end_index = findNodes(model.Mesh, 'Nearest',...
    transpose(voltage_end)) - 1;

% Save to HDF5.
h5create(file_path, '/x', size(x));
h5write(file_path, '/x', x);

h5create(file_path, '/y', size(y));
h5write(file_path, '/y', y);

h5create(file_path, '/elements', size(elements), 'Datatype', 'uint64');
h5write(file_path, '/elements', uint64(elements));

h5create(file_path, '/input_edge', 4);
h5write(file_path, '/input_edge', input_data(2:5));
h5writeatt(file_path,'/input_edge','format', ...
    'Formatted as [start x, end x, start y, end y]');

h5create(file_path, '/output_edge', 4);
h5write(file_path, '/output_edge', output_data(2:5));
h5writeatt(file_path,'/output_edge','format', ...
    'Formatted as [start x, end x, start y, end y]');

h5create(file_path, '/voltage_points', 2, 'Datatype', 'uint64');
h5write(file_path, '/voltage_points', ...
    uint64([voltage_start_index, voltage_end_index]));
h5writeatt(file_path,'/voltage_points','format', ...
    'Formatted as [index of start, index of end]');

end

