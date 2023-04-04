onmessage = function(e) {
    const [cellData, nodeData, cityOrigin] = e.data;
    // Initialise the arrays beforehand for efficiency
    // Each cell triangle has three vertices (nodes), with
    // three positional values, hence 9.
    const positions = new Float32Array(nodeData.length * 3);
    const normals = new Float32Array(nodeData.length * 3);
    const colors = new Array(nodeData.length);
    const indices = new Array(cellData.length * 3);

    const columns = ['node 1', 'node 2', 'node 3'];

    const colorMap = [
        0x0000FF, // A | Frequent sitting
        0x00AAFF, // B | Occasional Sitting
        0xAAFFFF, // C | Standing
        0x55FF00, // D | Walking
        0xFFFF00, // E | Unfomfortable
        0xFF5500  // S | Unsafe
    ];

    let node;
    for (let i=0; i<nodeData.length; i++) {
        node = nodeData[i];
        for (let j=0; j<3; j++) {
            positions[i*3 + j*3] = node.x - cityOrigin.x;
            positions[i*3 + j*3 + 1] = node.z;
            positions[i*3 + j*3 + 2] = - (node.y - cityOrigin.y);

            normals[i*3 + j*3 + 1] = 1; // Y is up
        }
    }

    let value, nodeID;
    for (let i=0; i<cellData.length; i++) {
        value = cellData[i]['Lawson LDDC'];

        for (let j=0; j<3; j++) {
            nodeID = cellData[i][columns[j]];
            colors[nodeID] = colorMap[value];
            indices[i*3 + j] = nodeID;
        }
    }
    postMessage({positions, normals, colors, indices});
}
