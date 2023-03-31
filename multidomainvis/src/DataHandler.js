import * as THREE from 'three';

import {Lut} from '../libs/Lut.js';
import {drawParticles, createColorbar} from './draw.js'

class DataHandler {
    constructor(scene) {
        this.scene = scene;
    }


    onBuildingOptionDataLoaded(geometry, cityOrigin, dataSet) {
        const origin = new THREE.Vector3(cityOrigin.x, 0, cityOrigin.y);
        geometry.rotateX(-Math.PI / 2);
        geometry.scale(1,1,-1);
        geometry.translate(-origin.x, -origin.y, -origin.z);
        geometry.scale(1,1,-1);
        const material = new THREE.MeshStandardMaterial({color: 0xAAAAAA, transparent: true, opacity: 0.8, flatShading: true});
        const mesh = new THREE.Mesh(geometry, material);
        //mesh.castShadow = true;
        //mesh.receiveShadow = true;

        mesh.visible = false;
        this.scene.add(mesh);
        dataSet.objects.set('buildingOption', mesh);
    }

    onRadiationDataLoaded(data, cityOrigin, dataSet) {
        const positions = [];
        const colors = [];
        const lut = new Lut("blackbody", 32);

        const values = [];
        for (let d of data) {
            const value = d['value'];

            if (value === undefined) {
                console.log(d);
                continue;
            }

            positions.push(
                d["x"], // - 24.850166 , // Magic grid offset number
                51.3,
                - (d["y"]), // - 32.03199), // Magic grid offset number
            );

            values.push(value);
            lut.minV = Math.min(lut.minV, value);
            lut.maxV = Math.max(lut.maxV, value);
        }
        for (let v of values) {
            const color = lut.getColor(v);
            colors.push(color.r, color.g, color.b);
        }

        const particles = drawParticles(positions, colors, 15, true);
        dataSet.objects.set('radiation', particles);

        const title = dataSet.name === "Option 0" ? "Radiation, base case (kWh/m<sup>2</sup>)" : "Radiation, difference from base case (kWh/m<sup>2</sup>)"
        const colorbar = createColorbar(lut, title);
        document.getElementById("legendContainer").append(colorbar);
        dataSet.legends.set('radiation', colorbar);

        this.scene.add(particles);
        particles.visible = false;
    }

    onWindDataLoaded(cellData, nodeData, cityOrigin, dataSet) {
        // Initialise the arrays beforehand for efficiency
        // Each cell triangle has three vertices (nodes), with
        // three positional values, hence 9.
        const positions = new Float32Array(cellData.length * 9);
        const normals = new Float32Array(cellData.length * 9);
        const colors = new Float32Array(cellData.length * 9);

        const columns = ['node 1', 'node 2', 'node 3'];

        const colorMap = [
            0x0000FF, // A | Frequent sitting
            0x00AAFF, // B | Occasional Sitting
            0xAAFFFF, // C | Standing
            0x55FF00, // D | Walking
            0xFFFF00, // E | Unfomfortable
            0xFF5500  // S | Unsafe
        ].map(v=>new THREE.Color(v));

        let value, color, nodeID, node;
        for (let i=0; i<cellData.length; i++) {
            value = cellData[i]['Lawson LDDC'];

            if (value === undefined) {
                console.warn("Why undefined?");
                continue;
            }

            color = colorMap[value];

            for (let j=0; j<3; j++) {
                nodeID = columns[j];
                node = nodeData[cellData[i][nodeID]];
                positions[i*9 + j*3] = node.x - cityOrigin.x;
                positions[i*9 + j*3 + 1] = node.z;
                positions[i*9 + j*3 + 2] = - (node.y - cityOrigin.y);

                normals[i*9 + j*3 + 1] = 1; // Y is up

                colors[i*9 + j*3] = color.r;
                colors[i*9 + j*3 + 1] = color.g;
                colors[i*9 + j*3 + 2] = color.b;
            }
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        const material = new THREE.MeshStandardMaterial({
            //side: THREE.DoubleSide,
            color: 0xF5F5F5,
            vertexColors: true
        });
        const mesh = new THREE.Mesh(geometry, material);

        const colorbar = document.createElement('img');
        colorbar.classList.add('legend');
        colorbar.style.padding = '5px';
        colorbar.src = "data/wind/surfaceLawson_option_0.png";
        document.getElementById("legendContainer").append(colorbar);

        mesh.visible = false;
        this.scene.add(mesh);

        dataSet.objects.set('wind', mesh);
        dataSet.legends.set('wind', colorbar);
    }

    onNoiseDataLoaded(data, cityOrigin, dataSet) {
        const positions = [];
        const colors = [];
        const lut = new Lut("rainbow", 32);

        const noiseVals = [];
        for (let d of data) {
            let [x, y, noiseVal] = d;
            if (isNaN(noiseVal)) {
                continue;
            }
            positions.push(
                x - cityOrigin.x,
                59.7,
                - (y - cityOrigin.y)
            );
            noiseVals.push(noiseVal);
        }
        lut.minV = Math.min(...noiseVals);
        lut.maxV = Math.max(...noiseVals);

        for (let v of noiseVals) {
            const color = lut.getColor(v);
            colors.push(color.r, color.g, color.b);
        }

        const particles = drawParticles(positions, colors, 4);
        particles.visible = false;
        this.scene.add(particles);

        const colorbar = createColorbar(lut, "Noise (dB)");
        document.getElementById("legendContainer").append(colorbar);

        dataSet.legends.set('noise', colorbar);
        dataSet.objects.set('noise', particles);
    }

    onCityDataLoaded(loadedData, energyMap, dataSet) {
        const lut = new Lut('rainbow', 32);
        for (let building of energyMap.values()) {
            lut.minV = Math.min(lut.minV, building.Total);
            lut.maxV = Math.max(lut.maxV, building.Total);
        }

        const buildings = loadedData.Buildings;

        const buildingGroup = new THREE.Group();

        for (let building of buildings) {
            const points = building.Footprint.map(p => new THREE.Vector2(p.x, p.y));
            const shape = new THREE.Shape(points);
            const geometry = new THREE.ExtrudeGeometry(shape, {
                steps: 1,
                depth: building.Height,
                bevelEnabled: false
            });

            let color = 0xffffff;
            if (energyMap.has(building.UUID)) {
                color = lut.getColor(energyMap.get(building.UUID).Total)
            }
            const material = new THREE.MeshStandardMaterial({color});
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.z = building.GroundHeight;
            buildingGroup.add(mesh);
        }
        buildingGroup.rotateX(-Math.PI / 2);
        buildingGroup.visible = false;
        this.scene.add(buildingGroup);

        dataSet.objects.set('energy', buildingGroup);

        if (energyMap.size > 0) {
            const colorbar = createColorbar(lut, "Energy (kWh/m<sup>2</sup>)");
            document.getElementById("legendContainer").append(colorbar);
            dataSet.legends.set('energy', colorbar);
        }

        return loadedData.Origin;
    }

}

export {DataHandler}