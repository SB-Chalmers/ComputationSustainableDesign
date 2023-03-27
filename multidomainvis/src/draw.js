import * as THREE from 'three';

function drawParticles(positions, colors, size=10, sizeAttenuation = true, texturePath = 'resources/circle.png') {
    const loader = new THREE.TextureLoader();
    const texture = loader.load(texturePath);

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geometry.computeBoundingSphere();

    const material = new THREE.PointsMaterial({
        size: size,
        vertexColors: true,
        map: texture,
        sizeAttenuation: sizeAttenuation,
        alphaTest: 0.5
    });

    return new THREE.Points(geometry, material);
}

function drawInstances(geometry, elements) {
    const count = elements.length;
    const material = new THREE.MeshNormalMaterial();
    const mesh = new THREE.InstancedMesh(geometry, material, count);
    const matrix = new THREE.Matrix4();
    for (let i=0; i < count; i++) {
        matrix.compose(
            elements[i].position,
            elements[i].quaternion,
            elements[i].scale
        );
        mesh.setMatrixAt(i, matrix);
        mesh.setColorAt(i, elements[i].color);
    }
    return mesh;
}

function createColorbar(lut, title, height = 300, nVals = 6) {
    const contentwrapper = document.createElement("div");
    contentwrapper.classList.add("legend");
    const legend = document.createElement("div");
    legend.style.display = "flex";
    legend.style.position = "relative";
    legend.style.textAlign = "center";
    const values = document.createElement("div");
    values.style.height = `${height}px`;
    const dv = (lut.maxV - lut.minV) / (nVals-1);
    for (let i=0; i<nVals; i++) {
        const row = document.createElement('td');
        row.style.position = "absolute";
        row.style.top = `${i/(nVals-1) * height}px`;
        row.style.translate = "0px -50%"
        row.style.left = "40px";
        row.innerHTML = (lut.maxV - i * dv).toPrecision(3);
        values.append(row);
    }
    values.style.padding = "10px 0px 0px 10px";
    legend.append(values);
    const colorbar = lut.createCanvas();
    colorbar.style.width = "30px";
    colorbar.style.height = `${height}px`;
    colorbar.style.right = 0;
    legend.append(colorbar);

    const legendTitle = document.createElement("p");
    legendTitle.innerHTML = title;
    contentwrapper.append(legendTitle);
    contentwrapper.append(legend);
    return contentwrapper;
}

export {drawParticles, drawInstances, createColorbar};
